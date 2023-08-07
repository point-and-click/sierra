import logging

from decouple import config
import pyaudio
import wave

from pynput import keyboard

from utils import log_format, palette

RECORD_BINDING = keyboard.Key.ctrl_l


class Recorder:
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
            pass

        while self.recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

        self.stream.stop_stream()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        self.frames = []

    def on_press(self, key):
        if key == RECORD_BINDING and not self.recording:
            self.recording = True
            logging.info(
                f'{log_format.color(palette.material.red)}'
                f'Recording'
                f'{log_format.reset()}'
            )

    def on_release(self, key):
        if key == RECORD_BINDING and self.recording:
            self.recording = False
            logging.info(
                f'{log_format.color(palette.material.green)}'
                f'Recording Stopped'
                f'{log_format.reset()}'
            )
            self.listener.stop()
