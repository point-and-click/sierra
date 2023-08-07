from decouple import config
import pyaudio
import wave

from pynput import keyboard

RECORD_BINDING = keyboard.Key.space


class Recorder:
    def __init__(self):
        self.chunk = config('CHUNK', cast=int)
        self.sample_format = pyaudio.paInt16
        self.channels = config('CHANNELS', cast=int)
        self.fs = config('FS', cast=int)

        self.interface = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

        self.primed = True
        self.recording = False

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def record(self, filename):
        self.stream = self.interface.open(channels=self.channels,
                                          rate=self.fs,
                                          format=self.sample_format,
                                          frames_per_buffer=self.chunk,
                                          input=True)

        self.listener.start()
        self.listener.join()

        self.stream.stop_stream()
        self.stream.close()
        self.interface.terminate()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.interface.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def on_press(self, key):
        if key == RECORD_BINDING and not self.recording:
            self.recording = True
            print('Recording')
        if key == RECORD_BINDING and self.recording:
            # TODO: Figure out this weird number
            for i in range(0, int(self.fs / self.chunk * 0.1)):
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)

    def on_release(self, key):
        if key == RECORD_BINDING and self.recording:
            self.recording = False
            print('Recording Stopped')
            self.listener.stop()
