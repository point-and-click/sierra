import asyncio
import pickle
import queue
import sys
from datetime import datetime
from threading import Thread

from pynput import keyboard

import ai
import windows
from ai.output import Output
from play import Play
from play.rules import RuleType
from sessions.history import History
from settings import sierra_settings as settings
from utils.logging import log
from utils.logging.format import nl, tab


class Session:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            self.ui = windows.Manager()

            available_characters = Play.characters()
            self.characters = {
                character_name: available_characters.get(character_name) for character_name in settings.characters
            }
            available_tasks = Play.tasks()
            self.tasks = {
                task_name: available_tasks.get(task_name) for task_name in settings.tasks
            }

            self.history = []
            self.summary = None

            self.output_queue = queue.Queue()
            self.input_queue = queue.Queue()

            self.response_word_count = 0

            self.playback = Playback()

            self._initialized = True

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['listener', 'input_queue', 'output_queue', 'screen']:
            del state[key]
        return state

    def __repr__(self):
        return '\n'.join(
            [
                '\tHistory:',
                *[f'\t\t{entry.role}: {entry.content}' for entry in self.history]
            ]
        )

    async def gather(self):
        input_task = asyncio.create_task(self.process_input())
        output_task = asyncio.create_task(self.process_output())

        await asyncio.gather(input_task, output_task)

    async def process_input(self):
        while True:
            if not self.input_queue.empty():
                input_thread = Thread(target=input_target, args=(self, self.input_queue.get()))
                input_thread.start()
            else:
                await asyncio.sleep(0.1)

    async def process_output(self):
        while True:
            if not self.output_queue.empty():
                await self.play(self.output_queue.get())
            else:
                await asyncio.sleep(0.1)

    async def play(self, output):
        await output.character.speak(output, self.playback)

    def get_chat_response(self, ai_input):
        self.pre_process()

        log.info(f"Getting chat response for: {ai_input.message}")
        prompt = ai_input.message
        character = self.characters[ai_input.character]

        response, audio_file = character.chat(prompt, self.tasks, self.summary, self.history)

        if audio_file is not None:
            self.output_queue.put(Output(character, audio_file))

        self.response_word_count += len(response.split())

        if self.tasks[0].summary.user:
            self.history.append(History(ai.Role.USER.value, prompt))
        if self.tasks[0].summary.assistant:
            self.history.append(History(ai.Role.ASSISTANT.value, response))

        self.post_process()

    def pre_process(self):
        for character in self.characters.values():
            character.rules[RuleType.TEMPORARY] = [
                rule for rule in character.rules[RuleType.TEMPORARY] if rule.expiration_time > datetime.now()
            ]
            log.info(f'Rules:\n{(nl + tab).join([rule.text for rule in character.rules[RuleType.TEMPORARY]])}')

    def post_process(self):
        history_word_count = sum([len(entry.content.split()) for entry in self.history])

        if history_word_count > settings.summary.max_words:
            self.summarize()

        self.save()

    def summarize(self):

        messages = [
            *[{"role": entry.role, "content": entry.content} for entry in self.history],
            {"role": "system", "content": self.tasks[0].summary.description}
        ]

        summary = ai.modules.get(settings.chat.module).Chat.send(messages)
        self.summary = History(ai.Role.ASSISTANT.value, summary)
        log.info(f'OpenAI: Summary: {self.summary}')

        return True

    def on_press(self, key):
        if key == keyboard.Key.right and self.playback.paused:
            self.playback.paused = False
            log.info('Unpaused')
        elif key == keyboard.Key.left and not self.playback.paused:
            self.playback.paused = True
            log.info('Paused')

    def save(self):
        pickle.dump(self, open(f'saves/{self.name}.sierra', 'wb'))

    def load(self, file_name):
        obj = pickle.load(open(file_name, 'rb'))
        self.characters = obj.characters
        for character in self.characters.values():
            log.info(
                f'''Loaded rules for ({character.name}):\n\t{f"{nl}{tab}".join(
                    [repr(entry) for entry in character.user_rules])}'''
            )
        self.history = obj.history
        log.info(
            f'Loaded history:\n\t{f"{nl}{tab}".join([repr(entry) for entry in self.history])}'
        )


class Playback:
    def __init__(self):
        self.paused = False


def input_target(session: Session, ai_input):
    session.get_chat_response(ai_input)
    return sys.exit()
