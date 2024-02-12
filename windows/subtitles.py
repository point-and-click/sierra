import asyncio
from datetime import datetime

import pyglet

from settings import sierra_settings
from windows import Window


def segment_as_label(segment):
    return pyglet.text.Label(
        segment.text,
        color=(255, 255, 255, 255),
        font_name='Arial',
        font_size=32,
        x=0, anchor_x='left',
        y=128, anchor_y='top',
        multiline=True, width=1024
    )


class SubtitlesWindow(Window):
    def __init__(self, ):
        super().__init__('Subtitles', 1024, 128)
        red, green, blue = sierra_settings.visual.chroma_key
        pyglet.gl.glClearColor(red, green, blue, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.segment = None

        @self.window.event
        def on_draw():
            self.window.clear()
            try:
                if self.segment:
                    label = segment_as_label(self.segment)
                    outline = segment_as_label(self.segment)
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            if abs(dx) + abs(dy) != 0:
                                outline.x = label.x + dx
                                outline.y = label.y + dy
                                outline.color = (0, 0, 0, 255)
                                outline.draw()
                    label.draw()
            except (AttributeError, TypeError):
                pass

    async def play(self, subtitles):
        segment = iter(subtitles)
        self.segment = next(segment)

        segments_start = datetime.now()
        while self.segment:
            await asyncio.sleep(0.01)
            if self.segment.complete(segments_start, datetime.now()):
                try:
                    self.segment = next(segment)
                except StopIteration:
                    self.segment = None
                    break
