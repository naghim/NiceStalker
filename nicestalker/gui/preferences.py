from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from nicestalker.gui.stylesheet import StyleSheet

from qfluentwidgets import (ScrollArea, PushButton, FluentIcon,
                            TitleLabel, SubtitleLabel, BodyLabel, CheckBox, LineEdit, FlowLayout, StateToolTip, MessageBox)
import json
import os
import psutil

class DynamicEntry(PushButton):

    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.setText(text)
        self.setIcon(FluentIcon.REMOVE)

class DynamicList(QWidget):

    def __init__(self, preferencesChanged, placeholder, parent=None):
        super().__init__(parent=parent)
        self.preferencesChanged = preferencesChanged
        self.setContentsMargins(0, 0, 0, 0)
        self.rowsToShow = 1

        self.vBoxLayout = QVBoxLayout(self)
        self.lineEditWidget = QWidget()
        self.lineEditWidget.setContentsMargins(0, 0, 0, 0)
        self.lineEditLayout = QHBoxLayout(self.lineEditWidget)
        self.lineEditLayout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText(placeholder)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.returnPressed.connect(self.on_add)
        self.lineEdit.textChanged.connect(self.on_text_changed)
        self.addButton = PushButton('Add')
        self.addButton.setIcon(FluentIcon.ADD)
        self.addButton.clicked.connect(self.on_add)
        self.addButton.setEnabled(False)
        self.clearAllButton = PushButton('Remove All')
        self.clearAllButton.setIcon(FluentIcon.REMOVE_FROM)
        self.clearAllButton.clicked.connect(self.on_clear)
        self.flowScrollWidget = ScrollArea()
        self.flowScrollWidget.setFixedHeight(self.rowsToShow * 45)
        self.flowScrollWidget.setWidgetResizable(True)
        self.flowWidget = QWidget()
        self.flowWidget.setObjectName('flowWidget')
        self.flowLayout = FlowLayout(self.flowWidget)

        self.flowScrollWidget.setWidget(self.flowWidget)

        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setVerticalSpacing(20)
        self.flowLayout.setHorizontalSpacing(10)

        self.lineEditLayout.addWidget(self.lineEdit)
        self.lineEditLayout.addWidget(self.addButton)
        self.lineEditLayout.addWidget(self.clearAllButton)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.lineEditWidget)
        self.vBoxLayout.addWidget(self.flowScrollWidget)

        self.data = []

    def on_text_changed(self):
        text = self.lineEdit.text()
        self.addButton.setEnabled(bool(text) and text not in self.data)

    def on_add(self):
        text = self.lineEdit.text()

        if not text:
            return
        
        if text in self.data:
            return
        
        self.__add_entry(text)
        self.flowLayout.update()

        self.data.append(text)
        self.lineEdit.clear()

        if self.preferencesChanged:
            self.preferencesChanged()

    def on_remove(self, entry: DynamicEntry, text):
        if text not in self.data:
            return
    
        self.data.remove(text)
        self.flowLayout.removeWidget(entry)
        self.flowLayout.update()
        entry.deleteLater()

        if self.preferencesChanged:
            self.preferencesChanged()
    
    def on_clear(self):
        self.flowLayout.takeAllWidgets()
        self.flowLayout.update()
        self.data = []

        if self.preferencesChanged:
            self.preferencesChanged()

    def __add_entry(self, text):
        entry = DynamicEntry(text)
        entry.clicked.connect(lambda: self.on_remove(entry, text))
        self.flowLayout.addWidget(entry)

    def load_from_list(self, l):
        for entry in l:
            self.__add_entry(entry)

        self.flowLayout.update()
        self.data.extend(l)

