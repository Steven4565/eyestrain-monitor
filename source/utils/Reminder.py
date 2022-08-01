import pygame
from tkinter import *
from os import environ
from pygame import mixer
# from source.utils.Overlay import OverlayInstance

from source.utils.Config import AppConfig
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()

short_sound_blink = mixer.Sound("./assets/sounds/short_blink.wav")
short_sound_break = mixer.Sound("./assets/sounds/short_break.wav")
long_sound_blink = mixer.Sound("./assets/sounds/voiceover_blink.wav")
long_sound_break = mixer.Sound("./assets/sounds/voiceover_break.wav")


class Reminder:
    def remind_blink():
        reminder_config = AppConfig.cfg["activity"]["reminder_type"]
        if reminder_config == "VOICE":
            short_sound_blink.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_blink.play()
        elif reminder_config == "VISUAL":
            # OverlayInstance.remind_blink()
            pass

    def remind_break():
        reminder_config = AppConfig.cfg["activity"]["reminder_type"]
        if reminder_config == "VOICE":
            short_sound_break.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_break.play()
        elif reminder_config == "VISUAL":
            # OverlayInstance.remind_break()
            pass
