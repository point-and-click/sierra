import re

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope

from input import chat, rule
from input.twitch.config import FunctionType
from utils.logging import log

target_scopes = [
    AuthScope.BITS_READ,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
    AuthScope.USER_READ_FOLLOWS,
    AuthScope.MODERATOR_READ_FOLLOWERS,
    AuthScope.CHANNEL_READ_POLLS,
    AuthScope.CHANNEL_READ_PREDICTIONS,
    AuthScope.CHANNEL_READ_HYPE_TRAIN,
]


class Listener:
    """
    :param client:
    :param helper:
    :param events:
    :param emotes:
    :param event_sub:
    :param user:
    """
    def __init__(self, client, helper, events, emotes, event_sub, user):
        self.client = client
        self.helper = helper
        self.events = events
        self.emotes = emotes
        self.event_sub = event_sub
        self.user = user

    @classmethod
    async def create(cls, secrets, events, emotes):
        """
        :param secrets:
        :param events:
        :param emotes:
        :return:
        """
        client = await Twitch(secrets.app_id, secrets.app_secret)
        helper = UserAuthenticationStorageHelper(client, target_scopes)
        await helper.bind()

        event_sub = EventSubWebsocket(client)
        user = await first(client.get_users())

        return Listener(client, helper, events, emotes, event_sub, user)

    async def start(self):
        """
        :return: None
        """
        self.event_sub.start()

        await self.event_sub.listen_channel_cheer(
            broadcaster_user_id=self.user.id,
            callback=self.on_cheer
        )
        await self.event_sub.listen_channel_follow_v2(
            broadcaster_user_id=self.user.id,
            moderator_user_id=self.user.id,
            callback=self.on_follow
        )
        await self.event_sub.listen_channel_points_custom_reward_redemption_add(
            broadcaster_user_id=self.user.id,
            callback=self.on_channel_point_redemption
        )
        await self.event_sub.listen_channel_poll_begin(
            broadcaster_user_id=self.user.id,
            callback=self.on_poll_begin
        )
        await self.event_sub.listen_channel_poll_end(
            broadcaster_user_id=self.user.id,
            callback=self.on_poll_end
        )
        await self.event_sub.listen_channel_prediction_begin(
            broadcaster_user_id=self.user.id,
            callback=self.on_prediction
        )
        await self.event_sub.listen_channel_prediction_end(
            broadcaster_user_id=self.user.id,
            callback=self.on_prediction_end
        )
        await self.event_sub.listen_channel_raid(
            to_broadcaster_user_id=self.user.id,
            callback=self.on_raid
        )
        await self.event_sub.listen_hype_train_begin(
            broadcaster_user_id=self.user.id,
            callback=self.on_hype_train_start
        )
        await self.event_sub.listen_hype_train_end(
            broadcaster_user_id=self.user.id,
            callback=self.on_hype_end
        )
        await self.event_sub.listen_channel_subscribe(
            broadcaster_user_id=self.user.id,
            callback=self.on_subscribe
        )
        await self.event_sub.listen_channel_subscription_gift(
            broadcaster_user_id=self.user.id,
            callback=self.on_subscribe_gift
        )
        log.info('Listening for Twitch events.')

    async def on_channel_point_redemption(self, data):
        """
        :param data: ChannelPointsCustomRewardRedemptionAddEvent
        """
        character, message = process(self.emotes, data.event.user_input)

        events = self.events.map.get('channel_point_redemption')
        event = events.get(data.event.reward.title)

        match event.function:
            case FunctionType.CHAT:
                chat.submit(
                    event.message.format(data=data, message=message),
                    character,
                    'twitch'
                )
            case FunctionType.RULE:
                rule.submit(message, character)
                chat.submit(
                    event.message.format(data=data, message=message),
                    character,
                    'twitch'
                )

    async def on_cheer(self, data):
        """
        :param data: ChannelCheerEvent
        """
        character, message = process(self.emotes, data.event.message)

        message = re.sub(r'\bcheer\d+\b', '', message, flags=re.IGNORECASE)

        events = self.events.map.get('cheer')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.bits], default=1))

        chat.submit(
            event.message.format(data=data, message=message),
            character,
            'twitch'
        )

    async def on_follow(self, data):
        """
        :param data: ChannelFollowEvent
        """
        events = self.events.map.get('follow')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.followed_at], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_hype_train_start(self, data):
        """
        :param data: HypeTrainEvent
        """
        events = self.events.map.get('hype_train_start')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.level], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_hype_end(self, data):
        """
        :param data: HypeTrainEndEvent
        """
        events = self.events.map.get('hype_end')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.level], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_poll_begin(self, data):
        """
        :param data: ChannelPollBeginEvent
        """
        events = self.events.map.get('poll_begin')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.choices)], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_poll_end(self, data):
        """
        :param data: ChannelPollEndEvent
        """
        events = self.events.map.get('poll_end')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.choices)], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_prediction(self, data):
        """
        :param data: ChannelPredictionEvent
        """
        events = self.events.map.get('prediction')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.outcomes)], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_prediction_end(self, data):
        """
        :param data: ChannelPredictionEndEvent
        """
        events = self.events.map.get('prediction_end')
        event = events.get(max([tier for tier in events.keys() if tier <= len(data.event.outcomes)], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_raid(self, data):
        """
        :param data: ChannelRaidEvent
        """
        events = self.events.map.get('raid')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.viewers], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_subscribe(self, data):
        """
        :param data: ChannelSubscribeEvent
        """
        events = self.events.map.get('subscribe')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.tier], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )

    async def on_subscribe_gift(self, data):
        """
        :param data: ChannelSubscriptionGiftEvent
        """
        events = self.events.map.get('subscribe_gift')
        event = events.get(max([tier for tier in events.keys() if tier <= data.event.tier], default=1))

        chat.submit(
            event.message.format(data=data),
            self.emotes.characters[0],
            'twitch'
        )


def process(emotes, message):
    """
    :param emotes:
    :param message:
    :return:
    """
    characters = re.findall(rf'{emotes.prefix}(\S+)', message, flags=re.IGNORECASE)
    message = re.sub(rf'{emotes.prefix}(\S+)', '', message, flags=re.IGNORECASE)

    return characters[0] if characters else emotes.characters[0], message
