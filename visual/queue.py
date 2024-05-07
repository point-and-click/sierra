import pyglet
from pyglet import shapes

from play import Play
from settings import sierra
from utils.format import truncate
from windows import Window

sprite_dimension = 32
text_offset = 58

palette = {
    "twitch": (100, 65, 165),
    "microphone": (0, 114, 178),
    "keyboard": (0, 158, 115),
}

border_palette = {key: tuple(int(v * 0.5) for v in value) for key, value in palette.items()}


def text_as_label(text):
    """

    :param text: str
    :return: pyglet.text.Label
    """
    return pyglet.text.Label(text, color=(255, 255, 255, 255), font_name='Arial', font_size=16, x=text_offset,
                             anchor_y='center', width=512 - text_offset)


def path_as_sprite(path):
    """

    :param path: str
    :return: pyglet.sprite.Sprite
    """
    image = pyglet.resource.image(path)
    image.anchor_y = image.height / 2
    sprite = pyglet.sprite.Sprite(image)
    sprite.width = sprite_dimension
    sprite.height = sprite_dimension
    sprite.x = sprite_dimension
    return sprite


class QueueWindow(Window):
    """
    `QueueWindow` class to represent a window for displaying the queue.
    """
    def __init__(self):
        super().__init__('Queue', 512, 1024)
        red, green, blue = sierra.visual.chroma_key
        pyglet.gl.glClearColor(red, green, blue, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.panels = []

        @self.window.event
        def on_draw():
            """
            `on_draw` event to draw the window.
            """
            self.window.clear()
            if self.panels:
                if len(self.panels) == 2:
                    pass
                for i, panel in enumerate(self.panels):
                    rectangle = shapes.BorderedRectangle(
                        width=self.window.width, height=panel.height,
                        x=0, y=self.window.height - panel.initial_offset - i * panel.additional_offset,
                        color=palette.get(panel.source),
                        border_color=border_palette.get(panel.source),
                        border=panel.border
                    )
                    rectangle.draw()
                    sprite = path_as_sprite(panel.image_path)
                    sprite.y = self.window.height - i * panel.additional_offset - sprite_dimension
                    sprite.draw()
                    label = text_as_label(panel.message)
                    label.y = self.window.height - i * panel.additional_offset - sprite_dimension
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
        """
        `add_panel` method to add a panel to the window.
        :param _input: Input
        """
        self.panels.append(self._QueuePanel(_input))

    def remove_panel(self, _id):
        """
        `remove_panel` method to remove a panel from the window.
        :param _id: str
        """
        self.panels = [panel for panel in self.panels if panel.id != _id]

    class _QueuePanel:
        height = 62
        border = 3
        initial_offset = height + border + 1
        additional_offset = height + 2 * (border + 1)

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
