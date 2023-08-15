from glob import glob

from yaml import safe_load

from play.character import Character
from play.task import Task

characters = {}
for character_glob in glob("config/characters/*.yaml"):
    with open(character_glob, "r") as character_yaml:
        character = Character(safe_load(character_yaml))
        characters[character.name] = character

tasks = {}
for task_glob in glob("config/tasks/*.yaml"):
    with open(task_glob, "r") as task_yaml:
        task = Task(safe_load(task_yaml))
        tasks[task.name] = task
