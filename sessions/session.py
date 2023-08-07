import logging
from datetime import datetime

from characters.character import Character
from sessions.recorder import Recorder
from ai.open_ai import Whisper

from utils import log_format, palette


class Session:
    def __init__(self, character_name):
        self.time = datetime.now()
        self.character = Character(character_name)
        self.recorder = Recorder()
        self.whisper = Whisper()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def begin(self):
        while True:
            self.recorder.record('temp/input.wav')
            prompt = self.whisper.transcribe('temp/input.wav')
            logging.info(f'{log_format.color(palette.material.orange)}'
                         f'Input'
                         f'{log_format.reset()}: '
                         f'{prompt}')

            response = self.character.chat(prompt)
            logging.info(
                f'{log_format.color(palette.material.indigo)}'
                f'{self.character.name.title().replace("_", " ")}'
                f'{log_format.reset()}: '
                f'{response}'
            )
            self.save(response)

    def save(self, response):
        with open(f'saves/{self.character.name}/{self.time}.clog', 'a') as f:
            f.write(response)
