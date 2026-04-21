"""
GrowLog — Settings Manager
Salva e carrega preferências do usuário em settings.json
"""

import json
from pathlib import Path

SETTINGS_FILE = 'settings.json'

DEFAULTS = {
    'watering_interval_days': 3,
}


class SettingsManager:
    def __init__(self, base_dir: str = '.'):
        self._path = Path(base_dir) / SETTINGS_FILE
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                with open(self._path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self._data.update(saved)
            except Exception:
                self._data = dict(DEFAULTS)

    def save(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, fallback=None):
        return self._data.get(key, fallback if fallback is not None else DEFAULTS.get(key))

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    @property
    def watering_interval_days(self) -> int:
        return int(self.get('watering_interval_days', 3))

    @watering_interval_days.setter
    def watering_interval_days(self, value: int):
        self.set('watering_interval_days', value)