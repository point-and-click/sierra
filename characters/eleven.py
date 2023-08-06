from datetime import datetime
from time import strftime

import elevenlabs

from characters import characters


class Eleven:
    def __init__(self, name):
        self.voice_model = None
        self.voice = None

        for k, v in characters.get(name, self).get('eleven').items():
            setattr(self, k, v)

    def speak(self, text, file_name):
        audio = elevenlabs.generate(text=text, voice=self.voice, model=self.voice_model)
        elevenlabs.save(audio, file_name)
        elevenlabs.play(audio)
