import logging
import re
import sys

from utils.logging import _format, palette

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

replacements = {
    # AI Clients
    'OpenAI': f'{_format.color(palette.material.cyan)}OpenAI{_format.reset()}',
    'ElevenLabs': f'{_format.color(palette.material.cyan)}ElevenLabs{_format.reset()}',
    'Whisper': f'{_format.color(palette.material.cyan)}Whisper{_format.reset()}',
    # Usage
    'Usage': f'{_format.color(palette.material.pink)}Usage{_format.reset()}',
    '[0-9]+ tokens': f'{_format.color(palette.material.purple)}\\g<0>{_format.reset()}',
    '[0-9]+ words': f'{_format.color(palette.material.purple)}\\g<0>{_format.reset()}',
    # Input
    'Input': f'{_format.color(palette.material.orange)}Input{_format.reset()}',
    'Recording': f'{_format.color(palette.material.red)}Recording{_format.reset()}',
    # Characters
    '\(([^\)]+?)\)': f'{_format.color(palette.material.blue)}(\\g<1>){_format.reset()}',
}


class Log:
    @staticmethod
    def info(message):
        for pattern, replacement in replacements.items():
            message = re.sub(pattern, replacement, message)

        logging.info(message)


log = Log()
