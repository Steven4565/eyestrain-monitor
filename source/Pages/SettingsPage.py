from customtkinter import *
from tkinter import *
from source.utils.Config import AppConfig

from source.customWidgets import NumberSetting, OptionMenuSetting, SettingsDesc, SettingsLabel


def populate_settings_page(frame):
    # To expand the canvas
    CTkFrame(master=frame, width=550, height=0).grid()

    entry1 = NumberSetting(frame, 'Max Screen Session',
                           'descasdkjfhao\nwiuehfljkasdhflkjahwlekjfhalskidhfliuwehflkjwdhfliuehlwaijhfdlkjhliewuhlkjdhflkuhelkwajhldksjfh', 0)
    entry2 = NumberSetting(frame, 'Minimum Break Time', 'desc', 1)
    entry3 = NumberSetting(frame, 'Max Blink Interval', 'desc', 2)
    entry4 = NumberSetting(frame, 'AI Confidence Threshold', 'desc', 3)
    entry5 = NumberSetting(frame, 'Eye Crop Height', 'desc', 4)
    entry6 = OptionMenuSetting(frame, 'Reminder', 'desc', 5, [
                               'Voice', 'Long Voice', 'Visual'])

    

    CTkButton(master=frame, text="Save", command=lambda: on_save(entry)).grid(sticky="e", pady=(0, 50))


def on_save(entry):
    # AppConfig.save_config()
    # print(AppConfig.cfg['activity']['max_session'])
    print(entry.get())
