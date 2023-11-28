import os
import time

import pygame
from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from ai.play_ht import PlayHt
from pynput import keyboard
from utils.audio_player import AudioPlayer
from utils.logging import log
from utils.word_wrap import WordWrap


class Character:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.chat_model_override = yaml.get('chat_model_override', None)
        self.motivation = yaml.get('motivation', None)
        self.rules = yaml.get('rules', None)
        self.voice = yaml.get('voice', None)
        self.max_angle = 35
        self.max_rotation = 3
        self.max_amplitude = 1000
        self.prev_angle = 0
        self.image = None
        self.speak_sound = None
        self.paused = False
        self.listener = None

    def chat(self, messages, screen):
        response, usage = ChatGPT.chat(messages, self.chat_model_override)

        log.info(f'Character ({self.name}): {response}')

        audio_file = None
        if config('ENABLE_SPEECH', cast=bool):
            audio_file = self.speak(response, screen)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, usage, audio_file

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
        if self.speak_sound is None:
            self.speak_sound = pygame.mixer.Sound("beep_basic_low.mp3")
            self.speak_sound.set_volume(0.1)
        pygame.mixer.Sound.play(self.speak_sound)
        with open('obs_player.txt', "w") as f:
            f.write("")
        time.sleep(0.5)
        with open('obs_ai.txt', "w") as f:
            f.write(WordWrap.word_wrap(text, 75))
        return audio_file

    def animate_frame(self, amplitude, screen):
        if self.image is None:
            file_name = f"config/characters/images/{self.name}.png"
            if os.path.isfile(file_name):
                self.image = pygame.image.load(file_name).convert_alpha()
        if amplitude > self.max_amplitude:
            self.max_amplitude = amplitude

        scaled_amplitude = min(amplitude, self.max_amplitude) / self.max_amplitude
        target_angle = scaled_amplitude * self.max_angle
        target_rotation_amount = target_angle - self.prev_angle
        actual_rotation_amount = max(-self.max_rotation, min(self.max_rotation, target_rotation_amount))
        new_angle = max(-self.max_angle, min(self.max_angle, actual_rotation_amount + self.prev_angle))
        rotated_image = pygame.transform.rotate(self.image, new_angle)
        rotated_rect = rotated_image.get_rect(center=self.image.get_rect().center)
        self.prev_angle = new_angle

        pygame.event.get()
        screen.fill((0, 255, 0))
        screen.blit(rotated_image, rotated_rect)
        pygame.display.update()

    def on_press(self, key):
        if key == keyboard.Key.right and self.paused:
            self.paused = False
            log.info('Unpaused')
        elif key == keyboard.Key.left and not self.paused:
            self.paused = True
            log.info('Paused')
