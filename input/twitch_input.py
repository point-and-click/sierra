import asyncio
import json
import re

import requests

from decouple import config
from twitchAPI.chat import EventData, Chat, ChatCommand
from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelCheerEvent, ChannelPointsCustomRewardRedemptionAddEvent, \
    ChannelSubscribeEvent, ChannelSubscriptionGiftEvent, ChannelFollowEvent, ChannelPollBeginEvent, ChannelPollEndEvent, \
    ChannelRaidEvent, HypeTrainEvent, HypeTrainEndEvent, ChannelPredictionEvent, ChannelPredictionEndEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import AuthScope, ChatEvent

from utils.logging import log


class TwitchNotification:
    APP_ID = config('TWITCH_APP_ID')
    APP_SECRET = config('TWITCH_APP_SECRET')
    TARGET_SCOPES = [AuthScope.BITS_READ, AuthScope.CHANNEL_READ_REDEMPTIONS, AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
                     AuthScope.USER_READ_FOLLOWS, AuthScope.MODERATOR_READ_FOLLOWERS, AuthScope.CHANNEL_READ_POLLS,
                     AuthScope.CHANNEL_READ_PREDICTIONS, AuthScope.CHANNEL_READ_HYPE_TRAIN,
                     AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    def __init__(self):
        self.config = {}
        self.read_result_ids = []

    async def on_channel_point_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        character_name, message = self.get_character_name_from_emotes(data.event.user_input)
        if data.event.reward.title == self.config["events"]["channel_point_redemption"]["ask_chatbot_event_title"]:
            TwitchNotification.message_chatbot(f'{self.config["events"]["channel_point_redemption"]["prefix"]}'
                                               f'Viewer {data.event.user_name} says: {message}.'
                                               f'{self.config["events"]["channel_point_redemption"]["suffix"]}',
                                               character_name)
        elif data.event.reward.title == self.config["events"]["channel_point_redemption"]["add_rule_event_title"]:
            TwitchNotification.add_rule(data.event.user_name, message, character_name)

    async def on_cheer(self, data: ChannelCheerEvent):
        message = re.sub(r'\bcheer\d+\b', '', data.event.message, flags=re.IGNORECASE)
        log.info(f'\n{data.event.user_name} cheered {data.event.bits}! : {message}')
        character_name, message = self.get_character_name_from_emotes(message)
        TwitchNotification.message_chatbot(f'{self.config["events"]["cheer"]["prefix"]}'
                                           f'Viewer {data.event.user_name} says: {message}.'
                                           f'{self.config["events"]["cheer"]["suffix"]}',
                                           character_name)

    async def on_follow(self, data: ChannelFollowEvent):
        TwitchNotification.message_chatbot(f'{self.config["events"]["follow"]["prefix"]}'
                                           f'User {data.event.user_name} just followed. '
                                           f'{self.config["events"]["follow"]["suffix"]}',
                                           "Other Poop")

    async def on_hype_train_start(self, data: HypeTrainEvent):
        TwitchNotification.message_chatbot(f'{self.config["events"]["hype_train_start"]["prefix"]}'
                                           f' Hype train has begun with a goal of: {data.event.goal}.'
                                           f' {self.config["events"]["hype_train_start"]["suffix"]}',
                                           "Other Poop")

    async def on_hype_end(self, data: HypeTrainEndEvent):
        TwitchNotification.message_chatbot(f'{self.config["events"]["hype_train_end"]["prefix"]}'
                                           f' Hype train has ended with a total of: {data.event.total}.'
                                           f' {self.config["events"]["hype_train_end"]["suffix"]}',
                                           "Other Poop")

    async def on_poll_begin(self, data: ChannelPollBeginEvent):
        choices = "\n".join(map(str, [x.title for x in data.event.choices]))
        TwitchNotification.message_chatbot(f'{self.config["events"]["poll_begin"]["prefix"]}'
                                           f' A new poll has begun. Title: {data.event.title} Choices: {choices}.'
                                           f'{self.config["events"]["poll_begin"]["suffix"]}',
                                           "Other Poop")

    async def on_poll_end(self, data: ChannelPollEndEvent):
        if any(data.event.id == event_id for event_id in self.read_result_ids):
            return

        choices = "\n".join(map(str, [f'{x.title} ({x.votes})' for x in data.event.choices]))
        TwitchNotification.message_chatbot(f'{self.config["events"]["poll_end"]["prefix"]}'
                                           f'The poll has ended.'
                                           f'\nTitle: {data.event.title} '
                                           f'\nChoices (and vote counts): {choices}'
                                           f'{self.config["events"]["poll_end"]["suffix"]}',
                                           "Other Poop")

        self.read_result_ids.append(data.event.id)

    async def on_prediction(self, data: ChannelPredictionEvent):
        outcomes = '\n'.join(outcome.title for outcome in data.event.outcomes)
        TwitchNotification.message_chatbot(f'{self.config["events"]["prediction_begin"]["prefix"]}'
                                           f'A new prediction event has begun.'
                                           f'\nTitle: {data.event.title}.'
                                           f'\nOutcomes: {outcomes}'
                                           f'{self.config["events"]["prediction_begin"]["suffix"]}',
                                           "Other Poop")

    async def on_prediction_end(self, data: ChannelPredictionEndEvent):
        # outcomes = '\n'.join(outcome.title for outcome in data.event.outcomes)
        # winner = next((obj for obj in data.event.outcomes if obj.id == data.event.winning_outcome_id), None)
        # TwitchNotification.message_chatbot(f'{self.config["events"]["prediction_end"]["prefix"]}'
        #                      f'A prediction event has ended. Title: {data.event.title}.'
        #                      f' Outcomes: {outcomes}'
        #                      f' Winner: {winner}'
        #                      f'{self.config["events"]["prediction_end"]["suffix"]}',
        #                      "Other Poop")
        pass

    async def on_raid(self, data: ChannelRaidEvent):
        TwitchNotification.message_chatbot(f'{self.config["events"]["raid"]["prefix"]}'
                                           f' We\'ve just been raided by {data.event.from_broadcaster_user_id}'
                                           f' with {data.event.viewers}! '
                                           f'{self.config["events"]["raid"]["suffix"]}',
                                           "Other Poop")

    async def on_subscribe(self, data: ChannelSubscribeEvent):
        message = (f'{self.config["events"]["subscribe"]["prefix"]}'
                   f' Viewer {data.event.user_name} subscribed to my channel!'
                   f' {self.config["events"]["subscribe"]["suffix"]}')
        TwitchNotification.message_chatbot(message,
                                           "Other Poop")

    async def on_subscribe_gift(self, data: ChannelSubscriptionGiftEvent):
        message = (f'{self.config["events"]["subscribe_gift"]["prefix"]}'
                   f' Viewer {data.event.user_name} gifted a subscription to my channel!'
                   f' {self.config["events"]["subscribe_gift"]["suffix"]}')
        TwitchNotification.message_chatbot(message,
                                           "Other Poop")

    def init_config(self):
        file_path = 'config/twitch_config.json'
        with open(file_path, 'r') as file:
            self.config = json.load(file)

    @staticmethod
    def add_rule(user_name, rule, character_name):
        print(f' Viewer {user_name} added rule: {rule}')
        requests.post("http://localhost:8008/rule",
                      json={"rule": rule, "character": character_name})

    @staticmethod
    def fetch_rules():
        log.info('Fetching rules.')
        return requests.get("http://localhost:8008/rules")

    @staticmethod
    def message_chatbot(message, character_name):
        log.info(message)
        requests.post("http://localhost:8008/",
                      json={"message": message,
                            "character": character_name})

    async def run_twitch_listeners(self, twitch):
        self.init_config()

        # get the currently logged in user
        user = await first(twitch.get_users())

        # create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()

        await eventsub.listen_channel_cheer(user.id, self.on_cheer)
        await eventsub.listen_channel_follow_v2(user.id, user.id, self.on_follow)
        await eventsub.listen_channel_points_custom_reward_redemption_add(user.id, self.on_channel_point_redemption)
        await eventsub.listen_channel_poll_begin(user.id, self.on_poll_begin)
        await eventsub.listen_channel_poll_end(user.id, self.on_poll_end)
        await eventsub.listen_channel_prediction_begin(user.id, self.on_prediction)
        # await eventsub.listen_channel_prediction_end(user.id, self.on_prediction_end)
        await eventsub.listen_channel_raid(to_broadcaster_user_id=user.id, callback=self.on_raid)
        await eventsub.listen_hype_train_begin(user.id, self.on_hype_train_start)
        await eventsub.listen_hype_train_end(user.id, self.on_hype_end)
        await eventsub.listen_channel_subscribe(user.id, self.on_subscribe)
        await eventsub.listen_channel_subscription_gift(user.id, self.on_subscribe_gift)
        print('Listening for Twitch events.')

    def get_character_name_from_emotes(self, message):
        character_keys = re.findall(r'\broughc3\w+\b', message, flags=re.IGNORECASE)
        message = re.sub(r'\broughc3\w+\b', '', message, flags=re.IGNORECASE)
        if len(character_keys) == 0:
            character_name = next(iter(self.config['emotes'].items()))[1]
        else:
            character_name = self.config['emotes'][character_keys[0]]

        return character_name, message

    @staticmethod
    async def on_ready(ready_event: EventData):
        log.info('Bot is ready for work, joining channel')
        await ready_event.chat.join_room('roughcookie')
        log.info('Bot joined channel')

    @staticmethod
    async def print_user_rules(cmd: ChatCommand):
        result = TwitchNotification.fetch_rules()
        rules = '\n\n'.join(json.loads(result.text))
        await cmd.reply(f'Here\'s the rules:\n\n{rules}')

    async def run_chatbot(self, twitch):
        log.info('Starting chat bot')
        chat = await Chat(twitch)
        chat.register_event(ChatEvent.READY, self.on_ready)
        chat.register_command('rules', self.print_user_rules)
        chat.start()
        log.info('Chat bot started. Waiting for ready event.')

    async def begin(self):
        # create the api instance and get user auth either from storage or website
        twitch = await Twitch(self.APP_ID, self.APP_SECRET)
        helper = UserAuthenticationStorageHelper(twitch, self.TARGET_SCOPES)
        await helper.bind()

        notification_task = asyncio.create_task(self.run_twitch_listeners(twitch))
        chatbot_task = asyncio.create_task(self.run_chatbot(twitch))

        await asyncio.gather(notification_task, chatbot_task)


if __name__ == "__main__":
    twitch_input = TwitchNotification()
    asyncio.run(twitch_input.begin())
