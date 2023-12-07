import pygame
from decouple import config

pygame.init()
SCREEN = pygame.display.set_mode((1920, 1080))
SCREEN.fill((0, 255, 0))
pygame.display.update()
pygame.display.set_caption("Sierra")
NOTIFY_PRESS = pygame.mixer.Sound("assets/audio/beep_basic_high.mp3")
NOTIFY_PRESS.set_volume(0.1)
NOTIFY_RELEASE = pygame.mixer.Sound("assets/audio/beep_basic.mp3")
NOTIFY_RELEASE.set_volume(0.1)
NOTIFY_SPEECH = pygame.mixer.Sound("assets/audio/beep_basic_low.mp3")
NOTIFY_SPEECH.set_volume(0.1)

FONT = pygame.font.Font(config('SUBTITLE_FONT'), config('SUBTITLE_FONT_SIZE', cast=int))
FONT.set_bold(config('SUBTITLE_FONT_BOLD', cast=bool))
