from nicestalker.discord_token import Discord
from nicestalker.util import is_partial_match
from nicestalker.tray import SystemTray
import json
import sys
import subprocess
import discord
import time
import random

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    from toasted import Toast, Text, Image, ToastImagePlacement

APP_ID = "NiceStalker Notifier"
DISPLAY_NAME = "NiceStalker Notifier"

colors = ["yellow", "green", "blue", "red", "grey"]

class NotifierClient(discord.Client):

    def __init__(self, main):
        discord.Client.__init__(self)
        self.main = main
        if IS_WINDOWS:
            Toast.register_app_id(
                handle = APP_ID,
                display_name = DISPLAY_NAME,
                icon_uri = None
            )
        self.last_update = {}

    async def on_ready(self):
        print('Logged on as', self.user, flush=True)
        try:
            print(f'Watching for: {self.main.ppl_to_stalk}', flush=True)
            print(f'Ignoring: {self.main.ppl_to_ignore}', flush=True)
            friends = [r for r in self.relationships if r.type == discord.RelationshipType.friend]
            print(f'Friends list ({len(friends)}):',  flush=True)
            for r in friends:
                print(f'  - {r.user.name} (global: {r.user.global_name}, id: {r.user.id})', flush=True)
        except Exception as e:
            print(f'[ERROR in on_ready] {e}', flush=True)
            import traceback
            traceback.print_exc()

    async def init_with_token(self):
        discord = Discord()

        if not discord.tokens:
            raise Exception('No Discord token found')
        
        token = discord.tokens[0]
        await self.start(token)

    async def alert_online(self, username, discord_id, profile_avatar_url):
        if discord_id in self.last_update and time.time() - self.last_update[discord_id] < 10:
            return

        self.last_update[discord_id] = time.time()

        content = f'{username} is now online!'
        print(f'[ALERT] {content}')

        if IS_WINDOWS:
            elements = []
            if profile_avatar_url:
                elements.append(Image(profile_avatar_url, placement = ToastImagePlacement.LOGO, is_circle = True))
            elements.append(Text(content))
            toast = Toast(app_id=APP_ID, remote_media = True)
            toast.elements = elements
            await toast.show()
        else:
            try:
                result = subprocess.run(
                    ['notify-send', '-a', DISPLAY_NAME, DISPLAY_NAME, content],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    print(f'[ALERT] notify-send failed: {result.stderr}')
            except FileNotFoundError:
                print(content)

    async def alert_activity(self, username, discord_id, activity_name):
        if discord_id in self.last_update and time.time() - self.last_update[discord_id] < 10:
            return

        self.last_update[discord_id] = time.time()

        content = f'{username} started playing {activity_name}!'
        print(f'[ALERT] {content}')

        if IS_WINDOWS:
            elements = [Text(content)]
            toast = Toast(app_id=APP_ID, remote_media=True)
            toast.elements = elements
            await toast.show()
        else:
            try:
                result = subprocess.run(
                    ['notify-send', '-a', DISPLAY_NAME, DISPLAY_NAME, content],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    print(f'[ALERT] notify-send failed: {result.stderr}')
            except FileNotFoundError:
                print(content)

    def _get_activities(self, presence):
        return getattr(presence, 'activities', ()) or ()

    async def on_presence_update(self, before, after):
        is_relationship = isinstance(before, discord.Relationship)
        user = before.user if is_relationship else before
        matches = [user.name, user.global_name, str(user.id)]

        print(f'[DEBUG] before type={type(before).__name__}, after type={type(after).__name__}, same obj={before is after}', flush=True)
        print(f'[DEBUG] before.status={before.status}, after.status={after.status}', flush=True)

        before_activities = self._get_activities(before)
        after_activities = self._get_activities(after)

        print(f'[DEBUG] before activities raw: {before_activities}', flush=True)
        print(f'[DEBUG] after activities raw: {after_activities}', flush=True)

        before_act_names = {a.name for a in before_activities if a.name}
        after_act_names = {a.name for a in after_activities if a.name}
        new_activities = after_act_names - before_act_names

        print(f'[PRESENCE] {user.name} (global: {user.global_name}, id: {user.id}): {before.status} -> {after.status} | activities: {before_act_names} -> {after_act_names}', flush=True)

        if self.main.ppl_to_stalk and not is_partial_match(matches, self.main.ppl_to_stalk):
            print(f'  [SKIP] Not in watch list. matches={matches}, stalk={self.main.ppl_to_stalk}')
            return
    
        if self.main.ppl_to_ignore and is_partial_match(matches, self.main.ppl_to_ignore):
            print(f'  [SKIP] In ignore list')
            return

        name = user.global_name if user.global_name is not None else user.name
        discord_id = user.id

        if user.avatar:
            profile_avatar_url = user.avatar.url
        else:
            random_color = random.choice(colors)
            profile_avatar_url = f"https://archive.org/download/discordprofilepictures/discord{random_color}.png"

        print(f'  [CHECK] status changed: {before.status != after.status}, was offline: {before.status == discord.Status.offline}, new activities: {new_activities}')
        
        if before.status != after.status:
            if before.status == discord.Status.offline and after.status != discord.Status.offline:
                await self.alert_online(name, discord_id, profile_avatar_url)

        for activity_name in new_activities:
            await self.alert_activity(name, discord_id, activity_name)
