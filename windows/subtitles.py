import asyncio
from datetime import datetime

import pyglet

from settings import sierra
from windows import Window


def segment_as_label(segment):
    """
    `segment_as_label` function to convert a `Segment` into a `pyglet.text.Label`.
    :param segment:
    :return:
    """
    return pyglet.text.Label(segment.text, color=(255, 255, 255, 255), font_name='Arial', font_size=32, y=127,
                             anchor_y='top', multiline=True, width=1024)


class SubtitlesWindow(Window):
    """
    `SubtitlesWindow` class to represent a window for displaying subtitles.
    """
    def __init__(self, ):
        super().__init__('Subtitles', 1024, 128)
        red, green, blue = sierra.visual.chroma_key
        pyglet.gl.glClearColor(red, green, blue, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.segment = None

        @self.window.event
        def on_draw():
            """
            `on_draw` event to draw the window.
            """
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
        """
        `play` method to play the subtitles.
        :param subtitles: Subtitles
        """
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
