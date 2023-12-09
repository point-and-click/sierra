import asyncio
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
    def __init__(self, settings, interface, stream, recording, listener):
        self.settings = settings
        self.interface = interface
        self.stream = stream
        self.recording = recording
        self.listener = listener

    @classmethod
    async def create(cls):
        settings = InputSettings()

        interface = pyaudio.PyAudio()
        stream = interface.open(channels=settings.audio.channels,
                                rate=settings.audio.fs,
                                format=settings.audio.sample_format,
                                frames_per_buffer=settings.audio.chunk,
                                input=True)

        recording = cls._Status()

        listener = keyboard.Listener(on_press=cls.on_press, on_release=cls.on_release)
        return InputController(settings, interface, stream, recording, listener)

    def record(self, filename):
        self.listener.start()

        frames = []
        self.stream.start_stream()

        while not self.recording.status:
            time.sleep(0.1)

        while self.recording.status:
            data = self.stream.read(self.settings.audio.chunk, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()
        self.listener.stop()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.settings.audio.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.settings.audio.sample_format))
        wf.setframerate(self.settings.audio.fs)
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

        if number in self.settings.binds.keys() and not self.recording:
            self.recording.status = True
            self.recording.character = self.settings.binds.get(number).character
            log.info('input.py: Recording Started')

    def on_release(self, key):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number in self.settings.binds.keys() and self.recording:
            self.recording.status = False
            log.info('input.py: Recording Stopped')

    def collect(self):
        while True:
            log.info('\ninput.py: Press binds to record.')
            self.record('temp/input.wav')
            prompt = Whisper.transcribe('temp/input.wav')["text"]

            requests.post("http://localhost:8008/", json={"message": prompt, "character": self.recording.character})
            log.info(f'Whisper: Transcribed: {prompt}')

    class _Status:
        def __init__(self):
            self.status = False
            self.character = None


class InputSettings:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self._raw = safe_load(file)
        self.audio = Audio(self._raw.get('audio', {}))
        self.binds = {bind.vk: bind for bind in [Bind(bind) for bind in self._raw.get('binds', [])]}


async def collect():
    microphone_input = await InputController.create()
    microphone_input.collect()


if __name__ == "__main__":
    asyncio.run(collect())
