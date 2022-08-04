import sys
import os

# Mute pygame's messages and suppress OpenCV's complaints.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"

# AI Imports
from source.rotated_rect_crop import *
from source.VideoCapture import *
from source.AppGui import *
from source.utils.Config import *

# Tkinter imports
from source.CustomWidgets import *


def main():

    # =========== Main Window ===========
    AppConfig.load_config()

    AppGuiInstance.init_window('EyeStrain Monitor')
    AppGuiInstance.init_menu()
    AppGuiInstance.init_pages()

    AppGuiInstance.init_videostream(AppConfig.cfg["video"]["camera_index"])
    AppGuiInstance.update_canvas()
    AppGuiInstance.app_loop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('App closed by keyboard interrupt.')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
