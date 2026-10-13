import asyncio
import random
import sys
import time
import traceback

import discord

from nicestalker import paths
from nicestalker.discord_token import Discord
from nicestalker.util import is_partial_match

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    from toasted import Toast, Text, Image, ToastImagePlacement

APP_ID = 'NiceStalker Notifier'
DISPLAY_NAME = 'NiceStalker Notifier'

ALERT_COOLDOWN = 10
colors = ['yellow', 'green', 'blue', 'red', 'grey']


class NotifierClient(discord.Client):

    def __init__(self, main):
        super().__init__()
        self.main = main
        self.running = False
        self._last_online = {}
        self._last_activity = {}

        if IS_WINDOWS:
            Toast.register_app_id(
                handle=APP_ID,
                display_name=DISPLAY_NAME,
                icon_uri=None,
            )

    @property
    def config(self):
        return self.main.config

    async def run(self):
        try:
            token = await asyncio.to_thread(self._grab_token)
            await self.start(token)
        except asyncio.CancelledError:
            raise
        except Exception:
            traceback.print_exc()
        finally:
            self.running = False
            self.main.notifier_stopped()

    async def shutdown(self):
        self.running = False
        try:
            await self.close()
        except Exception:
            pass

    def _grab_token(self):
        grabber = Discord()
        if not grabber.tokens:
            raise RuntimeError(
                'No Discord token found. Make sure the Discord client is installed and logged in.'
            )
        return grabber.tokens[0]

    async def on_ready(self):
        self.running = True
        print(f'Logged in as {self.user} (id: {self.user.id})', flush=True)
        print(f'Watching for: {self.config.people_to_stalk}', flush=True)
        print(f'Ignoring: {self.config.people_to_ignore}', flush=True)

        friends = [r for r in self.relationships if r.type == discord.RelationshipType.friend]
        print(f'Friends ({len(friends)}):', flush=True)
        for r in friends:
            print(f'  - {r.user.name} (global: {r.user.global_name}, id: {r.user.id})', flush=True)

        self.main.notifier_started()

    def _user(self, obj):
        return obj.user if isinstance(obj, discord.Relationship) else obj

    def _status(self, obj):
        return getattr(obj, 'status', discord.Status.offline)

    def _activity_names(self, obj):
        names = set()
        for activity in getattr(obj, 'activities', ()) or ():
            if getattr(activity, 'type', None) == discord.ActivityType.custom:
                continue
            if activity.name:
                names.add(activity.name)
        return names

    def _avatar_url(self, user):
        if user.avatar:
            return user.avatar.url

        color = random.choice(colors)
        return f'https://archive.org/download/discordprofilepictures/discord{color}.png'

    def _throttled(self, table, key):
        now = time.time()
        if key in table and now - table[key] < ALERT_COOLDOWN:
            return True
        table[key] = now
        return False

    async def on_presence_update(self, before, after):
        user = self._user(after)
        matches = [user.name, user.global_name, str(user.id)]

        stalk = self.config.people_to_stalk
        ignore = self.config.people_to_ignore
        if stalk and not is_partial_match(matches, stalk):
            return
        if ignore and is_partial_match(matches, ignore):
            return

        before_status = self._status(before)
        after_status = self._status(after)
        new_activities = self._activity_names(after) - self._activity_names(before)

        name = user.global_name or user.name

        if before_status == discord.Status.offline and after_status != discord.Status.offline:
            await self.alert_online(name, user.id, user)

        for activity_name in new_activities:
            await self.alert_activity(name, user.id, activity_name)

    async def alert_online(self, username, discord_id, user):
        if self._throttled(self._last_online, discord_id):
            return

        await self._notify(f'{username} is now online!', avatar_url=self._avatar_url(user))

    async def alert_activity(self, username, discord_id, activity_name):
        if self._throttled(self._last_activity, (discord_id, activity_name)):
            return

        await self._notify(f'{username} started playing {activity_name}!')

    async def _notify(self, content, avatar_url=None):
        await send_notification(content, avatar_url=avatar_url)


async def send_notification(content, avatar_url=None):
    print(f'[ALERT] {content}', flush=True)

    if IS_WINDOWS:
        elements = []
        if avatar_url:
            elements.append(Image(avatar_url, placement=ToastImagePlacement.LOGO, is_circle=True))
        elements.append(Text(content))
        toast = Toast(app_id=APP_ID, remote_media=True)
        toast.elements = elements
        await toast.show()
    else:
        await _notify_linux(content)


async def _notify_linux(content):
    try:
        proc = await asyncio.create_subprocess_exec(
            'notify-send',
            '-a', DISPLAY_NAME,
            '-i', paths.resource_path('nightstalker.png'),
            DISPLAY_NAME,
            content,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return

    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f'[ALERT] notify-send failed: {stderr.decode(errors="ignore")}', flush=True)
