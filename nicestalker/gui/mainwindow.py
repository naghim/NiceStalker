from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from nicestalker.gui.preferences import PreferencesInterface
from nicestalker.gui.status import StatusInterface
from qfluentwidgets import MessageBox
import os

class MainWindow(FluentWindow):

    def __init__(self, main):
        super().__init__()
        self.main = main

        self.preferencesInterface = PreferencesInterface(self.main, self)

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.preferencesInterface, FluentIcon.CHECKBOX, 'Preferences', pos)

        icon = QIcon()

        if os.path.exists('resources/nightstalker.png'):
            icon.addFile('resources/nightstalker.png')
        else:
            icon.addFile('nicestalker/resources/nightstalker.png')

        self.setWindowIcon(icon)
        self.setWindowTitle('Nice Stalker Configurator')
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()

    def closeEvent(self, event):
        if not self.preferencesInterface.saveButton.isEnabled():
            event.accept()
            return
        
        w = MessageBox('Save changes?', 'Do you want to save your changes?', self)
        w.yesButton.setText('Save')
        w.cancelButton.setText('No')

        if w.exec():
            self.preferencesInterface.save()

        event.accept()
