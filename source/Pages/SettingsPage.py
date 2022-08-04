from tkinter import messagebox
from customtkinter import *
from tkinter import *
from source.utils.Config import AppConfig
import sys
from source.CustomWidgets import NumberSetting, OptionMenuSetting, SettingsDesc, SettingsLabel


def populate_settings_page(frame):
    # To expand the canvas
    CTkFrame(master=frame, width=550, height=0).grid()

    entry = []

    entry.append(NumberSetting(
        frame, AppConfig.cfg["activity"]["max_session"], 'Max Screen Session', 'Longest period in front of the screen before you get notified to take a break\nValue is in integer and seconds. E.g. 10, 20, 5', 0))
    entry.append(NumberSetting(
        frame, AppConfig.cfg["activity"]["min_break"], 'Minimum Break Time', 'The minimum amount of seconds you\'re out of the camera it takes for the program to register you as taking a breaks\nValue is in integer', 1))
    entry.append(NumberSetting(
        frame, AppConfig.cfg["activity"]["max_blink_interval"], 'Max Blink Interval', 'Longest period in seconds between blinks before you get reminded to blink\nValue is in integer', 2))
    entry.append(NumberSetting(
        frame, AppConfig.cfg["activity"]["ai_confidence_threshold"], 'AI Confidence Threshold', 'How confident the AI should think before classifying the the eyes as closed\nFill in value as a floating point number between 100 and 0 exclusive. E.g. 0.9 or 10.0', 3))
    entry.append(NumberSetting(
        frame, AppConfig.cfg["activity"]["eye_crop_height"], 'Eye Crop Height', 'Height of eyes which will be cropped. This will affect how wide the AI thinks the eyes are opened\nValue is in integer between 20 to 60', 4))
    entry.append(OptionMenuSetting(frame, 'Blink Reminder', 'Reminds you to blink after you haven\'t blinked for "Max Blink Interval" seconds.\nVoice: Plays a short voice message\nLong Voice: Plays a sentence\n Visual: Displays a screen overlay (WIP)', 5, [
        'None', 'Voice', 'Long Voice', 'Visual']))
    entry.append(OptionMenuSetting(frame, 'Break Reminder', 'Reminds you to take a break after "Max Screen Session" seconds.\nVoice: Plays a short voice message\nLong Voice: Plays a sentence\n Visual: Displays a screen overlay (WIP)', 6, [
        'None', 'Voice', 'Long Voice', 'Visual']))

    def on_save():
        # Validate and get values
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
        blink_reminder_type = check_reminder_type(
            entry[5].get(), 'Please enter a valid option')
        break_reminder_type = check_reminder_type(
            entry[6].get(), 'Please enter a valid option')

        # Set values
        if (max_session):
            AppConfig.cfg["activity"]["max_session"] = max_session
        if (min_break):
            AppConfig.cfg["activity"]["min_break"] = min_break
        if (max_blink_interval):
            AppConfig.cfg["activity"]["max_blink_interval"] = max_blink_interval
        if (ai_confidence_threshold):
            AppConfig.cfg["activity"]["ai_confidence_threshold"] = ai_confidence_threshold
        if (eye_crop_height):
            AppConfig.cfg["activity"]["eye_crop_height"] = eye_crop_height
        if (blink_reminder_type):
            AppConfig.cfg["activity"]["blink_reminder_type"] = blink_reminder_type
        if (break_reminder_type):
            AppConfig.cfg["activity"]["break_reminder_type"] = break_reminder_type

        AppConfig.save_config()

        # Set placeholder text
        entry[0].configure(
            placeholder_text=AppConfig.cfg["activity"]["max_session"])
        entry[1].configure(
            placeholder_text=AppConfig.cfg["activity"]["min_break"])
        entry[2].configure(
            placeholder_text=AppConfig.cfg["activity"]["max_blink_interval"])
        entry[3].configure(
            placeholder_text=AppConfig.cfg["activity"]["ai_confidence_threshold"])
        entry[4].configure(
            placeholder_text=AppConfig.cfg["activity"]["eye_crop_height"])

        frame.focus()

        # Clear entries
        entry[0].delete(0, END)
        entry[1].delete(0, END)
        entry[2].delete(0, END)
        entry[3].delete(0, END)
        entry[4].delete(0, END)

    CTkButton(master=frame, text="Save", command=on_save).grid(
        sticky="e", pady=(0, 300))


def validate_int(value, error_message):
    if (not value):
        return False

    try:
        return int(value)
    except ValueError:
        messagebox.showerror("Error", error_message)
        return False


def validate_float(value, error_message):
    if (not value):
        return False

    try:
        return float(value)
    except ValueError:
        messagebox.showerror("Error", error_message)
        return False


def check_reminder_type(value, error_message):
    if value == 'None':
        return 'NONE'
    elif value == 'Voice':
        return 'VOICE'
    elif value == 'Long Voice':
        return 'VOICE_LONG'
    elif value == 'Visual':
        return "VISUAL"
    else:
        messagebox.showerror("Error", error_message)
        return False
