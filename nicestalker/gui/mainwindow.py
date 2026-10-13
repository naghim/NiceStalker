from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition, setTheme, Theme, MessageBox

from nicestalker import paths
from nicestalker.gui.preferences import PreferencesInterface


class MainWindow(FluentWindow):

    def __init__(self, main):
        super().__init__()
        self.main = main
        setTheme(Theme.AUTO)

        self.preferencesInterface = PreferencesInterface(self.main, self)

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.preferencesInterface, FluentIcon.CHECKBOX, 'Preferences', pos)

        self.setWindowIcon(QIcon(paths.resource_path('nightstalker.png')))
        self.setWindowTitle('Nice Stalker Configurator')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def closeEvent(self, event):
        if self.preferencesInterface.saveButton.isEnabled():
            w = MessageBox('Save changes?', 'Do you want to save your changes?', self)
            w.yesButton.setText('Save')
            w.cancelButton.setText('No')
            if w.exec():
                self.preferencesInterface.save()

        if self.main.quitting or not self.main.tray.available:
            event.accept()
            if not self.main.tray.available:
                self.main.quit()
            return

        event.ignore()
        self.hide()
        self.main.tray.notify_hidden()
