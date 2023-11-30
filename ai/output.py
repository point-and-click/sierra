from datetime import datetime

from ai.open_ai import Whisper
from play import Character


class AiOutput:

    def __init__(self, character: Character, audio_file):
        self.character = character
        self.audio = OutputAudio(audio_file)
        self.subtitles = Whisper.transcribe(self.audio.file_name)


class OutputAudio:
    def __init__(self, file_bytes):
        self.file_bytes = file_bytes
        self.file_name = f'temp/{datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")}.mp3'
        with open(self.file_name, "wb") as audio_file:
            audio_file.write(self.file_bytes)
