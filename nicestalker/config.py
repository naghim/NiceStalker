import json
import os
from dataclasses import dataclass, field

from nicestalker import paths


@dataclass
class Config:
    people_to_stalk: list = field(default_factory=list)
    people_to_ignore: list = field(default_factory=list)
    run_on_startup: bool = False

    @classmethod
    def load(cls):
        paths.migrate_legacy_config()

        config = cls()
        try:
            with open(paths.CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (OSError, ValueError):
            return config

        config.people_to_stalk = list(data.get('peopleToStalk') or [])
        config.people_to_ignore = list(data.get('peopleToIgnore') or [])
        config.run_on_startup = bool(data.get('runOnStartup', False))
        return config

    def save(self):
        paths.ensure_config_dir()
        data = {
            'peopleToStalk': self.people_to_stalk,
            'peopleToIgnore': self.people_to_ignore,
            'runOnStartup': self.run_on_startup,
        }
        with open(paths.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, separators=(',', ': '))
