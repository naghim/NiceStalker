import os
import shutil
import sys

from platformdirs import user_config_dir

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PKG_DIR)

CONFIG_DIR = user_config_dir('NiceStalker', 'naghim')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
ICON_PATH = os.path.join(CONFIG_DIR, 'nightstalker.png')


def resource_path(*parts):
    return os.path.join(PKG_DIR, 'resources', *parts)


def persistent_icon():
    """Return an icon path that survives restarts.

    Under a Nuitka onefile build ``resource_path`` points into a temporary
    extraction directory that is removed when the app exits, so autostart
    entries referencing it would show a broken icon. Copy the icon next to the
    config file instead.
    """
    try:
        ensure_config_dir()
        if not os.path.exists(ICON_PATH):
            shutil.copyfile(resource_path('nightstalker.png'), ICON_PATH)
        return ICON_PATH
    except OSError:
        return resource_path('nightstalker.png')


def _legacy_config_candidates():
    return [
        os.path.join(os.getcwd(), 'config.json'),
        os.path.join(PKG_DIR, 'config.json'),
        os.path.join(ROOT_DIR, 'config.json'),
    ]


def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def migrate_legacy_config():
    if os.path.exists(CONFIG_PATH):
        return

    source = os.path.abspath(CONFIG_PATH)
    for candidate in _legacy_config_candidates():
        candidate = os.path.abspath(candidate)
        if candidate == source or not os.path.isfile(candidate):
            continue
        try:
            ensure_config_dir()
            shutil.copyfile(candidate, CONFIG_PATH)
        except OSError:
            pass
        return
