from nicestalker.discord_token import Discord
from toasted import Toast, Text, Image, ToastImagePlacement
from nicestalker.util import is_partial_match
from nicestalker.tray import SystemTray
import json
import discord
import time
import random

APP_ID = "NiceStalker Notifier"
DISPLAY_NAME = "NiceStalker Notifier"

colors = ["yellow", "green", "blue", "red", "grey"]

with open('config.json', 'r') as f:
    config = json.load(f)

ppl_to_stalk = config['peopleToStalk']

class NotifierClient(discord.Client):

    def __init__(self):
        discord.Client.__init__(self)
        Toast.register_app_id(
            handle = APP_ID,
            display_name = DISPLAY_NAME,
            icon_uri = None
        )
        self.last_update = {}

    async def on_ready(self):
        print('Logged on as', self.user)

    def init_with_token(self):
        discord = Discord()

        if not discord.tokens:
            raise Exception('No Discord token found')
        
        token = discord.tokens[0]
        self.run(token)

    async def alert_online(self, username, discord_id, profile_avatar_url):
        if discord_id in self.last_update and time.time() - self.last_update[discord_id] < 10:
            # Don't spam the user with notifications
            return

        # Update the last update time
        self.last_update[discord_id] = time.time()

        content = f'{username} is now online!'
        elements = []

        if profile_avatar_url:
            elements.append(Image(profile_avatar_url, placement = ToastImagePlacement.LOGO, is_circle = True))
        
        elements.append(Text(content))

        toast = Toast(app_id=APP_ID,  remote_media = True)
        toast.elements = elements
        await toast.show()

    async def on_presence_update(self, before, after):
        is_relationship = isinstance(before, discord.Relationship)
        user = before.user if is_relationship else before

        if ppl_to_stalk and not is_partial_match([user.name, user.global_name, str(user.id)], ppl_to_stalk):
            return

        name = user.global_name if not None else user.name
        discord_id = user.id

        if user.avatar:
            profile_avatar_url = user.avatar.url
        else:
            # Some people don't have avatars, we will give them a random default Discord avatar 
            random_color = random.choice(colors)
            profile_avatar_url = f"https://archive.org/download/discordprofilepictures/discord{random_color}.png"
        
        if before.status != after.status:
            if before.status == discord.Status.offline:
                await self.alert_online(name, discord_id, profile_avatar_url)

if __name__ == '__main__':
    tray = SystemTray()
    tray.start()
    client = NotifierClient()
    client.init_with_token()
