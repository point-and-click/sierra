from datetime import datetime

import ai
from play import Character
import plugins
from settings import sierra_settings as settings


class Output:
    def __init__(self, _id,character: Character, chat, speech, subtitles):
        self.id = _id
        self.character = character
        self.chat = chat
        self.speech = speech
        self.subtitles = subtitles


