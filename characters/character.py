import logging
from datetime import datetime

from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from utils import log_format, palette


class Character:
    def __init__(self, name):
        self.name = name

        self.tts = Eleven(name)
        self.chat_gpt = ChatGPT(name)

    def chat(self, message):
        response = self.chat_gpt.chat(message)

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
            self.tts.speak(response, f'saves/{self.name}/audio/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.wav')
        else:
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'ElevenLabs'
                f'{log_format.reset()}: '
                f'Speech synthesis is disabled. Skipping.'
            )

        return response
