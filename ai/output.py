from datetime import datetime
from enum import Enum

import ai
from play import Character
from settings import sierra_settings as settings


class Output:
    def __init__(self, character: Character, audio_file):
        self.character = character
        self.audio = SpeakOutput(audio_file)
        # self.subtitles = ai.modules.get(settings.transcribe.module).Transcribe.transcribe(self.audio.file_name)


class SpeakOutput:
    def __init__(self, audio_bytes, audio_type):
        self.bytes = audio_bytes
        self.path = f'temp/{datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")}'
        with open(self.path, "wb") as audio_file:
            audio_file.write(self.bytes)
