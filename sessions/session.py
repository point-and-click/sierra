from datetime import datetime

from characters.character import Character


class Session:
    def __init__(self, character_name):
        self.time = datetime.now()
        self.character = Character(character_name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def begin(self):
        while True:
            prompt = input('')
            self.save(self.character.chat(prompt))

    def save(self, response):
        with open(f'saves/{self.character.name}/{self.time}.clog', 'a') as f:
            f.write(response)
