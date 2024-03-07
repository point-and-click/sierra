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
from utils.logging import log

secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))


class Chat:
    client = OpenAI(api_key=secrets.get('api_key'))

    @staticmethod
    def send(prompt, session, character=None):
        messages = []
        if character:
            messages.append(
                {"role": ai.Role.SYSTEM.value, "content": character.personality.get('description')}
            )
            if character.task:
                messages.append(
                    {"role": ai.Role.USER.value,
                     "content": f'{character.task.description} {character.serialize_rules(RuleType.PERMANENT)}'}
                )
        if session.history.summary:
            messages.append(session.history.summary.serialize())
        if session.history.moments:
            messages.extend(
                [entry.serialize(character.name) for entry in session.history.get()]
            )
        messages.append(
            {"role": ai.Role.USER.value,
             "content": f'{character.serialize_rules(RuleType.TEMPORARY)} {prompt}'}
        )

        model = character.personality.get('model', settings.get('chat.model'))

        try:
            completion = Chat.client.chat.completions.create(model=model,
                                                             messages=messages,
                                                             max_tokens=settings.get('chat.tokens'))
        except RateLimitError as error:
            log.error(f'{error}: Retrying in 60 seconds.')
            sleep(60)
            return Chat.send(prompt, session, character)
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
    def send(audio_path):
        model = whisper.load_model(settings.get('transcribe.model'))
        return model.transcribe(audio_path, fp16=False, word_timestamps=True)
