from nicestalker.discord_token import Discord
from toasted import Toast, Text, Image, Progress
import discord
import time

class NotifierClient(discord.Client):

    def __init__(self):
        discord.Client.__init__(self)
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
            elements.append({
                "@type": "image",
                "source": profile_avatar_url,
                "placement": "LOGO",
                "is_circle": True
            })
        
        elements.append({
            "@type": "text",
            "content": content
        })

        data = {"elements": elements}
        toast = Toast.from_json(data)
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
        
        if before.status != after.status and not is_relationship:
            if before.status == discord.Status.offline:
                await self.alert_online(name, discord_id, profile_avatar_url)

client = NotifierClient()
client.init_with_token()