class PreferencesInterface(ScrollArea):
    
    def __init__(self, main, parent=None):
        super().__init__(parent=parent)
        self.main = main
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)

        self.view.setObjectName('view')
        self.setObjectName('PreferencesInterface')

        self.titleWidget = QWidget()
        self.titleWidgetLayout = QHBoxLayout(self.titleWidget)
        self.titleWidgetLayout.setContentsMargins(0, 0, 0, 0)

        self.title = TitleLabel('Preferences')
        self.saveButton = PushButton('Save')
        self.saveButton.setIcon(FluentIcon.SAVE)
        self.saveButton.setEnabled(False)
        self.saveButton.clicked.connect(self.save)

        self.titleWidgetLayout.addWidget(self.title)
        self.titleWidgetLayout.addStretch()
        self.titleWidgetLayout.addWidget(self.saveButton)
        self.filtersSubtitle = SubtitleLabel('Filters')
        self.appSubtitle = SubtitleLabel('Application')
        self.peopleToWatchCaption = BodyLabel('People to monitor:')
        self.peopleToWatchList = DynamicList(self.preferences_changed, 'Name or Discord ID')
        self.peopleToIgnoreCaption = BodyLabel('People to ignore:')
        self.peopleToIgnoreList = DynamicList(self.preferences_changed, 'Name or Discord ID')
        self.runOnStartup = CheckBox('Run on startup')
        self.runOnStartup.stateChanged.connect(self.preferences_changed)

        self.startButton = PushButton('Start')
        self.startButton.setIcon(FluentIcon.BROOM)
        self.startButton.setEnabled(True)
        self.startButton.clicked.connect(self.start_app)

        self.app_running = self.is_app_running()
        self.update_start_button()

        self.vBoxLayout.addWidget(self.titleWidget)
        self.vBoxLayout.addWidget(self.filtersSubtitle)
        self.vBoxLayout.addWidget(self.peopleToWatchCaption)
        self.vBoxLayout.addWidget(self.peopleToWatchList)
        self.vBoxLayout.addWidget(self.peopleToIgnoreCaption)
        self.vBoxLayout.addWidget(self.peopleToIgnoreList)
        self.vBoxLayout.addWidget(self.appSubtitle)
        self.vBoxLayout.addWidget(self.runOnStartup)
        self.vBoxLayout.addWidget(self.startButton)

        StyleSheet().apply(self)
        self.load()

    def get_other_apps(self):
        current_pid = os.getpid()

        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] == 'NiceStalker.exe' and proc.info['pid'] != current_pid:
                yield proc

    def is_app_running(self):
        for _ in self.get_other_apps():
            return True

        return False
    
    def update_start_button(self):
        if self.app_running:
            self.startButton.setText('Stop')
        else:
            self.startButton.setText('Start')

    def preferences_changed(self):
        self.saveButton.setEnabled(True)
    
    def load_config(self):
        self.main.load_config()
        self.peopleToWatchList.load_from_list(self.main.ppl_to_stalk)
        self.peopleToIgnoreList.load_from_list(self.main.ppl_to_ignore)
        self.runOnStartup.setChecked(self.main.run_on_startup)
        self.saveButton.setEnabled(False)

    def save_config(self):
        self.main.ppl_to_stalk = self.peopleToWatchList.data
        self.main.ppl_to_ignore = self.peopleToIgnoreList.data
        self.main.run_on_startup = self.runOnStartup.isChecked()
        self.main.save_config()

    def load(self):
        try:
            self.load_config()
        except:
            w = MessageBox('Error!', 'Could not load the config file.', self)
            w.cancelButton.hide()
            w.exec()

    def save(self): 
        if self.main.run_on_startup != self.runOnStartup.isChecked():
            should_run_on_startup = self.runOnStartup.isChecked()

            if should_run_on_startup:
                self.main.add_to_startup()
            else:
                self.main.remove_from_startup()

        try:
            self.save_config()
        except:
            w = MessageBox('Error!', 'Could not save the config file.', self)
            w.cancelButton.hide()
            w.exec()
            return

        self.saveButton.setEnabled(False)
        self.stateTooltip = StateToolTip('Saved!', 'Your preferences have been saved!', self.window())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        self.stateTooltip.setState(True)

    def start_app(self):
        if self.saveButton.isEnabled():
            self.saveButton.setEnabled(False)
            w = MessageBox('Warning!', 'You have unsaved changes. Would you like to save them?', self)
            w.cancelButton.clicked.connect(self.start_app_without_save)
            w.yesButton.clicked.connect(self.save_and_start_app)
            w.exec()
            return
    
        self.start_app_without_save()

    def save_and_start_app(self):
        self.save()
        self.start_app_without_save()

    def start_app_without_save(self):
        if self.app_running:
            for proc in self.get_other_apps():
                proc.kill()
        else:
            self.main.start_notifier()