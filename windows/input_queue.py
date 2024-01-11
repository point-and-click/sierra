import pyglet
from pyglet import shapes

from play import Play
from settings import sierra_settings
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


pallet = {
    "Twitch": (100, 65, 165),
    "Microphone": (0, 114, 178)
}


def path_as_sprite(path):
    image = pyglet.resource.image(path)
    image.anchor_y = image.height / 2
    sprite = pyglet.sprite.Sprite(image)
    sprite.width = 32
    sprite.height = 32
    sprite.x = 32
    return sprite


class InputQueueWindow(Window):
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
            if len(self.panels) > 0:
                if len(self.panels) == 2:
                    pass
                for i, panel in enumerate(self.panels):
                    border_color = tuple(int(value * 0.5) for value in pallet.get(panel.source))
                    rectangle = shapes.BorderedRectangle(width=512, height=62, x=0, y=self.window.height - 66 - i * 70,
                                                         color=pallet.get(panel.source), border=3,
                                                         border_color=border_color)
                    rectangle.draw()
                    sprite = path_as_sprite(panel.image_path)
                    sprite.y = self.window.height - i * 70 - 32
                    sprite.draw()
                    label = text_as_label(panel.text)
                    label.y = self.window.height - i * 70 - 32
                    outline = text_as_label(panel.text)
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if abs(dx) + abs(dy) != 0:
                                outline.x = label.x + dx
                                outline.y = label.y + dy
                                outline.color = (0, 0, 0, 255)
                                outline.draw()
                    label.draw()

    def add_panel(self, _id, character_name, text, source):
        self.panels.append(self._InputQueuePanel(_id, character_name, text, source))

    def remove_panel(self, _id):
        self.panels = [panel for panel in self.panels if panel.id != _id]

    class _InputQueuePanel:
        def __init__(self, _id, character_name, text, source):
            self.id = _id
            self.image_path = Play.characters().get(character_name).path.replace("\\",
                                                                                 "/") + '/' + Play.characters().get(
                character_name).image
            self.source = source
            self.text = f'{text[:45]}'
            if len(text) > 45:
                self.text += '...'
