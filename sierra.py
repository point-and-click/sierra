from glob import glob

import elevenlabs
import openai
from decouple import config

from sessions.session import Session
from utils.logging import log

openai.api_key = config('OPENAI_API_KEY')
elevenlabs.set_api_key(config('ELEVENLABS_API_KEY'))

if __name__ == '__main__':
    with Session(character_name=config('CHARACTER'), task_name=config('TASK')) as session:
        saves = glob('saves/*.sierra')
        if saves:
            if input('Load from previous session? (y/N): ').lower().startswith('y'):
                log.info(''.join([f'{i}: {save}\n' for i, save in enumerate(saves)]))
                index = int(input('Load save: '))
                session.load(saves[index])

        session.begin()
