from enum import Enum
from importlib import import_module
from glob import glob
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
for ai_glob in glob("ai/*"):
    if isdir(ai_glob):
        modules[ai_glob.split('/')[-1]] = import_module(ai_glob.replace('/', '.'))


def load(name, function):
    return getattr(modules.get(name), function.value)
