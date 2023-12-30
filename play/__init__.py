from glob import glob

from yaml import safe_load

from play.character import Character
from play.task import Task
from utils.logging import log


class Play:
    @staticmethod
    def characters():
        characters = {}
        for character_glob in glob("play/characters/*"):
            try:
                with open(f'{character_glob}/character.yaml', "r") as character_yaml:
                    c = Character(character_glob, safe_load(character_yaml))
                    characters[c.name] = c
            except FileNotFoundError:
                log.warning(f'Character folder contains invalid character setup: {character_glob}')
        return characters

    @staticmethod
    def tasks():
        tasks = {}
        for task_glob in glob("play/tasks/*.yaml"):
            with open(task_glob, "r") as task_yaml:
                t = Task(safe_load(task_yaml))
                tasks[t.name] = t
        return tasks
