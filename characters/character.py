from datetime import datetime

from characters.eleven import Eleven
from characters.open_ai import OpenAI


class Character:
    def __init__(self, name):
        self.name = name

        self.eleven = Eleven(name)
        self.open_ai = OpenAI(name)

        self.history = []

    def chat(self, message):
        response = self.open_ai.chat([{"role": "system", "content": self.open_ai.role},
                                      *[{"role": "assistant", "content": entry} for entry in self.history],
                                      {"role": "user", "content": message}])
        self.history.append(response)

        self.eleven.speak(response, f'saves/{self.name}/audio/{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.wav')

        return response
