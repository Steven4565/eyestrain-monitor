import sys
import webbrowser
import pygame
from tkinter import *
from os import environ
from pygame import mixer

from source.utils.Config import AppConfig
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()
short_sound_blink = mixer.Sound("./assets/sounds/short_blink.wav")
short_sound_break = mixer.Sound("./assets/sounds/short_break.wav")
long_sound_blink = mixer.Sound("./assets/sounds/voiceover_blink.wav")
long_sound_break = mixer.Sound("./assets/sounds/voiceover_break.wav")

toaster = None
app_icon = './assets/images/icon.ico'

is_win10 = False

# if (sys.platform == 'win32' and sys.getwindowsversion().build <= 20000):
is_win10 = True
from win10toast_click import ToastNotifier
toaster = ToastNotifier()


class Reminder:
    
    def remind_blink():
        reminder_config = AppConfig.cfg["activity"]["blink_reminder_type"]
        if reminder_config == "VOICE":
            short_sound_blink.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_blink.play()
        elif reminder_config == "VISUAL":
            # AppGuiInstance.overlay.remind_blink()
            pass

    def remind_break():
        reminder_config = AppConfig.cfg["activity"]["break_reminder_type"]
        if reminder_config == "VOICE":
            short_sound_break.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_break.play()
        elif reminder_config == "VISUAL":
            # OverlayInstance.remind_break()
            pass

    def notify_blink_average(average):
        if (not is_win10):
            return

        remarks = Reminder.get_remarks(average)
        message = ''

        def on_notif_click():
            try:
                webbrowser.open('https://youtu.be/dQw4w9WgXcQ')
            except:
                print('failed to open link')

        if (remarks == 'bad'):
            message = 'Please blink more. Click here to view an eye exercise'
        elif (remarks == 'ok'):
            message = 'You blink enough'
        elif (remarks == 'good'):
            message = 'You blink a lot. Keep it up!'
        else:
            message = 'You blink more than most people. Keep it up!'

        if (remarks == 'bad'):
            return toaster.show_toast(
                title='Here\'s your blink report for this session',
                msg='You have blinked {0} amount of times per minute average. {1}'.format(
                    round(average), message),
                duration=10,
                callback_on_click=on_notif_click,
                threaded=True,
                icon_path=app_icon
            )
        toaster.show_toast(
            title='Here\'s your blink report for this session',
            msg='You have blinked {0} amount of times per minute average. {1}'.format(
                round(average), message),
            duration=10,
            threaded=True,
            icon_path=app_icon,
        )

    def get_remarks(average):
        if average < 10:
            return 'bad'
        elif average < 30:
            return 'ok'
        elif average < 50:
            return 'good'
        else:
            return 'great'
