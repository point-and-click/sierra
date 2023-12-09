import json

import requests
from twitchAPI.chat import EventData, Chat, ChatCommand
from twitchAPI.type import ChatEvent

from utils.logging import log


class Bot:
    def __init__(self, controller):
        self.controller = controller

    async def start(self):
        log.info('Starting chat bot')
        chat = await Chat(self.controller.client)
        chat.register_event(ChatEvent.READY, self.on_ready)
        chat.register_command('rules', self.command_rules)
        chat.start()
        log.info('Chat bot started. Waiting for ready event.')

    async def on_ready(self, ready_event: EventData):
        log.info('Bot is ready for work, joining channel')
        await ready_event.chat.join_room(self.controller.config.broadcaster)
        log.info('Bot joined channel')

    @staticmethod
    async def command_rules(cmd: ChatCommand):
        result = requests.get("http://localhost:8008/rules")
        rules = '\n\n'.join(json.loads(result.text))
        await cmd.reply(f'Here\'s the rules:\n\n{rules}')