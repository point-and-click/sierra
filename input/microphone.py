import time
import wave

import pyaudio
import pygame
import requests
from decouple import config
from pynput import keyboard

from ai.audio.open_ai import Whisper
from utils.logging import log
from assets.audio.notifications import NOTIFY_RELEASE, NOTIFY_PRESS

assert (len(config('VK_BINDS').split(','))
        == len(config('CHARACTERS').split(','))), 'VK_BINDS and CHARACTERS must be the same length'
BIND_MAP = dict(zip(config('VK_BINDS').split(','), config('CHARACTERS').split(',')))  # NUM_0


class Input:
    def __init__(self):
        self.chunk = config('CHUNK', cast=int)
        self.sample_format = pyaudio.paInt16
        self.channels = config('CHANNELS', cast=int)
        self.fs = config('FS', cast=int)

        self.interface = pyaudio.PyAudio()
        self.stream = self.interface.open(channels=self.channels,
                                          rate=self.fs,
                                          format=self.sample_format,
                                          frames_per_buffer=self.chunk,
                                          input=True)
        self.frames = []

        self.recording = False
        self.listener = None

    def record(self, filename):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        self.stream.start_stream()

        while not self.recording:
            time.sleep(0.1)

        while self.recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

        self.stream.stop_stream()
        self.listener.stop()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.interface.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.frames))

        self.frames = []

    def on_press(self, key):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = 0

        if number in BIND_MAP.keys():
            pygame.mixer.Sound.play(NOTIFY_PRESS)
            self.recording = True
            log.info('input.py: Recording Started')

    def on_release(self, key):
        if isinstance(key, keyboard.Key):
            number = key.value.vk
        elif isinstance(key, keyboard.KeyCode):
            number = key.vk
        else:
            number = 0

        if number in BIND_MAP.keys() and self.recording:
            pygame.mixer.Sound.play(NOTIFY_RELEASE)
            self.recording = False
            log.info('input.py: Recording Stopped')

    def run(self):
        while True:
            log.info(f'\ninput.py: Press any VK_BIND to record.')
            self.record('temp/input.wav')
            prompt = Whisper.transcribe('temp/input.wav')

            requests.post(
                "http://localhost:8008/",
                json={
                    "message": prompt,
                    "character": "Other Poop"
                }
            )
            log.info(f'Whisper: Transcribed: {prompt}')


if __name__ == "__main__":
    pygame.init()
    recorder = Input()
    recorder.run()
