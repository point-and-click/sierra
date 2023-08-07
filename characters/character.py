import logging
from datetime import datetime

from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from utils import log_format, palette


class Character:
    def __init__(self, name):
        self.name = name

        self.eleven = Eleven(name)
        self.chat_gpt = ChatGPT(name)

        self.history = []

    def chat(self, message):
        response = self.chat_gpt.chat([{"role": "system", "content": f'{self.chat_gpt.role} {self.chat_gpt.format}'},
                                       *[{"role": "assistant", "content": entry} for entry in self.history],
                                       {"role": "user", "content": message}])
        self.history.append(response)

        if config('ENABLE_SPEECH', cast=bool):
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'ElevenLabs'
                f'{log_format.reset()}: '
                f'Speech synthesis requested'
            )
            self.eleven.speak(response, f'saves/{self.name}/audio/{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.wav')
        else:
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'ElevenLabs'
                f'{log_format.reset()}: '
                f'Speech synthesis is disabled. Skipping.'
            )

        return response
