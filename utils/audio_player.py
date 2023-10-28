import traceback

import numpy as np
import pyaudio
import audioread
from decouple import config


class AudioPlayer:
    def __init__(self, file_bytes):
        self.py_audio = pyaudio.PyAudio()
        self.file_bytes = file_bytes

    def __enter__(self):
        self.file = open('temp/output.wav', 'wb')
        self.file.write(self.file_bytes)
        self.file.seek(0)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.file.close()
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            # return False # uncomment to pass exception through

        return True

    def play_audio_chunk(self):
        stream = self.py_audio.open(format=pyaudio.paInt16,
                                    channels=config('CHANNELS', cast=int),
                                    rate=config('SAMPLE_RATE', cast=int),
                                    output=True)

        with audioread.audio_open(self.file.name) as f:
            for buf in f:
                audio_array = np.frombuffer(buf, dtype=np.int16)
                stream.write(audio_array.tobytes())
                yield np.max(np.abs(audio_array))
