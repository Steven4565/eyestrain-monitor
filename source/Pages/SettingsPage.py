from tkinter import messagebox
from customtkinter import *
from tkinter import *
from source.utils.Config import AppConfig
import sys
from source.customWidgets import NumberSetting, OptionMenuSetting, SettingsDesc, SettingsLabel


def populate_settings_page(frame):
    # To expand the canvas
    CTkFrame(master=frame, width=550, height=0).grid()

    entry = []

    entry.append(NumberSetting(frame, 'Max Screen Session', 'desc', 0))
    entry.append(NumberSetting(frame, 'Minimum Break Time', 'desc', 1))
    entry.append(NumberSetting(frame, 'Max Blink Interval', 'desc', 2))
    entry.append(NumberSetting(frame, 'AI Confidence Threshold', 'desc', 3))
    entry.append(NumberSetting(frame, 'Eye Crop Height', 'desc', 4))
    entry.append(OptionMenuSetting(frame, 'Reminder', 'desc', 5, [
        'Voice', 'Long Voice', 'Visual']))

    def on_save():
        max_session = validate_int(
            entry[0].get(), 'Max Session must be an integer')
        min_break = validate_int(
            entry[1].get(), 'Min break must be an integer')
        max_blink_interval = validate_int(
            entry[2].get(), 'max blink interval must be an integer')
        ai_confidence_threshold = validate_float(
            entry[3].get(), 'AI Confidence Threshold must be a float')
        eye_crop_height = validate_int(
            entry[4].get(), 'Eye Crop Height must be an integer')
        reminder_type = check_reminder_type(
            entry[5].get(), 'Please enter a valid option')

        if (max_session):
            AppConfig.cfg["activity"]["max_session"] = max_session
        if (min_break):
            AppConfig.cfg["activity"]["min_break"] = min_break
        if (max_blink_interval):
            AppConfig.cfg["activity"]["max_blink_interval"] = max_blink_interval
        if (ai_confidence_threshold):
            AppConfig.cfg["activity"]["ai_confidence_threshold"] = ai_confidence_threshold
        if (eye_crop_height):
            AppConfig.cfg["activity"]["eye_crop_height"] = ai_confidence_threshold
        if (reminder_type):
            AppConfig.cfg["activity"]["reminder_type"] = reminder_type

        AppConfig.save_config()

        entry[0].delete(0, END)
        entry[1].delete(0, END)
        entry[2].delete(0, END)
        entry[3].delete(0, END)
        entry[4].delete(0, END)

    CTkButton(master=frame, text="Save", command=on_save).grid(
        sticky="e", pady=(0, 50))


def validate_int(value, error_message):
    if (not value):
        return False

    try:
        return int(value)
    except ValueError:
        messagebox.showerror(error_message)
        return False


def validate_float(value, error_message):
    if (not value):
        return False

    try:
        return float(value)
    except ValueError:
        messagebox.showerror(error_message)
        return False


def check_reminder_type(value, error_message):
    if value == 'Voice':
        return 'VOICE'
    elif value == 'Long Voice':
        return 'VOICE_LONG'
    elif value == 'Visual':
        return "VISUAL"
    else:
        messagebox.showerror(error_message)
        return False
