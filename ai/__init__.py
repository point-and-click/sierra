from enum import Enum
from importlib import import_module
from glob import glob
from os import path
from os.path import isdir


class Function(Enum):
    CHAT = "Chat"
    SPEAK = "Speak"
    TRANSCRIBE = "Transcribe"


class Role(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


ai = {}
for ai_glob in glob(path.join('ai', '*')):
    if isdir(ai_glob) and not ai_glob.startswith('_'):
        if path.exists(path.join(ai_glob, '__init__.py')):
            ai[path.split(ai_glob)[-1]] = import_module('.'.join(path.split(ai_glob)))


def load(name, function):
    return getattr(ai.get(name), function.value)
