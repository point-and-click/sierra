import time
import wave

import pyaudio
import requests
from pynput import keyboard
from yaml import safe_load

from ai.open_ai import Whisper
from input.microphone.config import Bind, Audio
from utils.logging import log


class InputController:
    def __init__(self):
        self.config = InputConfig()

        self.interface = pyaudio.PyAudio()
        self.stream = self.interface.open(channels=self.config.audio.channels,
                                          rate=self.config.audio.fs,
                                          format=self.config.audio.sample_format,
                                          frames_per_buffer=self.config.audio.chunk,
                                          input=True)

        self.recording = self._Status()

        self.listener = None

    def record(self, filename):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        frames = []
        self.stream.start_stream()

        while not self.recording.status:
            time.sleep(0.1)

        while self.recording.status:
            data = self.stream.read(self.config.audio.chunk, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()
        self.listener.stop()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.config.audio.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.config.audio.sample_format))
        wf.setframerate(self.config.audio.fs)
        wf.writeframes(b''.join(frames))
        wf.close()

    def on_press(self, key):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number in self.config.binds.keys() and not self.recording:
            self.recording.status = True
            self.recording.character = self.config.binds.get(number).character
            log.info('input.py: Recording Started')

    def on_release(self, key):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number in self.config.binds.keys() and self.recording:
            self.recording.status = False
            log.info('input.py: Recording Stopped')

    def collect(self):
        while True:
            log.info(f'\ninput.py: Press binds to record.')
            self.record('temp/input.wav')
            prompt = Whisper.transcribe('temp/input.wav')["text"]

            requests.post("http://localhost:8008/", json={"message": prompt, "character": self.recording.character})
            log.info(f'Whisper: Transcribed: {prompt}')

    class _Status:
        def __init__(self):
            self.status = False
            self.character = None


class InputConfig:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self._raw = safe_load(file)
        self.audio = Audio(self._raw.get('audio', {}))
        self.binds = {bind.vk: bind for bind in [Bind(bind) for bind in self._raw.get('binds', [])]}


if __name__ == "__main__":
    microphone_input = InputController()
    microphone_input.collect()
