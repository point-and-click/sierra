import pyglet

from utils.logging import log
from windows.window import Window


class Manager:
    def __init__(self):
        self.characters = {}
        self.broadcast = Window('broadcast')

    def start(self):
        log.info(f'Starting window manager: {self.characters}')
        pyglet.app.run()

    def register(self, character):
        self.characters[character.name] = Window(character.name)
