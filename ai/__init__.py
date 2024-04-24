from enum import Enum
from importlib import import_module
from glob import glob
from os import path
from os.path import isdir


class Function(Enum):
    """
    The different functions that can be called on an AI.
    """
    CHAT = "Chat"
    SPEAK = "Speak"
    TRANSCRIBE = "Transcribe"


class Role(Enum):
    """
    The different roles that an AI can have.
    """
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


ai = {}
for ai_glob in glob(path.join('ai', '*')):
    if isdir(ai_glob) and not ai_glob.startswith('_'):
        if path.exists(path.join(ai_glob, '__init__.py')):
            ai[path.split(ai_glob)[-1]] = import_module('.'.join(path.split(ai_glob)))


def load(name, function):
    """
    `load` function to load a function from an AI.
    :param name:
    :param function:
    :return:
    """
    return getattr(ai.get(name), function.value)
