import json
import os

class SettingsManager:
    def __init__(self, filename: str) -> None:
        # Get the directory of the current script and construct the relative path
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.filename = os.path.join(script_dir, filename)
        self.settings = {}

        # Load the settings from the file
        self.load_settings()

    def load_settings(self) -> None:
        """Loads settings from the JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    self.settings = json.load(file)
            except json.JSONDecodeError:
                print(f"Error: The file '{self.filename}' contains invalid JSON.")
            except Exception as e:
                print(f"Error: Unable to load settings from '{self.filename}': {e}")
        else:
            # File doesn't exist, initialize with an empty dictionary
            self.settings = {}

    def save_settings(self) -> None:
        """Saves the current settings to the JSON file."""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.settings, file, indent=4)
        except Exception as e:
            print(f"Error: Unable to save settings to '{self.filename}': {e}")

    def get_setting(self, key: str, default=None) -> str:
        """Gets a setting value. If the key does not exist, returns the default value, and creates the key."""
        value = self.settings.get(key, default)
        if value == default:
            self.set_setting(key, value)
        return value

    def set_setting(self, key: str, value) -> None:
        """Sets a setting value and saves it to the file."""
        self.settings[key] = value
        self.save_settings()

    def remove_setting(self, key: str) -> None:
        """Removes a setting from the file and saves the update."""
        if key in self.settings:
            del self.settings[key]
            self.save_settings()
        else:
            print(f"Warning: Setting '{key}' does not exist.")