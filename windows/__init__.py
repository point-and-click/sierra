import pyglet

from utils.logging import log


class Window:
    def __init__(self, name, width, height):
        self.manager = Manager()
        self.name = name
        self.dimensions = self._Dimensions(width, height)
        self.window = pyglet.window.Window(width=width, height=height, caption=name)

        self.manager.register(self)

        @self.window.event
        def on_key_press(symbol, modifiers):
            if modifiers is None:
                if symbol == pyglet.window.key.ESCAPE:
                    return pyglet.event.EVENT_HANDLED

        @self.window.event
        def on_close():
            return pyglet.event.EVENT_HANDLED

    class _Dimensions:
        def __init__(self, width, height):
            self.width = width
            self.height = height


class Manager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.characters = {}
            self.subtitles = None

            self._initialized = True

    def start(self):
        log.info(f'Starting Visual (x{len(self.characters.keys())}) ...')
        pyglet.app.run()

    def register(self, window: Window):
        self.characters[window.name] = window
