from PIL import Image, ImageDraw
import threading
import pystray
import sys, os

class SystemTray(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.icon_image = Image.open('nightstalker.png')
        self.menu = pystray.Menu(
            pystray.MenuItem('Quit', self.on_quit)
        )
        self.icon = pystray.Icon('Night Stalker', self.icon_image, 'Night Stalker', self.menu)

    def on_quit(self):
        os._exit(0)

    def run(self):
        self.icon.run()
