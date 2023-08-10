import logging

import openai
import whisper
from decouple import config

from characters import characters
from utils import log_format, palette


class ChatGPT:
    def __init__(self, name):
        self.chat_model = None
        self.role = None
        self.format = None
        self.summary = None
        self.history = []

        for k, v in characters.get(name, self).get('chat_gpt').items():
            setattr(self, k, v)

    def chat(self, message):
        logging.info(f'{log_format.color(palette.material.cyan)}'
                     f'OpenAI'
                     f'{log_format.reset()}: '
                     f'Chat completion requested.')

        messages = [{"role": "system", "content": f'{self.role} {self.format}'},
                    *[{"role": "user", "content": entry} for entry in self.history],
                    {"role": "user", "content": message}]
        try:
            completion = openai.ChatCompletion.create(model=self.chat_model,
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_MAX_TOKENS', cast=int))
        except openai.error.TryAgain as err:
            logging.error(err)
            return

        try:
            response = completion.choices[0].message.content
            self.history.append(message)
            self.summarize()
            return response
        except IndexError as err:
            logging.warning(err)
            return

    def summarize(self):
        history_word_count = sum([len(entry.split()) for entry in self.history])
        word_count = (len(self.format.split())
                      + len(self.role.split())
                      + history_word_count)

        logging.info(
            f'{log_format.color(palette.material.gray)}'
            f'History Word Count: '
            + str(word_count))

        if word_count < config("OPENAI_HISTORY_MAX_WORD_COUNT", cast=int):
            return

        messages = [{"role": "system", "content": "Summarize the following messages. Be as concise as possible. "
                                                  "Place emphasis on your primary objective, current goal, and any "
                                                  "items: in your inventory, or in the world and their locations"},
                    *[{"role": "assistant", "content": entry} for entry in self.history]]

        try:
            completion = openai.ChatCompletion.create(model=self.chat_model,
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_MAX_TOKENS', cast=int))

            response = completion.choices[0].message.content
            self.history = [response]

            logging.info(
                f'{log_format.color(palette.material.gray)}'
                f'Summary: '
                + response
            )
        except openai.error.TryAgain as err:
            logging.error(err)
            return

        return


class Whisper:
    def __init__(self):
        self.model = 'base'

    def transcribe(self, audio_file):
        model = whisper.load_model(self.model)
        result = model.transcribe(audio_file, fp16=False)
        return result["text"]
