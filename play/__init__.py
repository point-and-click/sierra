from glob import glob

from yaml import safe_load

from play.character import Character
from play.task import Task

characters = {}
for character_glob in glob("config/characters/*.yaml"):
    character_name = character_glob.split("/")[-1].split(".")[0]

    with open(character_glob, "r") as character_yaml:
        characters[character_name] = Character(safe_load(character_yaml))

tasks = {}
for task_glob in glob("config/tasks/*.yaml"):
    task_name = task_glob.split("/")[-1].split(".")[0]

    with open(task_glob, "r") as task_yaml:
        tasks[task_name] = Task(safe_load(task_yaml))
