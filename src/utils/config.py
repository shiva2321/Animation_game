"""Configuration management for the application"""

import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "particle_settings": {
        "spawn_rate": 5,
        "max_particles": 100,
        "initial_particles": 10,
        "min_size": 3,
        "max_size": 15,
        "min_speed": 1,
        "max_speed": 5,
        "shape": "Circle",
    },
    "visual_settings": {
        "color_scheme": "Pastel Dreams",
        "boundary_style": "Solid",
        "enable_glow": True,
        "enable_trails": True,
        "trail_length": 20,
        "collision_effect": "Sparkle",
        "motion_blur": False,
    },
    "audio_settings": {
        "instrument": "Piano",
        "master_volume": 0.5,
        "collision_volume": 0.7,
        "spawn_volume": 0.3,
        "ambient_volume": 0.2,
        "enable_reverb": True,
        "mute_all": False,
    },
    "export_settings": {
        "duration": 90,
        "resolution": "1080p",
        "fps": 60,
        "quality": 90,
    },
    "ui_settings": {
        "theme": "dark",
        "window_width": 1600,
        "window_height": 900,
    },
}


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.presets_dir = self.config_dir / "presets"
        self.presets_dir.mkdir(exist_ok=True)
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_dicts(DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def _merge_dicts(self, defaults, user):
        """Recursively merge user config with defaults"""
        result = defaults.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, *keys, default=None):
        """Get a configuration value using dot notation"""
        if not keys:
            return default

        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, *keys, value):
        """Set a configuration value using dot notation"""
        d = self.config
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()

    def save_preset(self, preset_name):
        """Save current settings as a preset"""
        preset_file = self.presets_dir / f"{preset_name}.json"
        try:
            with open(preset_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving preset: {e}")

    def load_preset(self, preset_name):
        """Load a preset by name"""
        preset_file = self.presets_dir / f"{preset_name}.json"
        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    self.config = json.load(f)
                    return True
            except Exception as e:
                print(f"Error loading preset: {e}")
                return False
        return False

    def list_presets(self):
        """Get list of available presets"""
        presets = []
        if self.presets_dir.exists():
            for f in self.presets_dir.glob("*.json"):
                presets.append(f.stem)
        return sorted(presets)

    def delete_preset(self, preset_name):
        """Delete a preset"""
        preset_file = self.presets_dir / f"{preset_name}.json"
        if preset_file.exists():
            try:
                preset_file.unlink()
                return True
            except Exception as e:
                print(f"Error deleting preset: {e}")
        return False

