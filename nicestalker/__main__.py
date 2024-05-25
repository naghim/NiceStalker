from nicestalker.notifier import NotifierClient
from nicestalker.tray import SystemTray

tray = SystemTray()
tray.start()
client = NotifierClient()
client.init_with_token()
