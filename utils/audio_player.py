import audioread
import numpy as np
import pyaudio


class AudioPlayer:
    def __init__(self, output_audio):
        self.py_audio = pyaudio.PyAudio()
        self.output = output_audio

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def play_audio_chunk(self):
        stream = self.py_audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=24000,
                                    output=True)

        with audioread.audio_open(self.output.audio.file_name) as f:
            for buf in f:
                audio_array = np.frombuffer(buf, dtype=np.int16)
                stream.write(audio_array.tobytes())
                yield np.max(np.abs(audio_array))
