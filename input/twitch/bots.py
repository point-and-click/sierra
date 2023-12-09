import json

import requests
from twitchAPI.chat import EventData, Chat, ChatCommand
from twitchAPI.type import ChatEvent

from utils.logging import log


class Bot:
    def __init__(self, chat, broadcaster):
        self.chat = chat
        self.broadcaster = broadcaster

    @classmethod
    async def create(cls, client, config):
        chat = await Chat(client)
        return Bot(chat, config.broadcaster)

    async def start(self):
        log.info('Starting chat bot')
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_command('rules', self.command_rules)
        self.chat.start()
        log.info('Chat bot started. Waiting for ready event.')

    async def on_ready(self, ready_event: EventData):
        log.info('Bot is ready for work, joining channel')
        await ready_event.chat.join_room(self.broadcaster)
        log.info('Bot joined channel')

    @staticmethod
    async def command_rules(cmd: ChatCommand):
        result = requests.get("http://localhost:8008/rules")
        rules = '\n\n'.join(json.loads(result.text))
        await cmd.reply(f'Here\'s the rules:\n\n{rules}')
