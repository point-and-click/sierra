from os import path
from time import sleep

# noinspection PyPackageRequirements
import whisper
from openai import (
    OpenAI,
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
    APIResponseValidationError,
)

import ai
from play.rules import RuleType
from settings.secrets import Secrets
from settings.settings import Settings
from settings import sierra_settings
from utils.logging import log

secrets = Secrets(path.join(*__name__.split('.'), 'secrets.yaml'))
settings = Settings(path.join(*__name__.split('.'), 'settings.yaml'))


class Chat:
    client = OpenAI(api_key=secrets.get('api_key'))

    @staticmethod
    def send(prompt, character, task, history, summary, chat_model_override=None):
        messages = [
            {"role": ai.Role.SYSTEM.value, "content": character.motivation}
        ]
        if summary:
            messages.append(
                {"role": summary.role, "content": summary.content}
            )
        if task and character:
            messages.append(
                {"role": ai.Role.USER.value,
                 "content": f'{task.description} {character.serialize_rules(RuleType.PERMANENT)}'}
            )
        if len(history) > 0:
            messages.extend(
                [{"role": entry.role, "content": entry.content} for entry in history[-sierra_settings.history.max:]]
            )
        messages.append(
            {"role": ai.Role.USER.value,
             "content": f'{character.serialize_rules(RuleType.TEMPORARY)} {prompt}'}
        )

        model = chat_model_override if chat_model_override else settings.get('chat.model')

        try:
            log.info('OpenAI: Chat completion requested.')
            completion = Chat.client.chat.completions.create(model=model,
                                                             messages=messages,
                                                             max_tokens=settings.get('chat.tokens'))
        except RateLimitError as error:
            log.error(f'{error}: Retrying in 60 seconds.')
            sleep(60)
            return Chat.send(prompt, character, task, history, summary, chat_model_override)
        except (APIError, OpenAIError, ConflictError, NotFoundError, APIStatusError, APITimeoutError,
                BadRequestError, APIConnectionError, AuthenticationError, InternalServerError, PermissionDeniedError,
                UnprocessableEntityError, APIResponseValidationError) as error:
            log.error(error)
            return

        try:
            return completion.choices[0].message.content
        except IndexError as error:
            log.warning(error)
            return


class Transcribe:
    @staticmethod
    def send(audio_bytes):
        log.info('Whisper: Transcribing recorded audio.')
        model = whisper.load_model(settings.get('transcribe.model'))
        result = model.transcribe(audio_bytes, fp16=False, word_timestamps=True)
        return result
