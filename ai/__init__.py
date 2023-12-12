from enum import Enum
from importlib.util import spec_from_file_location, module_from_spec
from glob import glob
from os.path import isdir


class Role(Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


modules = {}
for ai_glob in glob("ai/*"):
    if isdir(ai_glob):
        spec = spec_from_file_location(ai_glob.split('/')[-1], f'{ai_glob}/__init__.py')
        module = module_from_spec(spec)
        modules[ai_glob.split('/')[-1]] = module
