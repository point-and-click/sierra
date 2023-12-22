import elevenlabs

from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets('ai/elevenlabs/secrets.yaml')
settings = Settings('ai/elevenlabs/settings.yaml')
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
