import asyncio
import re
from enum import Enum

import requests
from decouple import config
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelCheerEvent, ChannelPointsCustomRewardRedemptionAddEvent
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

from utils.logging import log


class TwitchEventType(Enum):
    UNKNOWN = 0
    CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION_ADD = 1
    CHANNEL_CHEER = 2


class TwitchEvent:
    def __init__(self, data):
        match type(data):
            case ChannelCheerEvent:
                self.type = TwitchEventType.CHANNEL_CHEER
                self.data = data
            case ChannelPointsCustomRewardRedemptionAddEvent:
                self.type = TwitchEventType.CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION_ADD
                self.data = data
            case _:
                self.type = TwitchEventType.UNKNOWN
                self.data = data


class Input:
    def __init__(self):
        self.APP_ID = config('TWITCH_APP_ID')
        self.APP_SECRET = config('TWITCH_APP_SECRET')
        self.TARGET_SCOPES = [AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS]

        self.twitch = None
        self.helper = None
        self.user = None

        self.events = []
        self.session_bits = 0
        self.session_channel_points = 0

    async def on_cheer(self, data: ChannelCheerEvent):
        message = re.sub(r'\bcheer\d+\b', '', data.event.message, flags=re.IGNORECASE)
        self.events.append(TwitchEvent(data))
        self.session_bits += data.event.bits
        log.info(f'\n{data.event.user_name} cheered {data.event.bits}! : {message}')
        requests.post(
            "http://localhost:8008/",
            json={
                "message": f' Viewer {data.event.user_name} says: {message}',
                "character": "Other Poop"
            }
        )

    async def on_channel_point_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        match data.event.reward.title:
            case 'Ask a Question':
                log.info(f'\n{data.event.user_name} asks : {data.event.user_input}')
                self.events.append(TwitchEvent(data))
                self.session_channel_points += data.event.reward.cost
                requests.post(
                    "http://localhost:8008/",
                    json={
                        "message": f' Viewer {data.event.user_name} says: {data.event.user_input}',
                        "character": "Other Poop"
                    }
                )
            case _:
                log.info(f'\n{data.event.user_name} redeemed {data.event.reward.title}')
                self.events.append(TwitchEvent(data))
                self.session_channel_points += data.event.reward.cost

    async def run(self):
        self.twitch = await Twitch(self.APP_ID, self.APP_SECRET)
        self.helper = UserAuthenticationStorageHelper(self.twitch, self.TARGET_SCOPES)
        await self.helper.bind()

        self.user = await first(self.twitch.get_users())

        event_sub = EventSubWebsocket(self.twitch)
        event_sub.start()

        await event_sub.listen_channel_cheer(self.user.id, self.on_cheer)
        await event_sub.listen_channel_points_custom_reward_redemption_add(self.user.id,
                                                                           self.on_channel_point_redemption)


if __name__ == "__main__":
    twitch_input = Input()
    asyncio.run(twitch_input.run())
