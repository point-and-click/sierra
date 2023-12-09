import asyncio
import json
import re

import requests
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch

from input.twitch.bots import Bot
from input.twitch.helpers import Events, Emotes, Secrets
from input.twitch.listeners import Listener, FunctionType


class InputController:
    def __init__(self):
        self.client = None
        self.helper = None
        self.config = InputConfig()
        self.read_result_ids = []
        self.bot = Bot(self)
        self.listener = Listener(self)

    @staticmethod
    def submit_rule(rule, character):
        requests.post("http://localhost:8008/rule",
                      json={"rule": rule, "character": character})

    @staticmethod
    def submit_chat(message, character):
        requests.post("http://localhost:8008/chat",
                      json={"message": message,
                            "character": character})

    def process(self, message):
        characters = re.findall(rf'{self.config.emotes.prefix}(\S+)', message, flags=re.IGNORECASE)
        message = re.sub(rf'{self.config.emotes.prefix}(\S+)', '', message, flags=re.IGNORECASE)

        return characters[0] if characters else self.config.emotes.characters[0], message

    async def collect(self):
        self.client = await Twitch(self.config.secrets.app_id, self.config.secrets.app_secret)
        self.helper = UserAuthenticationStorageHelper(self.client, self.listener.target_scopes)
        await self.helper.bind()

        notification_task = asyncio.create_task(self.listener.start())
        chatbot_task = asyncio.create_task(self.bot.start())
        await asyncio.gather(notification_task, chatbot_task)



class InputConfig:
    def __init__(self):
        with open('config.json', 'r') as config:
            self._raw = json.load(config)
        self.broadcaster = self._raw.get('broadcaster', [])
        self.secrets = Secrets(self._raw.get('secrets'))
        self.emotes = Emotes(self._raw.get('emotes'))
        self.events = Events(self._raw.get('events'))


if __name__ == "__main__":
    twitch_input = InputController()
    asyncio.run(twitch_input.collect())
