from datetime import datetime

import ai
from play import Character
from settings import sierra_settings as settings


class Output:
    def __init__(self, character: Character, audio_file):
        self.character = character
        self.audio = SpeakOutput(audio_file)
        self.subtitles = ai.modules.get(settings.transcribe.module).Transcribe.transcribe(self.audio.file_name)


class SpeakOutput:
    def __init__(self, file_bytes):
        self.file_bytes = file_bytes
        self.file_name = f'temp/{datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")}.mp3'
        with open(self.file_name, "wb") as audio_file:
            audio_file.write(self.file_bytes)
