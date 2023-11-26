import elevenlabs
from decouple import config


class Eleven:
    @staticmethod
    def speak(text, voice, file_name=None):
        audio = elevenlabs.generate(text=text, voice=voice, model=config('ELEVENLABS_MODEL'))
        # if file_name:
        #     elevenlabs.save(audio, file_name)
        # elevenlabs.play(audio)
        return audio
