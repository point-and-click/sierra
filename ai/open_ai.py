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
            log.error(err)
            return
        except openai.error.Timeout as err:
            log.error(err)
            ChatGPT.chat(messages)
            return

        try:
            return completion.choices[0].message.content, completion.usage
        except IndexError as err:
            log.warning(err)
            return

    @staticmethod
    def fine_tune(json_file_path):
        file = openai.File.create(
            file=open(json_file_path, "rb"),
            purpose='fine-tune'
        )

        job = openai.FineTune.create(training_file=file.openai_id, model="gpt-3.5-turbo")

        log.info(job)

    @staticmethod
    def list_jobs():
        response = openai.FineTune.list(limit=10)
        log.info(response)


class Whisper:
    @staticmethod
    def transcribe(audio_file):
        log.info('Whisper: Transcribing recorded audio.')
        model = whisper.load_model(config('OPENAI_WHISPER_MODEL'))
        result = model.transcribe(audio_file, fp16=False, word_timestamps=True)
        return result
