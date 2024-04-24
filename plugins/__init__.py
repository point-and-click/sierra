from enum import Enum
from glob import glob
from importlib import import_module
from os import path


class HookType(Enum):
    INITIALIZE = 'Initialize'
    PRE_CHAT = 'PreChat'
    POST_CHAT = 'PostChat'
    PRE_SPEECH = 'PreSpeech'
    POST_SPEECH = 'PostSpeech'
    PRE_TRANSCRIBE = 'PreTranscribe'
    POST_TRANSCRIBE = 'PostTranscribe'


plugins = []
for plugin_glob in glob(path.join('plugins', '*')):
    if path.isdir(plugin_glob) and not path.split(plugin_glob)[-1].startswith('_'):
        if path.exists(path.join(plugin_glob, '__init__.py')):
            plugins.append(import_module('.'.join(path.split(plugin_glob))))


def hook(hook_type, session, character, *args):
    for plugin in plugins:
        try:
            getattr(plugin, hook_type.value).hook(session, character, *args)
        except AttributeError:
            pass
