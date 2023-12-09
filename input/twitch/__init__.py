import asyncio

from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from yaml import safe_load

from input.twitch.bots import Bot
from input.twitch.config import Events, Emotes, Secrets
from input.twitch.listeners import Listener


class InputController:
    def __init__(self, settings, client, bot, listener, helper):
        self.settings = settings
        self.client = client
        self.bot = bot
        self.listener = listener
        self.helper = helper

    @classmethod
    async def create(cls):
        settings = InputSettings()
        client = await Twitch(settings.secrets.app_id, settings.secrets.app_secret)
        bot = await Bot.create(client, settings)
        listener = await Listener.create(client, settings.events, settings.emotes)
        helper = UserAuthenticationStorageHelper(client, listener.target_scopes)
        await helper.bind()
        return InputController(settings, client, bot, listener, helper)

    async def collect(self):
        await self.helper.bind()

        notification_task = asyncio.create_task(self.listener.start())
        chatbot_task = asyncio.create_task(self.bot.start())
        await asyncio.gather(notification_task, chatbot_task)


class InputSettings:

    def __init__(self):
        with open('config.yaml', 'r') as file:
            yaml = safe_load(file)
        self.broadcaster = yaml.get('broadcaster', [])
        self.secrets = Secrets(yaml.get('secrets'))
        self.emotes = Emotes(yaml.get('emotes'))
        self.events = Events(yaml.get('events'))


async def collect():
    twitch_input = await InputController.create()
    await twitch_input.collect()


if __name__ == "__main__":
    asyncio.run(collect())
