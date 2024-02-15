from os import path

from api import TextToSpeech
from utils.audio import load_audio

from settings.settings import Settings

settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))


class Speak:
    @staticmethod
    def send(text: str, voice: dict) -> tuple[bytes, str]:
        tts = TextToSpeech(
            use_deepspeed=settings.get('use_deepseed', True),
            kv_cache=settings.get('kv_cache', True),
            half=settings.get('half', True),
            k=1
        )
        gen = tts.tts_with_preset(
            text,
            voice_samples=[
                load_audio(clip, settings.get('sampling_rate', 24000))
                for clip in settings.get('clip_paths', [])
            ],
            preset=settings.get('preset', 'fast')
        )

        torchaudio.save('temp/tortoise.wav', gen.squeeze(0).cpu(), settings.get('sampling_rate', 24000))

        with open('temp/tortoise.wav', 'rb') as tortoise_file:
            tortoise_bytes = tortoise_file.read()
        return tortoise_bytes, 'wav'
