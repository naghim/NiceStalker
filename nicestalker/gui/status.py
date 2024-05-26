from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from nicestalker.gui.stylesheet import StyleSheet

from qfluentwidgets import (ScrollArea, PushButton, FluentIcon,
                            TitleLabel)

class StatusInterface(ScrollArea):
    
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
        self.setObjectName('StatusInterface')

        self.titleWidget = QWidget()
        self.titleWidgetLayout = QHBoxLayout(self.titleWidget)
        self.titleWidgetLayout.setContentsMargins(0, 0, 0, 0)

        self.title = TitleLabel('Status')
        self.startButton = PushButton('Start')
        self.startButton.setIcon(FluentIcon.BROOM)
        self.startButton.setEnabled(True)
        self.startButton.clicked.connect(self.start)

        self.titleWidgetLayout.addWidget(self.title)
        self.titleWidgetLayout.addStretch()
        self.titleWidgetLayout.addWidget(self.startButton)
    
        self.vBoxLayout.addWidget(self.titleWidget)

        StyleSheet().apply(self)
    
    def start(self):
        self.main.start_notifier()