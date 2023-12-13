import pyglet

from windows import Window


class CharacterWindow(Window):
    def __init__(self, character):
        super().__init__(character.name, 512, 512)
        pyglet.gl.glClearColor(0, 1, 0, 1)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.character = character
        self.image = pyglet.resource.image(f'{character.path}/{character.image}')
        self.hidden = True

        @self.window.event
        def on_draw():
            self.window.clear()
            if not self.hidden:
                self.image.blit(0, 0)
