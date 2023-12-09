import logging
import re
import sys

from utils.logging import format, palette

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

replacements = {
    # AI Clients
    'OpenAI': f'{format.color(palette.material.cyan)}OpenAI{format.reset()}',
    'ElevenLabs': f'{format.color(palette.material.cyan)}ElevenLabs{format.reset()}',
    'PlayHT': f'{format.color(palette.material.cyan)}PlayHT{format.reset()}',
    'Whisper': f'{format.color(palette.material.cyan)}Whisper{format.reset()}',
    # Usage
    'Usage': f'{format.color(palette.material.pink)}Usage{format.reset()}',
    '[0-9]+ tokens': f'{format.color(palette.material.purple)}\\g<0>{format.reset()}',
    '[0-9]+ words': f'{format.color(palette.material.purple)}\\g<0>{format.reset()}',
    # input.py
    'input.py': f'{format.color(palette.material.orange)}input.py{format.reset()}',
    'Recording': f'{format.color(palette.material.red)}Recording{format.reset()}',
    # Characters
    '\(([^\)]+?)\)': f'{format.color(palette.material.blue)}(\\g<1>){format.reset()}',
}


class Log:
    @staticmethod
    def info(message):
        for pattern, replacement in replacements.items():
            message = re.sub(pattern, replacement, message)

        logging.info(message)


log = Log()
