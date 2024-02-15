from os import path

from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))


class Chat:
    # TODO: Implement Chat class
    pass
