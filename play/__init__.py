from glob import glob

from yaml import safe_load

from play.character import Character
from play.task import Task
from utils.logging import log

characters = {}
for character_glob in glob("play/characters/*"):
    try:
        with open(f'{character_glob}/character.yaml', "r") as character_yaml:
            character = Character(character_glob, safe_load(character_yaml))
            characters[character.name] = character
    except FileNotFoundError:
        log.warn(f'Character folder contains invalid character setup: {character_glob}')
tasks = {}
for task_glob in glob("config/tasks/*.yaml"):
    with open(task_glob, "r") as task_yaml:
        task = Task(safe_load(task_yaml))
        tasks[task.name] = task
