import logging
from enum import Enum

import openai
from decouple import config

from utils.logging import log


class MessageRole(Enum):
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'


class ChatGPT:
    @staticmethod
    def chat(messages, chat_model_override=None):
        log.info('OpenAI: Chat completion requested.')

        if chat_model_override is not None:
            model = chat_model_override
        else:
            model = config('OPENAI_CHAT_COMPLETION_MODEL')

        try:
            completion = openai.ChatCompletion.create(model=model,
                                                      messages=messages,
                                                      max_tokens=config('OPENAI_CHAT_COMPLETION_MAX_TOKENS', cast=int))

        except openai.error.TryAgain as err:
            logging.error(err)
            return
        except openai.error.Timeout as err:
            logging.error(err)
            ChatGPT.chat(messages)
            return

        try:
            return completion.choices[0].message.content, completion.usage
        except IndexError as err:
            logging.warning(err)
            return
