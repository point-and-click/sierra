import logging
from enum import Enum

import openai
import whisper
from decouple import config

from utils.logging import log

TOKENS = 0


class MessageRole(Enum):
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'


class ChatGPT:
    @staticmethod
    def chat(messages):
        log.info('OpenAI: Chat completion requested.')

        try:
            completion = openai.ChatCompletion.create(model=config('OPENAI_CHAT_COMPLETION_MODEL'),
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_CHAT_COMPLETION_MAX_TOKENS', cast=int))

        except openai.error.TryAgain as err:
            logging.error(err)
            return

        try:
            return completion.choices[0].message.content, completion.usage
        except IndexError as err:
            logging.warning(err)
            return


class Whisper:
    @staticmethod
    def transcribe(audio_file):
        log.info('Whisper: Transcribing recorded audio.')
        model = whisper.load_model(config('OPENAI_WHISPER_MODEL'))
        result = model.transcribe(audio_file, fp16=False)
        return result["text"]
