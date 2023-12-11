import pyglet


class Window:
    def __init__(self, name):
        self._name = name
        self._window = pyglet.window.Window()

    def __enter__(self):
        return self._window

    def __exit__(self, exc_type, exc_value, traceback):
        self._manager.close(self._name)