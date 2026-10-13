from PyQt6.QtCore import QObject
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from nicestalker import paths


class SystemTray(QObject):

    def __init__(self, main):
        super().__init__()
        self.main = main
        self._first_hide = True

        self.icon = QSystemTrayIcon(QIcon(paths.resource_path('nightstalker.png')))
        self.icon.setToolTip('NiceStalker')

        self.menu = QMenu()
        self.open_action = QAction('Open settings', self.menu)
        self.open_action.triggered.connect(main.show_window)
        self.toggle_action = QAction('Start notifier', self.menu)
        self.toggle_action.triggered.connect(main.toggle_notifier)
        quit_action = QAction('Quit', self.menu)
        quit_action.triggered.connect(main.quit)

        self.menu.addAction(self.open_action)
        self.menu.addAction(self.toggle_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)

        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self._on_activated)

    @property
    def available(self):
        return QSystemTrayIcon.isSystemTrayAvailable()

    def show(self):
        if not self.available:
            print(
                '[tray] No system tray available. On GNOME, install and enable the '
                '"AppIndicator and KStatusNotifierItem Support" extension '
                '(and make sure extensions are not globally disabled).',
                flush=True,
            )
            return

        self.icon.show()

    def hide(self):
        self.icon.hide()

    def set_running(self, running):
        self.toggle_action.setText('Stop notifier' if running else 'Start notifier')

    def notify_hidden(self):
        if not self.available or not self._first_hide:
            return

        self._first_hide = False
        self.icon.showMessage(
            'NiceStalker',
            'Still running in the background. Use the tray icon to reopen or quit.',
            QSystemTrayIcon.MessageIcon.Information,
            4000,
        )

    def _on_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.main.show_window()
