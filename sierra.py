import asyncio
import logging
import sys
from threading import Thread
from glob import glob

from input import sierra
from sessions import Session
from utils.logging import log


def service():
    asyncio.run(session.gather())


def api():
    sys.modules['flask.cli'].show_server_banner = lambda *x: None
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    sierra.run(port=8008)


if __name__ == '__main__':
    with Session() as session:
        saves = glob('saves/*.sierra')
        if saves:
            if input('Load history from previous session? (y/N): ').lower().startswith('y'):
                log.info(''.join([f'{i}: {save}\n' for i, save in enumerate(saves)]))
                index = int(input('Load save: '))
                session.load(saves[index])

        log.info('Running Sierra')

        service_thread = Thread(target=service)
        service_thread.start()
        api_thread = Thread(target=api)
        api_thread.start()
