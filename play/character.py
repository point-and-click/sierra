import os

import pygame
from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from ai.play_ht import PlayHt
from utils.audio_player import AudioPlayer
from utils.logging import log
from utils.word_wrap import WordWrap


class Character:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.motivation = yaml.get('motivation', None)
        self.rules = yaml.get('rules', None)
        self.voice = yaml.get('voice', None)
        self.max_angle = 35
        self.max_rotation = 3
        self.max_amplitude = 1000
        self.prev_angle = 0
        self.image = None

    def chat(self, messages, screen):
        response, usage = ChatGPT.chat(messages)

        log.info(f'Character ({self.name}): {response}')

        if config('ENABLE_SPEECH', cast=bool):
            self.speak(response, screen)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, usage

    def speak(self, text, screen):
        tts_service = config('TTS_SERVICE')
        log.info(f'{tts_service}: Speech synthesis requested')
        if tts_service == 'PlayHT':
            audio_file = PlayHt.fetch_audio_file(text, self.voice)
        # elif tts_service == 'ElevenLabs':
        #     Eleven.speak(response, self.voice, f'saves/audio/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.wav')
        else:
            audio_file = None
        with open('obs_text.txt', "w") as f:
            f.write(WordWrap.word_wrap(text, 75))
        with AudioPlayer(audio_file) as audio_player:
            for amplitude in audio_player.play_audio_chunk():
                self.animate_frame(amplitude, screen)

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
