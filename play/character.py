import asyncio
from datetime import datetime

import ai
import plugins
import windows
from play.chat import Chat
from play.rules import Rule, RuleType
from play.speech import Speech
from play.subtitles import Subtitles
from settings import sierra
from utils.format import truncate
from utils.logging import log
from windows.character import CharacterWindow


class Character:
    """
    `Character`
    """
    def __init__(self, glob, yaml):
        self._yaml = yaml
        self.path = glob

        self.name = self._yaml.get('name', None)
        self.task = None
        self.rules = {RuleType.PERMANENT: [Rule(rule) for rule in self._yaml.get('chat', {}).get('rules', [])],
                      RuleType.TEMPORARY: []}

        self.personality = self._yaml.get('chat', {}).get('personality', {})
        self.voice = self._yaml.get('speech', {}).get('voice', {})

        self.skip_chat = False
        self.chat_ai = ai.load(
            self._yaml.get('chat', {}).get('service', sierra.chat.service),
            ai.Function.CHAT
        )()

        self.skip_speech = False
        self.speak_ai = ai.load(
            self._yaml.get('speech', {}).get('service', sierra.speech.service),
            ai.Function.SPEAK
        )()

        self.skip_transcribe = False
        self.transcribe_ai = ai.load(
            self._yaml.get('transcribe', {}).get('service', sierra.transcribe.service),
            ai.Function.TRANSCRIBE
        )()

        self.image = self._yaml.get('visual', None).get('image', None)

        self.window = None

    def __setstate__(self, state):
        """
        :param state:
        :return:
        """
        self._yaml = state.get('_yaml', None)
        self.path = state.get('path', None)

        self.name = state.get('name', None)
        self.task = state.get('task', None)
        self.rules = state.get('rules', {RuleType.PERMANENT: [], RuleType.TEMPORARY: []})
        self.personality = state.get('personality', None)

        self.voice = state.get('voice', None)

        self.image = state.get('image', None)

        self.skip_chat = state.get('skip_chat', False)
        self.chat_ai = ai.load(
            self._yaml.get('chat', {}).get('service', sierra.chat.service),
            ai.Function.CHAT
        )()

        self.skip_speech = state.get('skip_speech', False)
        self.speak_ai = ai.load(
            self._yaml.get('speech', {}).get('service', sierra.speech.service),
            ai.Function.SPEAK
        )()

        self.skip_transcribe = state.get('skip_transcribe', False)
        self.transcribe_ai = ai.load(
            self._yaml.get('transcribe', {}).get('service', sierra.transcribe.service),
            ai.Function.TRANSCRIBE
        )()

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['window']:
            del state[key]
        return state

    def assign_task(self, task):
        """
        :param task: Task
        """
        self.task = task

        self.window = CharacterWindow(self)

    def add_rule(self, rule_type, rule):
        """
        :param rule_type: RuleType
        :param rule: TemporaryRule | Rule
        """
        self.rules[rule_type].append(rule)

    def serialize_rules(self, rule_type):
        """
        :param rule_type: RuleType
        :return: str
        """
        return ', '.join([rule.text for rule in self.rules.get(rule_type)])

    def converse(self, prompt, session):
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S+%f")

        chat = Chat(timestamp)
        plugins.hook(plugins.HookType.PRE_CHAT, session, self, chat)
        if not self.skip_chat:
            log.info('Chat AI: Chat completion requested.')
            chat.set(self.chat_ai.send(prompt, session, self))
        plugins.hook(plugins.HookType.POST_CHAT, session, self, chat)
        log.debug(f'Chat AI: {chat}')

        speech = Speech(timestamp)
        plugins.hook(plugins.HookType.PRE_SPEECH, session, self, chat, speech)
        if not self.skip_speech:
            log.info('Speech AI: Speech synthesis requested.')
            speech.set(*self.speak_ai.send(chat.response, self.voice))
        plugins.hook(plugins.HookType.POST_SPEECH, session, self, chat, speech)
        log.debug(f'Speech AI: {speech}')

        subtitles = Subtitles(timestamp)
        plugins.hook(plugins.HookType.PRE_TRANSCRIBE, session, self, chat, speech, subtitles)
        if not self.skip_transcribe:
            log.info('Transcribe AI: Transcribing synthesized audio.')
            subtitles.set(self.transcribe_ai.send(speech.path))
        plugins.hook(plugins.HookType.POST_TRANSCRIBE, session, self, chat, speech, subtitles)
        log.debug(f'Transcribe AI: {subtitles}')

        return chat, speech, subtitles

    async def respond(self, ai_output):
        """
        :param ai_output:
        """
        if sierra.transcribe.reconstitute:
            ai_output.subtitles.reconstitute(ai_output.chat.response)

        log.info(f'\tCharacter ({self.name}): {truncate(ai_output.chat.response, 256)}')
        character_task = asyncio.create_task(self.window.speak(ai_output.speech))
        subtitle_task = asyncio.create_task(self.window.manager.subtitles.play(ai_output.subtitles))

        await asyncio.gather(character_task, subtitle_task)
