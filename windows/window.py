import pyglet


class Window:
    def __init__(self, name):
        self._name = name
        self._window = pyglet.window.Window()
