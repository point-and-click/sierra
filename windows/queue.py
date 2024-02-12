import pyglet
from pyglet import shapes

from play import Play
from settings import sierra_settings
from utils.format import truncate
from windows import Window


def text_as_label(text):
    return pyglet.text.Label(
        text,
        color=(255, 255, 255, 255),
        font_name='Arial',
        font_size=16,
        x=58, anchor_x='left',
        anchor_y='center',
        multiline=False,
        width=(512 - 58)
    )


palette = {
    "twitch": (100, 65, 165),
    "microphone": (0, 114, 178)
}


def path_as_sprite(path):
    image = pyglet.resource.image(path)
    image.anchor_y = image.height / 2
    sprite = pyglet.sprite.Sprite(image)
    sprite.width = 32
    sprite.height = 32
    sprite.x = 32
    return sprite


class QueueWindow(Window):
    def __init__(self):
        super().__init__('Input Queue', 512, 1080)
        red, green, blue = sierra_settings.visual.chroma_key
        pyglet.gl.glClearColor(red, green, blue, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.panels = []

        @self.window.event
        def on_draw():
            self.window.clear()
            if self.panels:
                if len(self.panels) == 2:
                    pass
                for i, panel in enumerate(self.panels):
                    border_color = tuple(int(value * 0.5) for value in palette.get(panel.source))
                    rectangle = shapes.BorderedRectangle(width=512, height=62, x=0, y=self.window.height - 66 - i * 70,
                                                         color=palette.get(panel.source), border=3,
                                                         border_color=border_color)
                    rectangle.draw()
                    sprite = path_as_sprite(panel.image_path)
                    sprite.y = self.window.height - i * 70 - 32
                    sprite.draw()
                    label = text_as_label(panel.message)
                    label.y = self.window.height - i * 70 - 32
                    outline = text_as_label(panel.message)
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if abs(dx) + abs(dy) != 0:
                                outline.x = label.x + dx
                                outline.y = label.y + dy
                                outline.color = (0, 0, 0, 255)
                                outline.draw()
                    label.draw()

    def add_panel(self, _input):
        self.panels.append(self._QueuePanel(_input))

    def remove_panel(self, _id):
        self.panels = [panel for panel in self.panels if panel.id != _id]

    class _QueuePanel:
        def __init__(self, _input):
            self.id = _input.id
            self.image_path = Play.characters().get(
                _input.character
            ).path.replace(
                "\\", "/"
            ) + '/' + Play.characters().get(
                _input.character).image
            self.source = _input.source
            self.message = truncate(_input.message, 60)
