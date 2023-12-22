import asyncio
import time
import wave

import pyaudio
from pynput import keyboard
from yaml import safe_load

import ai
from input import chat
from input.microphone.config import Bind, Audio
from settings import sierra_settings as settings
from utils.logging import log


class InputController:
    def __init__(self):
        self.settings = InputSettings()

        self.interface = pyaudio.PyAudio()
        self.stream = self.interface.open(channels=self.settings.audio.channels,
                                          rate=self.settings.audio.fs,
                                          format=self.settings.audio.sample_format,
                                          frames_per_buffer=self.settings.audio.chunk,
                                          input=True)

        self.recording = self._Status()

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def record(self, filename):
        frames = []
        self.stream.start_stream()

        while not self.recording.status:
            time.sleep(0.1)

        while self.recording.status:
            data = self.stream.read(self.settings.audio.chunk, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.settings.audio.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.settings.audio.sample_format))
        wf.setframerate(self.settings.audio.fs)
        wf.writeframes(b''.join(frames))
        wf.close()

    def on_press(self, key: keyboard.Key | keyboard.KeyCode):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number in self.settings.binds.keys() and not self.recording.status:
            self.recording.status = True
            self.recording.character = self.settings.binds.get(number).character
            log.info('input.py: Recording Started')

    def on_release(self, key: keyboard.Key | keyboard.KeyCode):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number in self.settings.binds.keys() and self.recording.status:
            self.recording.status = False
            log.info('input.py: Recording Stopped')

    def collect(self):
        while True:
            log.info('\ninput.py: Press binds to record.')
            self.record('temp/input.wav')
            prompt = ai.load(settings.transcribe.module, ai.Function.TRANSCRIBE)().send('temp/input.wav')['text']

            chat.submit(prompt, self.recording.character)
            log.info(f'Whisper: Transcribed: {prompt}')

    class _Status:
        def __init__(self):
            self.status = False
            self.character = None


class InputSettings:
    def __init__(self):
        with open('input/microphone/config.yaml', 'r') as file:
            self._raw = safe_load(file)
        self.audio = Audio(self._raw.get('audio', {}))
        self.binds = {bind.vk: bind for bind in [Bind(bind) for bind in self._raw.get('binds', [])]}


async def collect():
    microphone_input = InputController()
    microphone_input.collect()


if __name__ == "__main__":
    asyncio.run(collect())
