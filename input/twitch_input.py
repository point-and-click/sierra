import asyncio
import json
import re

import requests

from decouple import config
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelCheerEvent, ChannelPointsCustomRewardRedemptionAddEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import AuthScope


class TwitchNotification:
    APP_ID = config('TWITCH_APP_ID')
    APP_SECRET = config('TWITCH_APP_SECRET')
    TARGET_SCOPES = [AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS]

    def __init__(self):
        self.emote_dict = {}

    async def on_cheer(self, data: ChannelCheerEvent):
        message = re.sub(r'\bcheer\d+\b', '', data.event.message, flags=re.IGNORECASE)
        print(f'\n{data.event.user_name} cheered {data.event.bits}! : {message}')
        character_name, message = self.get_character_name_from_emotes(message)
        requests.post("http://localhost:8008/",
                      json={"message": f' Viewer {data.event.user_name} says: {message}', "character": character_name})

    async def on_channel_point_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        # our event happend, lets do things with the data we got!
        message = f' Viewer {data.event.user_name} says: {data.event.user_input}'
        print(message)
        character_name, message = self.get_character_name_from_emotes(message)
        requests.post("http://localhost:8008/",
                      json={"message": message,
                            "character": character_name})

    def init_emote_dict(self):
        file_path = 'config/characters/emote_dict.json'
        with open(file_path, 'r') as file:
            self.emote_dict = json.load(file)

    async def run(self):
        self.init_emote_dict()
        # create the api instance and get user auth either from storage or website
        twitch = await Twitch(self.APP_ID, self.APP_SECRET)
        helper = UserAuthenticationStorageHelper(twitch, self.TARGET_SCOPES)
        await helper.bind()

        # get the currently logged in user
        user = await first(twitch.get_users())

        # create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()

        await eventsub.listen_channel_cheer(user.id, self.on_cheer)
        await eventsub.listen_channel_points_custom_reward_redemption_add(user.id, self.on_channel_point_redemption)

    def get_character_name_from_emotes(self, message):
        character_keys = re.findall(r'\broughc3\w+\b', message, flags=re.IGNORECASE)
        message = re.sub(r'\broughc3\w+\b', '', message, flags=re.IGNORECASE)
        if len(character_keys) == 0:
            character_name = next(iter(self.emote_dict.items()))[1]
        else:
            character_name = self.emote_dict[character_keys[0]]

        return character_name, message


if __name__ == "__main__":
    twitch_input = TwitchNotification()
    asyncio.run(twitch_input.run())
