from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from nicestalker.gui.mainwindow import MainWindow
from nicestalker.notifier import NotifierClient
from nicestalker.tray import SystemTray
import json
import asyncio

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
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        self.ppl_to_stalk = self.config['peopleToStalk']
        self.ppl_to_ignore = self.config['peopleToIgnore']

    def close_main_window(self):
        if self.window:
            print('Close window')
            self.window.close()

        if self.app:
            print('Quit app')
            self.app.quit()
        
        self.window = None
        self.app = None

    def close_notifier(self):
        if self.tray:
            self.tray.close()

        if self.notifier_loop:
            print('Close notifier loop')
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
        print('Create notifier')
        self.tray = SystemTray(self)
        self.tray.start()
        self.notifier = NotifierClient(self)
        self.notifier_loop = asyncio.new_event_loop()

        try:
            self.notifier_loop.run_until_complete(self.notifier.init_with_token())
        except:
            import traceback
            print(traceback.format_exc())