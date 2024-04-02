
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from .mainwindow import MainWindow
import sys

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

# create main window
w = MainWindow()

app.exec()