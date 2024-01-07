import asyncio

from pynput import keyboard

import ai
from play.rules import Rule, RuleType, TemporaryRule
from settings import sierra_settings as settings
from utils.logging import log
from windows.character import CharacterWindow


class Character:
    def __init__(self, glob, yaml):
        self.play = False
        self.name = yaml.get('name', None)
        self.task = None

        self.motivation = yaml.get('chat', {}).get('motivation', None)
        self.rules = {RuleType.PERMANENT: yaml.get('rules', []), RuleType.TEMPORARY: []}
        self.voice = yaml.get('speech', {}).get('voice', None)

        self.overrides = yaml.get('overrides', None)
        self.chat_model_override = yaml.get('chat_model_override', None)

        self.chat_ai = ai.load(settings.chat.module, ai.Function.CHAT)()
        self.speak_ai = ai.load(settings.speech.module, ai.Function.SPEAK)()

        self.path = glob
        self.image = yaml.get('visual', None).get('image', None)

        self.window = None
        self.listener = keyboard.Listener(on_release=self.on_release)
        self.listener.start()

    def __setstate__(self, state):
        self.name = state.get('name', None)
        self.chat_model_override = state.get('chat_model_override', None)
        self.motivation = state.get('motivation', None)
        self.rules = state.get('rules', None)
        self.voice = state.get('voice', None)
        self.rules = state.get('rules', [])

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['image', 'window']:
            del state[key]
        return state

    def assign_task(self, task):
        self.task = task

        self.window = CharacterWindow(self)

    def add_rule(self, rule_type, rule):
        match rule_type:
            case RuleType.TEMPORARY:
                self.rules[rule_type].append(TemporaryRule(rule))
            case RuleType.PERMANENT:
                self.rules[rule_type].append(Rule(rule))

    def serialize_rules(self, rule_type):
        return ''.join([f'{rule.text} ' for rule in self.rules.get(rule_type)])

    def converse(self, prompt, summary, history):
        response = self.chat_ai.send(prompt, self, self.task, history, summary, self.chat_model_override)

        log.info(f'Character ({self.name}): {response}')

        if settings.speech.enabled:
            audio_bytes = self.speak_ai.send(response, self.voice)
            return response, audio_bytes
        else:
            log.info('Speech synthesis is disabled. Skipping.')
            return response, None, None

    async def respond(self, ai_output):
        log.info(f'Character ({self.name}) speaking')

        while not self.play:
            await asyncio.sleep(0.1)
        character_task = asyncio.create_task(self.window.speak(ai_output.audio))
        # subtitle_task = asyncio.create_task(self.window.manager.subtitles.play(ai_output.subtitles.get('segments')))
        self.play = False
        await asyncio.gather(character_task)

    def on_release(self, key: keyboard.Key | keyboard.KeyCode):
        match type(key):
            case keyboard.Key:
                number = key.value.vk
            case keyboard.KeyCode:
                number = key.vk
            case _:
                number = None

        if number == 34:
            self.play = True