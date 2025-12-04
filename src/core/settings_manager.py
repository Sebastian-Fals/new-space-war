import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = {
            "fps": 60,
            "width": 1280,
            "height": 720,
            "language": "en",
            "fullscreen": False,
            "show_fps": False,
            "music_volume": 0.5,
            "sfx_volume": 0.5,
            "high_score": 0,
            "use_bloom": True,
            "use_vignette": True,
            "use_chromatic": False,
            "use_fxaa": False,
            "msaa_enabled": True
        }
        self.load()

    def load(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def save(self):
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
