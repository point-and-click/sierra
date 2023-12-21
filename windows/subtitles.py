import asyncio
from datetime import datetime, timedelta

import pyglet

from windows import Window


def segment_as_label(segment):
    return pyglet.text.Label(
        segment.text,
        color=(255, 255, 255, 255),
        font_name='Arial',
        font_size=32,
        x=0, anchor_x='left',
        y=128, anchor_y='top',
    )


class SubtitlesWindow(Window):
    def __init__(self, ):
        super().__init__('Subtitles', 1024, 128)
        pyglet.gl.glClearColor(0, 1, 0, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.segments = None
        self.current_segment = None

        @self.window.event
        def on_draw():
            self.window.clear()
            if self.segments:
                segment_as_label(self.segments[self.current_segment]).draw()

    async def play(self, segments):
        self.segments = [SubtitleSegment(segment) for segment in segments]
        self.current_segment = 0

        segments_start = datetime.now()
        while self.current_segment < len(self.segments):
            await asyncio.sleep(0.01)
            if self.segments[self.current_segment].complete(segments_start, datetime.now()):
                self.current_segment += 1

        self.segments = None


class SubtitleSegment:
    def __init__(self, segment):
        # Silence is handled weirdly by segments.
        self.text = segment.get('text', '')
        self.start = segment.get('start', 0)
        self.end = segment.get('end', 0)
        self.duration = self.end - self.start

    def complete(self, start_time, time):
        return start_time + timedelta(seconds=self.start) + timedelta(seconds=self.duration) <= time
