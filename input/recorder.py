import time
import wave

import pyaudio
import pygame
import requests
from decouple import config
from pynput import keyboard

from ai.open_ai import Whisper
from utils.logging import log
from utils.pygame_manager import NOTIFY_RELEASE, NOTIFY_PRESS

RECORD_BINDING = 96  # NUM_0


class Recorder:
    def __init__(self):
        self.character_count = len(config('CHARACTERS').split(','))
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
        self.press_sound = None
        self.release_sound = None
        self.character_number = None

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

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        self.frames = []

    def on_press(self, key):
        if isinstance(key, keyboard.Key):
            number = key.value.vk
        elif isinstance(key, keyboard.KeyCode):
            number = key.vk
        else:
            number = 0

        if RECORD_BINDING <= number < RECORD_BINDING + self.character_count and not self.recording:
            self.character_number = number - RECORD_BINDING
            pygame.mixer.Sound.play(NOTIFY_PRESS)
            self.recording = True
            log.info('input.py: Recording Started')

    def on_release(self, key):
        if self.character_number is None:
            return

        if isinstance(key, keyboard.Key):
            number = key.value.vk
        elif isinstance(key, keyboard.KeyCode):
            number = key.vk
        else:
            number = 0

        if number == RECORD_BINDING + self.character_number and self.recording:
            pygame.mixer.Sound.play(NOTIFY_RELEASE)
            self.recording = False
            log.info('input.py: Recording Stopped')

    def run(self):
        while True:
            log.info(f'\ninput.py: Press {str(RECORD_BINDING)} to record.')
            self.record('temp/input.wav')
            prompt = Whisper.transcribe('temp/input.wav')["text"]
            if self.character_number == 0:
                character = "Other Poop"
            elif self.character_number == 1:
                character = "B"
            else:
                character = "God"

            requests.post("http://localhost:8008/", json={"message": prompt, "character": character})
            log.info(f'Whisper: Transcribed: {prompt}')


if __name__ == "__main__":
    recorder = Recorder()
    recorder.run()
