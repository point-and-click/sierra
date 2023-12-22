import asyncio
import logging
import sys
from threading import Thread
from glob import glob

from input import sierra
from sessions import Session
from utils.logging import log


class Service:
    def __init__(self):
        self.thread = Thread(target=Service.thread)

    @staticmethod
    def thread():
        log.info('Starting Session ...')
        asyncio.run(session.gather())

    def start(self):
        self.thread.start()


class API:
    def __init__(self):
        self.thread = Thread(target=API.thread)

    @staticmethod
    def thread():
        log.info('Starting API ...')
        sys.modules['flask.cli'].show_server_banner = lambda *x: None
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        sierra.run(port=8008)

    def start(self):
        self.thread.start()


if __name__ == '__main__':
    with Session() as session:
        saves = glob('saves/*.sierra')
        if saves:
            if input('Load history from previous session? (y/N): ').lower().startswith('y'):
                log.info(''.join([f'{i}: {save}\n' for i, save in enumerate(saves)]))
                index = int(input('Load save: '))
                session.load(saves[index])

        Service().start()
        API().start()
        session.windows.start()
