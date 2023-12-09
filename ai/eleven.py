import elevenlabs
from decouple import config


class Eleven:
    @staticmethod
    def speak(text, voice):
        audio = elevenlabs.generate(text=text, voice=voice, model=config('ELEVENLABS_MODEL'))
        return audio
