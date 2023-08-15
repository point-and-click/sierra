from datetime import datetime

from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT
from utils.logging import log


class Character:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.motivation = yaml.get('motivation', None)
        self.format = yaml.get('format', None)
        self.voice = yaml.get('voice', None)

    def chat(self, messages):
        response, usage = ChatGPT.chat(messages)

        log.info(f'Character ({self.name}): {response}')

        if config('ENABLE_SPEECH', cast=bool):
            log.info('ElevenLabs: Speech synthesis requested')
            Eleven.speak(response, self.voice, f'saves/audio/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.wav')
        else:
            log.info('ElevenLabs: Speech synthesis is disabled. Skipping.')

        return response, usage
