import traceback
import json
import asyncio
import winshell
import argparse
import os
import sys

class Main(object):

    def __init__(self):
        self.app = None
        self.tray = None
        self.window = None
        self.notifier = None
        self.notifier_loop = None
    
    def run(self):
        self.startup = winshell.startup()
        self.startup_shortcut = os.path.join(self.startup, 'NiceStalker.lnk')
        self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--discord', action='store_true', help='Start NiceStalker as a Discord bot.')
        args = parser.parse_args()

        if args.discord:
            self.start_notifier()
        else:
            self.start_main_window()
    
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.ppl_to_stalk = []
            self.ppl_to_ignore = []
            self.run_on_startup = False
            return

        self.ppl_to_stalk = self.config['peopleToStalk']
        self.ppl_to_ignore = self.config['peopleToIgnore']
        self.run_on_startup = bool(self.config.get('runOnStartup', False))

    def save_config(self):
        data = {
            'peopleToStalk': self.ppl_to_stalk,
            'peopleToIgnore': self.ppl_to_ignore,
            'runOnStartup': self.run_on_startup
        }

        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, separators=(',', ': '))

    def start_main_window(self):
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        from nicestalker.gui.mainwindow import MainWindow

        self.app = QApplication([])
        self.app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.window = MainWindow(self)
        self.app.exec()
    
    def start_notifier(self):
        from nicestalker.notifier import NotifierClient
        from nicestalker.tray import SystemTray
        self.tray = SystemTray(self)
        self.tray.start()
        self.notifier = NotifierClient(self)
        self.notifier_loop = asyncio.new_event_loop()

        try:
            self.notifier_loop.run_until_complete(self.notifier.init_with_token())
        except:
            print(traceback.format_exc())
    
    def add_to_startup(self):
        self.remove_from_startup()

        with winshell.shortcut(self.startup_shortcut) as link:
            is_nuitka = '__compiled__' in globals()

            if is_nuitka:
                link.path = os.path.abspath(sys.argv[0])
                link.arguments = '--discord'
            else:
                link.path = sys.executable
                link.arguments = '-m nicestalker --discord'

            link.description = 'NiceStalker Notifier'
            link.working_directory = os.getcwd()
            link.write()
    
    def remove_from_startup(self):
        if os.path.exists(self.startup_shortcut):
            os.remove(self.startup_shortcut)