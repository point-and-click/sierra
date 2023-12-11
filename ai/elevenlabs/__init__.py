import elevenlabs

from settings.secrets import Secrets

secrets = Secrets('ai/elevenlabs/secrets.yaml')
elevenlabs.set_api_key(secrets.get('api_key'))


class Eleven:
    @staticmethod
    def speak(text, voice, model):
        audio = elevenlabs.generate(text=text, voice=voice, model=model)
        return audio
