from pygame import mixer
import pygame
from os import environ

from source.utils.Config import AppConfig
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()

short_sound_blink = mixer.Sound("./sounds/short_blink.wav")
short_sound_break = mixer.Sound("./sounds/short_break.wav")
long_sound_blink = mixer.Sound("./sounds/voiceover_blink.wav")
long_sound_break = mixer.Sound("./sounds/voiceover_break.wav")


class Sounds:

    def playBlink():
        reminder_config = AppConfig.cfg["activity"]["reminder_type"]
        if reminder_config == "VOICE":
            short_sound_blink.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_blink.play()

    def playBreak():
        reminder_config = AppConfig.cfg["activity"]["reminder_type"]
        if reminder_config == "VOICE":
            short_sound_break.play()
        elif reminder_config == "VOICE_LONG":
            long_sound_break.play()
