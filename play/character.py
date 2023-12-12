import time

import ai
from sessions.rules import Rule
from settings import sierra_settings as settings
from utils.audio_player import AudioPlayer
from utils.logging import log


class Character:
    def __init__(self, glob, yaml):
        self.path = glob
        self.name = yaml.get('name', None)

        self.chat_model_override = yaml.get('chat_model_override', None)
        self.motivation = yaml.get('motivation', None)
        self.rules = yaml.get('rules', None)
        self.voice = yaml.get('voice', None)
        self.user_rules = []

    def __setstate__(self, state):
        self.name = state.get('name', None)
        self.chat_model_override = state.get('chat_model_override', None)
        self.motivation = state.get('motivation', None)
        self.rules = state.get('rules', None)
        self.voice = state.get('voice', None)
        self.user_rules = state.get('user_rules', [])

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['image', 'font']:
            del state[key]
        return state

    def add_rule(self, rule):
        self.user_rules.append(Rule(rule))

    def chat(self, prompt, task, summary, history):

        response = ai.modules.get(settings.chat.module).Chat.send(prompt, task, history, summary)

        log.info(f'Character ({self.name}): {response}')

        audio_file = None
        if settings.speech.enabled:
            audio_file = ai.modules.get(settings.speech.module).Speak.send(response, self.voice)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, audio_file

    async def speak(self, ai_output, playback):
        log.info(f'Character ({self.name}) speaking')
        with (AudioPlayer(ai_output) as audio_player):

            for _ in audio_player.play_audio_chunk():
                while playback.paused:
                    time.sleep(1)
