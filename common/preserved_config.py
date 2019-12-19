import os
import json
from common import Singleton
from common.app_dir import AppDir


class PreservedConfig(object, metaclass=Singleton):
    def __init__(self, **kwargs):
        self.config_path = os.path.join(AppDir().app_directory, "config.json")
        self.config: dict = dict()
        self.load()

    def add(self, key, obj):
        self.config[key] = obj
        self.write()

    def remove(self, key):
        if key in self.config:
            self.config.pop(key)

    def get(self, key):
        return self.config[key] if key in self.config else None

    def write(self):
        with open(self.config_path, 'w') as conf_file:
            print("Saving configuration")
            conf_file.write(json.dumps(self.config))

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as conf_file:
                self.config = json.load(conf_file)
