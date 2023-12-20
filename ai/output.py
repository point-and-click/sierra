from datetime import datetime
from enum import Enum

import ai
from play import Character
from settings import sierra_settings as settings


class Output:
    def __init__(self, character: Character, audio_bytes):
        self.character = character
        self.audio = SpeakOutput(audio_bytes)
        self.subtitles = ai.load(settings.transcribe.module, ai.Function.TRANSCRIBE)().send(self.audio.path)


class SpeakOutput:
    def __init__(self, audio_bytes):
        self.bytes = audio_bytes
        self.path = f'temp/{datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")}'
        with open(self.path, "wb") as audio_file:
            audio_file.write(self.bytes)
