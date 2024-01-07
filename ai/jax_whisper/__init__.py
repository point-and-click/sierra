from os import path

import jax.numpy as jnp
from whisper_jax import FlaxWhisperPipline

from play.subtitles import Subtitles
from settings.settings import Settings
from utils.logging import log

settings = Settings(path.join(*__name__.split('.'), 'settings.yaml'))


class Transcribe:
    @staticmethod
    def send(audio_path):
        log.info('Whisper: Transcribing recorded audio.')
        pipeline = FlaxWhisperPipline(settings.get('transcribe.model'), dtype=jnp.bfloat16)
        result = pipeline(audio_path, task='transcribe', return_timestamps=True)
        subtitles = Subtitles([(chunk.get('text'), chunk.get('timestamp')[0], chunk.get('timestamp')[1]) for chunk in result.get('chunks')])
        text = result.get('text')
        return text, subtitles
