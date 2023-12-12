import openai
# noinspection PyPackageRequirements
import whisper
from openai import (
    APIError,
    OpenAIError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    UnprocessableEntityError,
    APIResponseValidationError
)

import ai
from settings.secrets import Secrets
from settings.settings import Settings
from settings import sierra_settings
from utils.logging import log


class Chat:
    @staticmethod
    def send(prompt, character, task, history, summary, chat_model_override=None):
        messages = [
            {"role": ai.Role.SYSTEM.value,
             "content": 'You will be playing the part of multiple characters. Respond as the character described.'},
            {"role": ai.Role.USER.value,
             "content": f'{task.description} {character.motivation} {character.rules}'},
            {"role": summary.role, "content": summary.content},
            *[{"role": entry.role, "content": entry.content} for entry in history[-sierra_settings.history.max:]],
            {"role": ai.Role.USER.value,
             "content": f'{" ".join([rule.text for rule in character.user_rules])} {prompt}'}
        ]
        log.info('OpenAI: Chat completion requested.')

        if chat_model_override is not None:
            model = chat_model_override
        else:
            model = settings.get('chat.model')

        try:
            completion = openai.ChatCompletion.create(model=model,
                                                      messages=messages,
                                                      max_tokens=settings.get('chat.tokens'))

        except (APIError, OpenAIError, ConflictError, NotFoundError, APIStatusError, RateLimitError, APITimeoutError,
                BadRequestError, APIConnectionError, AuthenticationError, InternalServerError, PermissionDeniedError,
                UnprocessableEntityError, APIResponseValidationError) as error:
            log.error(error)
            return

        try:
            return completion.choices[0].message.content, completion.usage
        except IndexError as error:
            log.warning(error)
            return


class Transcribe:
    @staticmethod
    def send(audio_file):
        log.info('Whisper: Transcribing recorded audio.')
        model = whisper.load_model(settings.get('transcribe.model'))
        result = model.transcribe(audio_file, fp16=False, word_timestamps=True)
        return result


secrets = Secrets('ai/open_ai/secrets.yaml')
settings = Settings('ai/open_ai/settings.yaml')

openai.api_key = secrets.get('api_key')
