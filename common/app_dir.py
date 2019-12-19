import os
from common import Singleton, APP_DATA, APP_NAME


class AppDir(object, metaclass=Singleton):
    def __init__(self, **kwargs):
        self.app_directory = self.create_app_dir(True)

    def create_app_dir(self, notify: bool):
        app_dir = os.getenv(APP_DATA)
        if app_dir is not None:
            app_dir = os.path.join(app_dir, APP_NAME)
            try:
                os.makedirs(app_dir)
            except:
                pass

        if notify:
            print("App temp directory: {}".format(app_dir))
        return app_dir
