import json
import re

import requests
from twitchAPI.chat import EventData, Chat, ChatCommand, ChatMessage
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.type import ChatEvent, AuthScope

from utils.logging import log

target_scopes = [
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT
]


class Bot:
    def __init__(self, client, helper, chat, broadcaster, replies):
        self.client = client
        self.helper = helper
        self.chat = chat
        self.broadcaster = broadcaster
        self.replies = replies
        self.commands = {
            'rules': self.command_rules,
            'help': self.command_help
        }

    @classmethod
    async def create(cls, secrets, broadcaster, replies):
        client = await Twitch(secrets.app_id, secrets.app_secret)
        helper = UserAuthenticationStorageHelper(client, target_scopes)
        await helper.bind()
        chat = await Chat(client)
        return Bot(client, helper, chat, broadcaster, replies)

    async def start(self):
        log.info('Starting chat bot')
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
        for command, function in self.commands.items():
            self.chat.register_command(command, function)
        self.chat.start()
        log.info('Chat bot started. Waiting for ready event.')

    async def on_ready(self, ready_event: EventData):
        await ready_event.chat.join_room(self.broadcaster)
        log.info(f'Bot joined {self.broadcaster}\'s chat.')

    async def on_message(self, message: ChatMessage):
        replies = [
            (reply, found) for reply in self.replies
            for found in re.findall(rf'{reply.pattern}', message.text, re.IGNORECASE)
        ]

        for reply, _ in replies:
            await message.reply(f'{reply.response}')

    @staticmethod
    async def command_rules(cmd: ChatCommand):
        result = requests.get("http://localhost:8008/rules")
        rules = '\n\n'.join(json.loads(result.text))
        await cmd.reply(f'Here\'s the rules:\n\n{rules}')

    @staticmethod
    async def command_help(cmd: ChatCommand):
        await cmd.reply('Here\'s the commands:\n\n!rules\n\n!help')
