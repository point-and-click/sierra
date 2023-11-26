import wave

import pyaudio
from decouple import config


class Audio:
    def __init__(self, file_name):
        self.file_name = file_name
        self.py_audio = pyaudio.PyAudio()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def play_chunk(self):
        stream = self.py_audio.open(format=pyaudio.paInt16,
                                    channels=config('CHANNELS', cast=int),
                                    rate=config('SAMPLE_RATE', cast=int),
                                    output=True)

        with wave.open(self.file_name, 'rb') as wf:
            data = wf.readframes(config('CHUNK', cast=int))
            while data:
                stream.write(data)
                data = wf.readframes(config('CHUNK', cast=int))
                yield
