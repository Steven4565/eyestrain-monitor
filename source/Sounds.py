from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from pygame import mixer

SHORT_VOICEOVER = True

pygame.init()

short_sound_blink = mixer.Sound("./sounds/short_blink.wav")
short_sound_break = mixer.Sound("./sounds/short_break.wav")
long_sound_blink = mixer.Sound("./sounds/voiceover_blink.wav")
long_sound_break = mixer.Sound("./sounds/voiceover_break.wav")


class Sounds:

    def playBlink():
        if SHORT_VOICEOVER:
            short_sound_blink.play()
        else:
            long_sound_blink.play()

    def playBreak():
        if SHORT_VOICEOVER:
            short_sound_break.play()
        else:
            long_sound_break.play()
