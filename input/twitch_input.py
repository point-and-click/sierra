import asyncio
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
        pass

    async def on_cheer(self, data: ChannelCheerEvent):
        message = re.sub(r'\bcheer\d+\b', '', data.event.message, flags=re.IGNORECASE)
        print(f'\n{data.event.user_name} cheered {data.event.bits}! : {message}')
        requests.post("http://localhost:8008/",
                      json={"message": f' Viewer {data.event.user_name} says: {message}', "character": "Other Poop"})

    async def on_channel_point_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        # our event happend, lets do things with the data we got!
        print(f'\n{data.event.user_name} asks : {data.event.user_input}')
        requests.post("http://localhost:8008/",
                      json={"message": f' Viewer {data.event.user_name} says: {data.event.user_input}',
                            "character": "Other Poop"})

    async def run(self):
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


if __name__ == "__main__":
    twitch_input = TwitchNotification()
    asyncio.run(twitch_input.run())

