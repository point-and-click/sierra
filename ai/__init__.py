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


modules = {}
for ai_glob in glob(path.join('ai', '*')):
    if isdir(ai_glob):
        modules[path.split(ai_glob)[-1]] = import_module('.'.join(path.split(ai_glob)))


def load(name, function):
    return getattr(modules.get(name), function.value)
