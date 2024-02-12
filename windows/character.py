import asyncio
import time

import pyglet
from audioread import audio_open
from numpy import frombuffer, abs, max, int16
from pyaudio import PyAudio, paInt16

from settings import sierra_settings
from windows import Window
from windows.animation.rotate import RotateAnimation


class CharacterWindow(Window):
    def __init__(self, character):
        super().__init__(character.name, 512, 512)
        red, green, blue = sierra_settings.visual.chroma_key
        pyglet.gl.glClearColor(red, green, blue, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.character = character
        self._image = pyglet.resource.image(f'{character.path}/{character.image}')
        self.sprite = pyglet.sprite.Sprite(self._image)
        self.animation = RotateAnimation(sierra_settings.visual.animation)
        self._angle = 0
        self.hidden = True

        self.paused = False

        @self.window.event
        def on_draw():
            self.window.clear()
            if not self.hidden:
                self.sprite.rotation = self._angle
                self.sprite.draw()

    async def speak(self, speech):
        for amplitude in self._play_audio_chunk(speech):
            while self.paused:
                time.sleep(0.1)
            self._angle = self.animation.render(amplitude)
            await asyncio.sleep(0.01)
        self._angle = 0

    def _play_audio_chunk(self, audio):
        stream = PyAudio().open(
            format=paInt16,
            channels=sierra_settings.speech.channels,
            rate=sierra_settings.speech.sample_rate,
            output=True
        )

        with audio_open(audio.path) as audio_file:
            self.hidden = False
            for buffer in audio_file:
                audio_array = frombuffer(buffer, dtype=int16)
                stream.write(audio_array.tobytes())
                yield max(abs(audio_array))
            self.hidden = True
