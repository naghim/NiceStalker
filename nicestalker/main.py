import argparse
import asyncio
import os
import sys

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
import qasync

from nicestalker import paths
from nicestalker.config import Config
from nicestalker.tray import SystemTray

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    import winshell


def is_compiled():
    if '__compiled__' in globals() or getattr(sys, 'frozen', False):
        return True

    argv0 = sys.argv[0]
    return os.path.isfile(argv0) and not argv0.lower().endswith('.py')


class Main(QObject):

    notifierStateChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.app = None
        self.loop = None
        self.tray = None
        self.window = None
        self.notifier = None
        self.notifier_task = None
        self.quitting = False

        if IS_WINDOWS:
            self.startup_shortcut = os.path.join(winshell.startup(), 'NiceStalker.lnk')
        else:
            autostart_dir = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
            self.startup_shortcut = os.path.join(autostart_dir, 'nicestalker.desktop')

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--discord', action='store_true',
                            help='Run the notifier headless, without opening the window.')
        parser.add_argument('--test-notify', action='store_true',
                            help='Send a single test notification and exit.')
        args = parser.parse_args()

        if args.test_notify:
            from nicestalker.notifier import send_notification
            asyncio.run(send_notification('NiceStalker test notification'))
            return

        self.app = QApplication([])
        self.app.setApplicationName('NiceStalker')
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setWindowIcon(QIcon(paths.resource_path('nightstalker.png')))

        self.loop = qasync.QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

        self.tray = SystemTray(self)
        self.tray.show()

        if args.discord:
            self.start_notifier()
        else:
            self.show_window()

        with self.loop:
            self._install_signal_handlers()
            self.loop.run_forever()

    def _install_signal_handlers(self):
        import signal

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self.loop.add_signal_handler(sig, self.quit)
            except (NotImplementedError, RuntimeError):
                signal.signal(sig, lambda *_: self.quit())

    def show_window(self):
        if self.window is None:
            from nicestalker.gui.mainwindow import MainWindow
            self.window = MainWindow(self)

        self.window.show()
        if self.window.isMinimized():
            self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def is_notifier_running(self):
        return self.notifier_task is not None and not self.notifier_task.done()

    def start_notifier(self):
        if self.is_notifier_running():
            return

        from nicestalker.notifier import NotifierClient
        self.notifier = NotifierClient(self)
        self.notifier_task = self.loop.create_task(self.notifier.run())

    def stop_notifier(self):
        if self.notifier is not None:
            self.loop.create_task(self.notifier.shutdown())

    def toggle_notifier(self):
        if self.is_notifier_running():
            self.stop_notifier()
        else:
            self.start_notifier()

    def notifier_started(self):
        self.tray.set_running(True)
        self.notifierStateChanged.emit(True)

    def notifier_stopped(self):
        self.notifier = None
        self.notifier_task = None
        self.tray.set_running(False)
        self.notifierStateChanged.emit(False)

    def quit(self):
        if self.quitting:
            return

        self.quitting = True
        if self.notifier is not None:
            self.loop.create_task(self.notifier.shutdown())
        self.tray.hide()
        self.app.quit()

    def add_to_startup(self):
        self.remove_from_startup()

        if IS_WINDOWS:
            with winshell.shortcut(self.startup_shortcut) as link:
                if is_compiled():
                    link.path = os.path.abspath(sys.argv[0])
                    link.arguments = '--discord'
                    link.working_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
                else:
                    link.path = sys.executable
                    link.arguments = '-m nicestalker --discord'
                    link.working_directory = paths.ROOT_DIR

                link.description = 'NiceStalker Notifier'
                link.write()
        else:
            os.makedirs(os.path.dirname(self.startup_shortcut), exist_ok=True)

            if is_compiled():
                exec_line = f'{os.path.abspath(sys.argv[0])} --discord'
                work_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            else:
                exec_line = f'{sys.executable} -m nicestalker --discord'
                work_dir = paths.ROOT_DIR

            desktop_entry = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=NiceStalker Notifier\n"
                f"Exec={exec_line}\n"
                f"Path={work_dir}\n"
                f"Icon={paths.persistent_icon()}\n"
                "Terminal=false\n"
                "Hidden=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            with open(self.startup_shortcut, 'w', encoding='utf-8') as f:
                f.write(desktop_entry)

    def remove_from_startup(self):
        if os.path.exists(self.startup_shortcut):
            os.remove(self.startup_shortcut)
