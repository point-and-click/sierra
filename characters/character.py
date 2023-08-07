from datetime import datetime

from decouple import config

from characters.eleven import Eleven
from characters.open_ai import ChatGPT


class Character:
    def __init__(self, name):
        self.name = name

        self.eleven = Eleven(name)
        self.open_ai = ChatGPT(name)

        self.history = []

    def chat(self, message):
        response = self.open_ai.chat([{"role": "system", "content": f'{self.open_ai.role} {self.open_ai.format}'},
                                      *[{"role": "assistant", "content": entry} for entry in self.history],
                                      {"role": "user", "content": message}])
        self.history.append(response)

        if config('ENABLE_SPEECH', cast=bool):
            self.eleven.speak(response, f'saves/{self.name}/audio/{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.wav')

        return response
