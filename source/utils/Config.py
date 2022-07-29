from typing import Any
from tkinter import messagebox
import sys
import yaml

# TODO: Better Error handling/message box???
class AppConfigClass:
    _file_name: str
    cfg: Any
    has_loaded: bool

    def __init__(self, file_name):
        self._file_name = file_name

    def load_config(self):
        try:
            with open(self._file_name, "r") as f:
                self.cfg = yaml.load(f, Loader=yaml.FullLoader)
                self.has_loaded = True
        except OSError:
            messagebox.showerror("Failed to load config", "Could not open/read file: {}".format(self._file_name))
            sys.exit()
    
    def save_config(self):
        try:
            with open(self._file_name, "w") as f:
                yaml.dump(self.cfg, stream=f, default_flow_style=False, sort_keys=False)
        except OSError:
            messagebox.showerror("Failed to load config", "Could not open/write file: {}".format(self._file_name))
            sys.exit()

AppConfig = AppConfigClass()
