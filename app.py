import sys
import os

# AI Imports
from source.rotated_rect_crop import *
from source.VideoCapture import *
from source.AppGui import *

# Tkinter imports
from source.customWidgets import *


def main():
    # =========== Main Window ===========
    AppGuiInstance = AppGui()
    AppGuiInstance.init_window('EyeStrain Monitor')
    AppGuiInstance.init_menu()
    AppGuiInstance.init_pages()

    # AppGuiInstance.app_loop()
    AppGuiInstance.init_videostream()
    AppGuiInstance.update_canvas()
    AppGuiInstance.root_tk.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
