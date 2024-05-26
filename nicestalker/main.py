from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from nicestalker.gui.mainwindow import MainWindow
from nicestalker.notifier import NotifierClient
from nicestalker.tray import SystemTray
import json
import asyncio
import os

class Main(object):

    def __init__(self):
        self.app = None
        self.tray = None
        self.window = None
        self.notifier = None
        self.notifier_loop = None
    
    def run(self):
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

    def close_main_window(self):
        if self.window:
            self.window.close()

        if self.app:
            self.app.quit()
        
        self.window = None
        self.app = None

    def close_notifier(self):
        if self.tray:
            self.tray.close()

        if self.notifier_loop:
            for task in asyncio.all_tasks(self.notifier_loop):
                task.cancel()
            
            try:
                self.notifier_loop.close()
            except:
                pass

        self.tray = None       
        self.notifier = None
        self.notifier_loop = None

    def start_main_window(self):
        self.close_main_window()
        self.close_notifier()

        self.app = QApplication([])
        self.app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.window = MainWindow(self)
        self.app.exec()
    
    def start_notifier(self):
        self.close_main_window()
        self.close_notifier()
        
        self.tray = SystemTray(self)
        self.tray.start()
        self.notifier = NotifierClient(self)
        self.notifier_loop = asyncio.new_event_loop()

        try:
            self.notifier_loop.run_until_complete(self.notifier.init_with_token())
        except:
            import traceback
            print(traceback.format_exc())