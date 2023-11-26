import time

import pygame
from decouple import config

from ai.audio.eleven import Eleven
from ai.text.open_ai import ChatGPT
from ai.audio.play_ht import PlayHt
from pynput import keyboard

from play.animation import Animation
from utils.audio_player import AudioPlayer
from utils.logging import log
from assets.audio.notifications import NOTIFY_SPEECH
from utils.text import word_wrap


class Character:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.chat_model_override = yaml.get('chat_model_override', None)
        self.motivation = yaml.get('motivation', None)
        self.rules = yaml.get('rules', None)
        self.voice = yaml.get('voice', None)
        self.animation = Animation(self.name)
        self.paused = False
        self.listener = None

    def chat(self, messages, screen):
        response, usage = ChatGPT.chat(messages, self.chat_model_override)

        log.info(f'Character ({self.name}): {response}')

        if config('ENABLE_SPEECH', cast=bool):
            self.speak(response, screen)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, usage

    def speak(self, text, screen):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        tts_service = config('TTS_SERVICE')
        log.info(f'{tts_service}: Speech synthesis requested')
        if tts_service == 'PlayHT':
            audio_file = PlayHt.fetch_audio_file(text, self.voice)
        elif tts_service == 'ElevenLabs':
            audio_file = Eleven.speak(text, self.voice)
        else:
            audio_file = None
        pygame.mixer.Sound.play(NOTIFY_SPEECH)
        with open('obs_player.txt', "w") as f:
            f.write("")
        time.sleep(0.5)
        with open('obs_ai.txt', "w") as f:
            f.write(word_wrap(text, 75))
        with AudioPlayer(audio_file) as audio_player:
            while self.paused:
                time.sleep(0.5)
            for amplitude in audio_player.play_audio_chunk():
                while self.paused:
                    time.sleep(1)
                self.animation.animate_frame(amplitude, screen)
        screen.fill((0, 255, 0))
        pygame.display.update()


    def on_press(self, key):
        if key == keyboard.Key.right and self.paused:
            self.paused = False
            log.info('Unpaused')
        elif key == keyboard.Key.left and not self.paused:
            self.paused = True
            log.info('Paused')
