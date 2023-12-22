import asyncio

from yaml import safe_load

from input import chat
from utils.logging import log


class InputController:
    def __init__(self):
        self.settings = InputSettings()

    def collect(self):
        while True:
            log.info(''.join([f'{i}: {character}\n' for i, character in enumerate(self.settings.characters)]))
            index = int(input('Character: '))
            prompt = input(f'Ask {self.settings.characters[index]}: ')

            chat.submit(prompt, self.settings.characters[index])


class InputSettings:
    def __init__(self):
        with open('input/keyboard/config.yaml', 'r') as file:
            self._raw = safe_load(file)
        self.characters = self._raw.get('characters', [])


async def collect():
    keyboard_input = InputController()
    keyboard_input.collect()


if __name__ == "__main__":
    asyncio.run(collect())
