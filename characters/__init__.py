import elevenlabs
import openai
import logging

import yaml
from decouple import config
from openai.error import TryAgain

with open("characters.yaml", "r") as stream:
    characters = yaml.safe_load(stream)


class Character:
    def __init__(self, name):
        self.chat_model = None
        self.voice_model = None
        self.voice = None

        self.role = None
        self.history = []

        for k, v in characters.get(name, self).items():
            setattr(self, k, v)

    def chat(self, message):
        try:
            messages = [{"role": "system", "content": self.role},
                        *[{"role": "assistant", "content": entry} for entry in self.history],
                        {"role": "user", "content": message}]

            completion = openai.ChatCompletion.create(model=self.chat_model,
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_MAX_TOKENS', cast=int))
        except TryAgain as err:
            logging.error(err)
            return

        try:
            response = completion.choices[0].message.content
            self.history.append(response)
        except IndexError as err:
            logging.warning(err)
            return

        try:
            audio = elevenlabs.generate(text=response, voice=self.voice, model=self.voice_model)
            elevenlabs.save(audio, 'test.wav')
            elevenlabs.play(audio)
        except ValueError as err:
            logging.error(err)
            return
