from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition
from PyQt6.QtWidgets import QApplication
from gui.preferences import PreferencesInterface
from qfluentwidgets import MessageBox

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.preferencesInterface = PreferencesInterface(self)

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.preferencesInterface, FluentIcon.CHECKBOX, 'Preferences', pos)

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