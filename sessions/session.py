import logging
from datetime import datetime

from characters.character import Character
from sessions.recorder import Recorder, RECORD_BINDING
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
            logging.info(
                f'{log_format.color(palette.material.orange)}'
                f'Input'
                f'{log_format.reset()}: '
                f'Press {str(RECORD_BINDING)} to record.'
            )
            self.recorder.record('temp/input.wav')
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'Whisper'
                f'{log_format.reset()}: '
                f'Transcribing recorded audio.'
            )
            prompt = self.whisper.transcribe('temp/input.wav')

            if input(
                    f'{log_format.color(palette.material.orange)}'
                    f'Input'
                    f'{log_format.reset()}: '
                    f'{log_format.color(palette.material.cyan)}'
                    f'Whisper transcribed'
                    f'{log_format.reset()}: '
                    f'{prompt}\n'
                    f'Does this look correct? (Y/N): '
            ).lower().startswith('y'):
                response = self.character.chat(prompt)
                self.save(response)

    def save(self, response):
        with open(f'saves/{self.character.name}/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.clog', 'a') as f:
            f.write(response)
