import whisper
from decouple import config

from utils.logging import log


class Whisper:
    @staticmethod
    def transcribe(audio_file):
        log.info('Whisper: Transcribing recorded audio.')
        model = whisper.load_model(config('OPENAI_WHISPER_MODEL'))
        result = model.transcribe(audio_file, fp16=False, word_timestamps=True)
        return result["text"]
