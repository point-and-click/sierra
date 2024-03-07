import asyncio
import logging
import sys
from threading import Thread
from glob import glob

from input import sierra
import plugins
from play.sessions import Session
from utils.logging import log


class Service:
    """
    `Service` class to represent a service.
    """
    def __init__(self):
        self.thread = Thread(target=Service.thread)

    @staticmethod
    def thread():
        """
        `thread` method to start the service.
        """
        log.info('Starting Session ...')
        asyncio.run(session.gather())

    def start(self):
        """
        `start` method to start the service.
        """
        self.thread.start()


class API:
    """
    `API` class to represent an API.
    """
    def __init__(self):
        self.thread = Thread(target=API.thread)

    @staticmethod
    def thread():
        """
        `thread` method to start the API.
        """
        log.info('Starting API ...')
        sierra.run(port=8008)

    def start(self):
        """
        `start` method to start the API.
        """
        self.thread.start()


if __name__ == '__main__':
    sys.modules['flask.cli'].show_server_banner = lambda *x: None
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)

    with Session() as session:
        plugins.hook(plugins.HookType.INITIALIZE, session, None)
        saves = glob('saves/*.sierra')
        if saves:
            if input('Load history from previous session? (y/N): ').lower().startswith('y'):
                log.info(''.join([f'{i}: {save}\n' for i, save in enumerate(saves)]))
                index = int(input('Load save: '))
                session.load(saves[index])
                session.windows.associate(session)

        Service().start()
        API().start()
        session.windows.start()
