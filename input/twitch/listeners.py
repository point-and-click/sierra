import re
from enum import Enum

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.object.eventsub import (ChannelCheerEvent, ChannelPointsCustomRewardRedemptionAddEvent,
                                       ChannelSubscribeEvent, ChannelSubscriptionGiftEvent, ChannelFollowEvent,
                                       ChannelPollBeginEvent, ChannelPollEndEvent, ChannelRaidEvent, HypeTrainEvent,
                                       HypeTrainEndEvent, ChannelPredictionEvent, ChannelPredictionEndEvent)
from twitchAPI.type import AuthScope

from input.twitch import InputController
from utils.logging import log


class FunctionType(Enum):
    CHAT = "chat"
    RULE = "rule"


class Listener:
    def __init__(self, controller):
        self.controller = controller

        self.target_scopes = [
            AuthScope.BITS_READ,
            AuthScope.CHANNEL_READ_REDEMPTIONS,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
            AuthScope.USER_READ_FOLLOWS,
            AuthScope.MODERATOR_READ_FOLLOWERS,
            AuthScope.CHANNEL_READ_POLLS,
            AuthScope.CHANNEL_READ_PREDICTIONS,
            AuthScope.CHANNEL_READ_HYPE_TRAIN,
            AuthScope.CHAT_READ,
            AuthScope.CHAT_EDIT
        ]

        self.user = None
        self.event_sub = None

    async def start(self):
        self.user = await first(self.controller.client.get_users())

        self.event_sub = EventSubWebsocket(self.controller.client)
        self.event_sub.start()

        await self.event_sub.listen_channel_cheer(self.user.id, self.on_cheer)
        await self.event_sub.listen_channel_follow_v2(self.user.id, self.user.id, self.on_follow)
        await self.event_sub.listen_channel_points_custom_reward_redemption_add(self.user.id,
                                                                                self.on_channel_point_redemption)
        await self.event_sub.listen_channel_poll_begin(self.user.id, self.on_poll_begin)
        await self.event_sub.listen_channel_poll_end(self.user.id, self.on_poll_end)
        await self.event_sub.listen_channel_prediction_begin(self.user.id, self.on_prediction)
        await self.event_sub.listen_channel_prediction_end(self.user.id, self.on_prediction_end)
        await self.event_sub.listen_channel_raid(to_broadcaster_user_id=self.user.id, callback=self.on_raid)
        await self.event_sub.listen_hype_train_begin(self.user.id, self.on_hype_train_start)
        await self.event_sub.listen_hype_train_end(self.user.id, self.on_hype_end)
        await self.event_sub.listen_channel_subscribe(self.user.id, self.on_subscribe)
        await self.event_sub.listen_channel_subscription_gift(self.user.id, self.on_subscribe_gift)
        log.info('Listening for Twitch events.')

    async def on_channel_point_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        character, message = self.controller.process(data.event.user_input)

        events = self.controller.config.events.map.get('channel_point_redemption')
        event = events.get(data.event.reward.title)

        match event.function:
            case FunctionType.CHAT:
                InputController.submit_chat(
                    event.message.format(data=data, message=message),
                    character
                )
            case FunctionType.RULE:
                InputController.submit_rule(message, character)
                InputController.submit_chat(
                    event.message.format(data=data, message=message),
                    character
                )

    async def on_cheer(self, data: ChannelCheerEvent):
        character, message = self.controller.process(data.event.message)

        message = re.sub(r'\bcheer\d+\b', '', message, flags=re.IGNORECASE)

        events = self.controller.config.events.map.get('cheer')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.bits], default=1))

        InputController.submit_chat(
            event.message.format(data=data, message=message),
            character
        )

    async def on_follow(self, data: ChannelFollowEvent):
        events = self.controller.config.events.map.get('follow')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.followed_at], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_hype_train_start(self, data: HypeTrainEvent):
        events = self.controller.config.events.map.get('hype_train_start')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.level], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_hype_end(self, data: HypeTrainEndEvent):
        events = self.controller.config.events.map.get('hype_end')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.level], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_poll_begin(self, data: ChannelPollBeginEvent):
        events = self.controller.config.events.map.get('poll_begin')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.choices)], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_poll_end(self, data: ChannelPollEndEvent):
        events = self.controller.config.events.map.get('poll_end')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.choices)], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_prediction(self, data: ChannelPredictionEvent):
        events = self.controller.config.events.map.get('prediction')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.outcomes)], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_prediction_end(self, data: ChannelPredictionEndEvent):
        events = self.controller.config.events.map.get('prediction_end')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.outcomes)], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_raid(self, data: ChannelRaidEvent):
        events = self.controller.config.events.map.get('raid')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.viewers], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_subscribe(self, data: ChannelSubscribeEvent):

        events = self.controller.config.events.map.get('subscribe')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.tier], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )

    async def on_subscribe_gift(self, data: ChannelSubscriptionGiftEvent):
        events = self.controller.config.events.map.get('subscribe_gift')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.tier], default=1))

        InputController.submit_chat(
            event.message.format(data=data),
            self.controller.config.emotes.characters[0]
        )
