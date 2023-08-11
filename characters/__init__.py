import os.path

import yaml

with open("characters.yaml", "r") as stream:
    characters = yaml.safe_load(stream)
    for character in characters.keys():
        if not os.path.exists(f'saves/{character}'):
            os.mkdir(f'saves/{character}')
            os.mkdir(f'saves/{character}/audio')


with open("tasks.yaml", "r") as stream:
    tasks = yaml.safe_load(stream)
