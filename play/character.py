import time

import ai
from play.rules import Rule, RuleType
from settings import sierra_settings as settings
from utils.audio_player import AudioPlayer
from utils.logging import log
from windows.character import CharacterWindow


class Character:
    def __init__(self, glob, yaml):
        self.name = yaml.get('name', None)
        self.task = None

        self.motivation = yaml.get('motivation', None)
        self.rules = {RuleType.PERMANENT: yaml.get('rules', None), RuleType.TEMPORARY: []}
        self.voice = yaml.get('voice', None)

        self.overrides = yaml.get('overrides', None)

        self.chat_ai = ai.load(settings.chat.module, ai.Function.CHAT)()
        self.speak_ai = ai.load(settings.speech.module, ai.Function.SPEAK)()

        self.path = glob
        self.image = yaml.get('visual', None).get('image', None)

        self.window = CharacterWindow(self)

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

    def assign_task(self, task):
        self.task = task

    def add_rule(self, rule):
        self.user_rules.append(Rule(rule))

    def chat(self, prompt, summary, history):
        response = self.chat_ai.send(prompt, self, self.task, history, summary,)

        log.info(f'Character ({self.name}): {response}')

        audio_file = None
        if settings.speech.enabled:
            audio_file = self.speak_ai.send(response, self.voice)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, audio_file

    async def speak(self, ai_output, playback):
        self.window.hidden = False
        log.info(f'Character ({self.name}) speaking')
        with (AudioPlayer(ai_output) as audio_player):

            for _ in audio_player.play_audio_chunk():
                while playback.paused:
                    time.sleep(1)
        self.window.hidden = True
