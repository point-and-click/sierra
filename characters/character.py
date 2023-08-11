import logging
from datetime import datetime

from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from characters import characters
from characters.task import Task
from utils import log_format, palette


class Character:
    def __init__(self, name):
        self.name = name
        self.task = None

        # These values are populated by the character yaml definitions.
        self.motivation = None
        self.format = None
        for k, v in characters.get(name, self).items():
            setattr(self, k, v)

    def set_task(self, name):
        self.task = Task(name)

    def chat(self, messages):
        response = ChatGPT.chat(messages)

        logging.info(
            f'{log_format.color(palette.material.indigo)}'
            f'{self.name.title().replace("_", " ")}'
            f'{log_format.reset()}: '
            f'{response}'
        )

        if config('ENABLE_SPEECH', cast=bool):
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'ElevenLabs'
                f'{log_format.reset()}: '
                f'Speech synthesis requested.'
            )
            Eleven.speak(response, f'saves/{self.name}/audio/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.wav')
        else:
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'ElevenLabs'
                f'{log_format.reset()}: '
                f'Speech synthesis is disabled. Skipping.'
            )

        return response
