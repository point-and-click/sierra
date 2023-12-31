from os import path
import elevenlabs

from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets(path.join(*__name__.split('.'), 'secrets.yaml'))
settings = Settings(path.join(*__name__.split('.'), 'settings.yaml'))
elevenlabs.set_api_key(secrets.get('api_key'))


class Speak:
    @staticmethod
    def send(text, voice):
        audio = elevenlabs.generate(
            text=text,
            voice=voice,
            model=settings.get('voice.model'),
            output_format=settings.get('voice.output_format'),
        )
        return audio
