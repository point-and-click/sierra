import asyncio
from datetime import datetime

import ai
import plugins
from play.chat import Chat
from play.rules import Rule, RuleType
from play.speech import Speech
from play.subtitles import Subtitles
from settings import sierra_settings as settings
from utils.format import truncate
from utils.logging import log
from windows.character import CharacterWindow


class Character:
    def __init__(self, glob, yaml):
        self.name = yaml.get('name', None)
        self.task = None
        self.rules = {RuleType.PERMANENT: [Rule(rule) for rule in yaml.get('chat', {}).get('rules', [])],
                      RuleType.TEMPORARY: []}

        self.personality = yaml.get('chat', {}).get('personality', {})
        self.voice = yaml.get('speech', {}).get('voice', {})

        self.chat_ai = ai.load(yaml.get('chat', {}).get('service', 'open_ai'), ai.Function.CHAT)()
        self.speak_ai = ai.load(yaml.get('speech', {}).get('service', 'elevenlabs'), ai.Function.SPEAK)()
        self.transcribe_ai = ai.load(yaml.get('transcribe', {}).get('service', 'open_ai'), ai.Function.TRANSCRIBE)()

        self.path = glob
        self.image = yaml.get('visual', None).get('image', None)

        self.window = None

    def __setstate__(self, state):
        self.name = state.get('name', None)
        self.motivation = state.get('motivation', None)
        self.rules = state.get('chat', {}).get('rules', {RuleType.PERMANENT: [], RuleType.TEMPORARY: []})
        self.voice = state.get('voice', None)

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['image', 'window']:
            del state[key]
        return state

    def assign_task(self, task):
        self.task = task

        self.window = CharacterWindow(self)

    def add_rule(self, rule_type, rule):
        self.rules[rule_type].append(Rule(rule))

    def serialize_rules(self, rule_type):
        return ''.join([f'{rule.text} ' for rule in self.rules.get(rule_type)])

    def converse(self, prompt, session):
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")

        plugins.hook(plugins.HookType.PRE_CHAT)
        log.info('Chat AI: Chat completion requested.')
        chat = Chat(timestamp, self.chat_ai.send(prompt, session, self))
        plugins.hook(plugins.HookType.POST_CHAT)

        plugins.hook(plugins.HookType.PRE_SPEECH)
        log.info('Speech AI: Speech synthesis requested.')
        speech = Speech(timestamp, *self.speak_ai.send(chat.response, self.voice))
        plugins.hook(plugins.HookType.POST_SPEECH)

        plugins.hook(plugins.HookType.PRE_TRANSCRIBE)
        log.info('Transcribe AI: Transcribing synthesized audio.')
        subtitles = Subtitles(timestamp, self.transcribe_ai.send(speech.path))
        plugins.hook(plugins.HookType.POST_TRANSCRIBE)

        return chat, speech, subtitles

    async def respond(self, ai_output):
        if settings.transcribe.reconstitute:
            ai_output.subtitles.reconstitute(ai_output.chat.response)

        log.info(f'\tCharacter ({self.name}): {truncate(ai_output.chat.response, 256)}')
        character_task = asyncio.create_task(self.window.speak(ai_output.speech))
        subtitle_task = asyncio.create_task(self.window.manager.subtitles.play(ai_output.subtitles))

        await asyncio.gather(character_task, subtitle_task)
