from os import path

from anthropic import Anthropic

import ai
from play.rules import RuleType
from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))


class Chat:
    client = Anthropic(
        api_key=secrets.get("api_key"),
    )

    @staticmethod
    def send(prompt, session, character=None):
        """
        :param prompt:
        :param session:
        :param character:
        """
        messages = []
        system = None
        if character:
            system = character.personality.get('description')
            if character.task:
                system += f'{character.task.description} {character.serialize_rules(RuleType.PERMANENT)}'
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

        message = Chat.client.messages.create(
            model=model,
            system=system,
            max_tokens=settings.get("max_tokens", 128),
            messages=messages
        )

        return message.content[0].text
