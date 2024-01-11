from datetime import datetime

import ai
from play import Character
from settings import sierra_settings as settings


class Output:
    def __init__(self, _id, character: Character, audio_bytes, original_text):
        self.id = _id
        self.character = character
        self.audio = SpeakOutput(audio_bytes)
        self.original_text = original_text
        _, self.subtitles = ai.load(settings.transcribe.module, ai.Function.TRANSCRIBE)().send(self.audio.path)


class SpeakOutput:
    def __init__(self, audio_bytes):
        self.bytes = audio_bytes
        self.path = f'temp/{datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")}'
        with open(self.path, "wb") as audio_file:
            audio_file.write(self.bytes)
        try:
            with open('temp/output.wav', "wb") as audio_file:
                audio_file.write(self.bytes)
        except:
            pass
