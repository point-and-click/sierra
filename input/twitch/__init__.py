import asyncio
from enum import Enum

from yaml import safe_load

from input.twitch.bots import Bot
from input.twitch.config import Events, Emotes, Secrets
from input.twitch.listeners import Listener


class ClientType(Enum):
    LISTENER = "listener"
    BOT = "bot"


class InputController:
    def __init__(self, settings, bot, listener):
        self.settings = settings
        self.bot = bot
        self.listener = listener

    @classmethod
    async def create(cls):
        settings = InputSettings()

        bot = await Bot.create(settings.secrets.get(ClientType.BOT), settings.broadcaster)
        listener = await Listener.create(settings.secrets.get(ClientType.LISTENER), settings.events, settings.emotes)

        return InputController(settings, bot, listener)

    async def collect(self):
        notification_task = asyncio.create_task(self.listener.start())
        chatbot_task = asyncio.create_task(self.bot.start())
        await asyncio.gather(notification_task, chatbot_task)


class InputSettings:
    def __init__(self):
        with open('input/twitch/secrets.yaml', 'r') as file:
            yaml = safe_load(file)
        self.secrets = {
            ClientType.LISTENER: Secrets(yaml.get('listener')),
            ClientType.BOT: Secrets(yaml.get('bot'))
        }
        with open('input/twitch/config.yaml', 'r') as file:
            yaml = safe_load(file)
        self.broadcaster = yaml.get('broadcaster', [])
        self.bot = yaml.get('bot', {})
        self.listener = yaml.get('listener', {})
        self.emotes = Emotes(yaml.get('emotes'))
        self.events = Events(yaml.get('events'))


async def collect():
    twitch_input = await InputController.create()
    await twitch_input.collect()


if __name__ == "__main__":
    asyncio.run(collect())
