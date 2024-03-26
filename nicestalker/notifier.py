from nicestalker.discord_token import Discord
from toasted import Toast, Text, Image, ToastImagePlacement
from toasted.common import resolve_uri
from pathlib import Path
from tempfile import TemporaryFile
import discord
import time

APP_ID = "NiceStalker Notifier"
DISPLAY_NAME = "NiceStalker Notifier"

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

        if is_relationship:
            name = before.user.global_name
            discord_id = before.user.id
            profile_avatar_url = before.user.avatar.url if before.user.avatar else None
        else:
            name = before.global_name
            discord_id = before.id
            profile_avatar_url = before.avatar.url if before.avatar else None
        
        if before.status != after.status:
            if before.status == discord.Status.offline:
                await self.alert_online(name, discord_id, profile_avatar_url)

client = NotifierClient()
client.init_with_token()
