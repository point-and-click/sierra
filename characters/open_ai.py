import logging

import openai
import whisper
from decouple import config

from characters import characters


class ChatGPT:
    def __init__(self, name):
        self.chat_model = None
        self.role = None
        self.format = None

        for k, v in characters.get(name, self).get('open_ai').items():
            setattr(self, k, v)

    def chat(self, messages):
        logging.info('OpenAI: Chat Completion Requested')
        try:
            completion = openai.ChatCompletion.create(model=self.chat_model,
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_MAX_TOKENS', cast=int))
        except openai.error.TryAgain as err:
            logging.error(err)
            return

        try:
            return completion.choices[0].message.content
        except IndexError as err:
            logging.warning(err)
            return


class Whisper:
    def __init__(self):
        self.model = 'base'

    def transcribe(self, audio_file):
        model = whisper.load_model(self.model)
        result = model.transcribe(audio_file)
        return result["text"]
