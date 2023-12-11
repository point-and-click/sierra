import asyncio
import pickle
import queue
import sys
from datetime import datetime
from threading import Thread

import pygame
from pynput import keyboard

from ai.open_ai import ChatGPT, MessageRole
from ai.output import AiOutput
from play import characters, tasks
from sessions.history import History
from settings import settings
from utils.logging import log
from utils.logging.format import nl, tab

ACCEPT_SUMMARY_BINDING = keyboard.Key.ctrl_r
DECLINE_SUMMARY_BINDING = keyboard.Key.shift_r


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

            self.characters = {
                character_name: characters.get(character_name) for character_name in settings.characters
            }
            self.tasks = {
                task_name: tasks.get(task_name) for task_name in settings.tasks
            }

            self.user_rules = []
            self.history = []
            self.summary = None

            self.output_queue = queue.Queue()
            self.input_queue = queue.Queue()

            self.response_word_count = 0

            self.playback = Playback()
            self.screen = None
            self.listener = None
            self.accepted_summary = False
            self.declined_summary = False
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

    async def process(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.screen.fill((0, 255, 0))
        pygame.display.update()
        pygame.display.set_caption("Sierra")
        input_task = asyncio.create_task(self.process_input())
        output_task = asyncio.create_task(self.process_output())

        await asyncio.gather(input_task, output_task)

    async def process_input(self):
        while True:
            if not self.input_queue.empty():
                input_thread = Thread(target=dummy, args=(self, self.input_queue.get()))
                input_thread.start()
            else:
                await asyncio.sleep(0.1)

    async def process_output(self):
        while True:
            if not self.output_queue.empty():
                await self.play_output(self.output_queue.get())
            else:
                await asyncio.sleep(0.1)

    async def play_output(self, output):
        await output.character.speak(output, self.playback, self.screen)
        self.screen.fill((0, 255, 0))
        pygame.display.update()

    def get_chat_response(self, ai_input):
        self.pre_process()

        log.info(f"Getting chat response for: {ai_input.message}")
        prompt = ai_input.message
        character = self.characters[ai_input.character]

        messages = [
            {"role": MessageRole.SYSTEM.value,
             "content": 'You will be playing the part of multiple characters. Respond as the character described.'},
            {"role": MessageRole.USER.value,
             "content": f'{self.tasks[0].description} {character.motivation} {character.rules}'},
            {"role": self.summary.role, "content": self.summary.content},
            *[{"role": entry.role, "content": entry.content} for entry in self.history[-settings.history.max:]],
            {"role": MessageRole.USER.value,
             "content": f'{" ".join([rule.text for rule in character.user_rules])} {prompt}'}
        ]
        response, usage, audio_file = character.chat(messages)

        if audio_file is not None:
            self.output_queue.put(AiOutput(character, audio_file))

        self.response_word_count += len(response.split())

        if self.tasks[0].summary.user:
            self.history.append(History(MessageRole.USER.value, prompt))
        if self.tasks[0].summary.assistant:
            self.history.append(History(MessageRole.ASSISTANT.value, response))

        self.post_process()

    def pre_process(self):
        for character in self.characters.values():
            character.user_rules = [rule for rule in character.user_rules if rule.expiration_time > datetime.now()]
            log.info(f'Rules:\n{(nl + tab).join([rule.text for rule in character.user_rules])}')

    def post_process(self):
        history_word_count = sum([len(entry.content.split()) for entry in self.history])

        if history_word_count > settings.summary.max_words:
            self.summarize()

        self.save()

    def summarize(self):
        self.accepted_summary = False
        self.declined_summary = False

        messages = [
            *[{"role": entry.role, "content": entry.content} for entry in self.history],
            {"role": "system", "content": self.tasks[0].summary.description}
        ]

        summary, usage = ChatGPT.chat(messages)
        self.summary = History(MessageRole.ASSISTANT.value, summary)
        log.info(f'OpenAI: Summary: {self.summary}')

        if settings.summary.review:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()

            log.info('Waiting to accept summary.')
            while not self.accepted_summary and not self.declined_summary:
                pass

            self.listener.stop()

            if self.declined_summary:
                log.info('Summary declined.')
                return False

        log.info('Summary accepted.')
        return True

    def on_press(self, key):
        if key == ACCEPT_SUMMARY_BINDING:
            self.accepted_summary = True
        elif key == DECLINE_SUMMARY_BINDING:
            self.declined_summary = True
        elif key == keyboard.Key.right and self.playback.paused:
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


def dummy(obj: Session, ai_input):
    obj.get_chat_response(ai_input)
    return sys.exit()
