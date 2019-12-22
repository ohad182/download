import os

try:
    import ConfigParser as cp
except ImportError as e:
    import configparser as cp


def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return value


class Configuration(object):
    ENV = "ENV"

    def __init__(self):
        self.config = cp.RawConfigParser()
        self.config_path = None

    def get(self, section, option, default):
        return try_parse_int(self.config.get(section, option)) if self.config.has_option(section, option) else default

    def readcwd(self):
        print("Searching for config file at: {}".format(os.getcwd()))
        config_file = None
        for conf in os.listdir(os.getcwd()):
            if conf.endswith(".ini"):
                config_file = conf
                break

        if config_file:
            self.read(config_file)
            print("Found {}".format(config_file))
            self.expose_env()
        else:
            print("No config file found, working with defaults")

    def read_from_cwd(self, filename: str):
        print("Searching for {} at : {}".format(filename, os.getcwd()))
        config_file = None
        for conf in os.listdir(os.getcwd()):
            if filename in conf:
                config_file = conf
                break

        if config_file:
            self.read(config_file)
            print("Found {}".format(config_file))
            self.expose_env()
        else:
            print("No config file found, working with defaults")

    def read(self, config_file):
        self.config.read(config_file)
        self.config_path = config_file

    def expose_env(self):
        if self.config.has_section(Configuration.ENV):
            for var_name in self.config.options(Configuration.ENV):
                var_name = var_name.upper()
                var_value = self.config.get(Configuration.ENV, var_name).replace('"', "").replace("'", '')
                print("Exposing {} - {}: {}".format(Configuration.ENV, var_name, var_value))
                os.environ[var_name] = var_value
