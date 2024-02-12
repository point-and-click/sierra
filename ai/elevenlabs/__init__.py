from os import path
import elevenlabs

from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))
elevenlabs.set_api_key(secrets.get('api_key'))


class Speak:
    @staticmethod
    def send(text: str, voice: dict) -> tuple[bytes, str]:
        _voice = elevenlabs.Voice(
            voice_id=voice.get('voice_id', 'EXAVITQu4vr4xnSDxMaL'),
            name=voice.get('name', 'Bella'),
            settings=elevenlabs.VoiceSettings(
                stability=voice.get('stability', 0.71),
                similarity_boost=voice.get('similarity_boost', 0.5),
                style=voice.get('style', 0.0),
                use_speaker_boost=voice.get('user_speaker_boost', True)
            )
        )

        audio = elevenlabs.generate(
            text=text,
            voice=_voice,
            model=voice.get('model', 'eleven_multilingual_v2'),
            output_format=settings.get('voice.output_format')
        )
        return audio, settings.get('voice.output_file_type')
