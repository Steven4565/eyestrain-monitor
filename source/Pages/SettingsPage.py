from customtkinter import *
from tkinter import *

from source.customWidgets import NumberSetting, SettingsDesc, SettingsLabel


def populate_settings_page(frame):
    CTkFrame(master=frame, width=600, height=0).grid()

    entry1 = NumberSetting(frame, 'Max Screen Session', 'desc', 0)
    entry2 = NumberSetting(frame, 'Minimum Break Time', 'desc', 1)
    entry1 = NumberSetting(frame, 'Max Blink Interval', 'desc', 2)
    entry1 = NumberSetting(frame, 'AI Confidence Threshold', 'desc', 3)
    entry1 = NumberSetting(frame, 'Eye Crop Height', 'desc', 4)
    entry1 = NumberSetting(frame, 'Reminder Type', 'desc', 5)

    CTkButton(master=frame, text="Save", command=lambda: print(
        entry1.get())).grid(sticky="e")


def on_save():
    print()
