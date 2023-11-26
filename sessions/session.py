import asyncio
import pickle
import queue
from datetime import datetime

import pygame
from decouple import config
from pynput import keyboard

from ai import open_ai
from ai.open_ai import ChatGPT, MessageRole
from async_input import AsyncInput
from play import characters, tasks
from sessions.history import History
from sessions.recorder import Recorder
from extensions.twitch_input import TwitchNotification
from utils.logging import log
from utils.logging._format import nl, tab
from utils.word_wrap import WordWrap

ACCEPT_SUMMARY_BINDING = keyboard.Key.ctrl_r
DECLINE_SUMMARY_BINDING = keyboard.Key.shift_r


class Session:
    def __init__(self, character_names, task_name):

        self.name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.characters = []
        for character_name in character_names.split(','):
            self.characters.append(characters.get(character_name))

        self.task = tasks.get(task_name)

        self.history = []
        self.input_queue = queue.Queue()

        self.response_word_count = 0

        self.listener = None
        self.accepted_summary = False
        self.declined_summary = False

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['listener']
        del state['characters']
        del state['input_queue']
        return state

    # The way this works is maddening.
    def __setstate__(self, state):
        self.history = state.get('history', [])

    def __repr__(self):
        return '\n'.join(
            [
                f'\tHistory:',
                *[f'\t\t{entry.role}: {entry.content}' for entry in self.history]
            ]
        )

    async def begin(self):
        pygame.init()
        screen = pygame.display.set_mode((275, 338))
        screen.fill((0, 255, 0))
        pygame.display.update()
        pygame.display.set_caption("Sierra")

        twitch_input = TwitchNotification(self.input_queue)
        recorder = Recorder(len(self.characters), self.input_queue)
        loop = asyncio.get_event_loop()

        # async_input = AsyncInput(self.input_queue)
        # asyncio.run_coroutine_threadsafe(async_input.put_in_queue(), loop=loop)
        asyncio.run_coroutine_threadsafe(twitch_input.run(), loop=loop)
        asyncio.run_coroutine_threadsafe(recorder.run(), loop=loop)

        character_number = 0
        while True:
            while self.input_queue.empty():
                await asyncio.sleep(0.1)
                # character_number = self.recorder.record('temp/input.wav')

            prompt = self.input_queue.get()
            with open('obs_ai.txt', "w") as f:
                f.write("")
            with open('obs_player.txt', "w") as f:
                f.write(WordWrap.word_wrap(prompt, 75))

            messages = [
                {"role": MessageRole.SYSTEM.value, "content": f'You will be playing the part of multiple characters. In each prompt you will be given specific rules to the character you will be playing. Respond as the character described.'},
                {"role": MessageRole.USER.value,
                 "content": f'{self.task.description} {self.characters[character_number].motivation} {self.characters[character_number].rules} {prompt}'},
                *[{"role": entry.role, "content": entry.content} for entry in self.history],
                {"role": MessageRole.USER.value, "content": f'{prompt}'}
            ]
            response, usage = self.characters[character_number].chat(messages, screen)

            if config('OPENAI_CHAT_COMPLETION_REMOVE_FORMAT', cast=bool):
                response = response.replace('\n', '')

            open_ai.TOKENS += usage.get("total_tokens")

            self.response_word_count += len(response.split())

            if self.task.summary.user:
                self.history.append(History(MessageRole.USER.value, prompt))
            if self.task.summary.assistant:
                self.history.append(History(MessageRole.ASSISTANT.value, response))

            self.assess(usage)
            self.save()

    def assess(self, usage):
        history_word_count = sum([len(entry.content.split()) for entry in self.history])

        if config('DEBUG_USAGE', cast=bool):
            log.info(
                f'Usage: OpenAI'
                f'\n\tPrompt: '
                f'{usage.get("prompt_tokens")} tokens'
                f'\n\tCompletion: '
                f'{usage.get("completion_tokens")} tokens'
                f'\n\tTotal: '
                f'{usage.get("total_tokens")} tokens'
                f'\n\tSession: '
                f'{open_ai.TOKENS} tokens'
            )
            log.info(
                f'Usage: ElevenLabs'
                f'\n\tSummary: '
                f'{history_word_count} words / {config("OPENAI_CHAT_COMPLETION_MAX_WORD_COUNT", cast=int)} words'
                f'\n\tSession: '
                f'{self.response_word_count} words'
            )

        if history_word_count > config("OPENAI_CHAT_COMPLETION_MAX_WORD_COUNT", cast=int):
            self.summarize()

    def summarize(self):
        self.accepted_summary = False
        self.declined_summary = False

        messages = [
            *[{"role": entry.role, "content": entry.content} for entry in self.history],
            {"role": "system", "content": self.task.summary.description}
        ]

        summary, usage = ChatGPT.chat(messages)
        log.info(f'OpenAI: Summary: {summary}')

        if config("REVIEW_SUMMARY", cast=bool):
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()

            log.info('Waiting to accept summary.')
            while not self.accepted_summary and not self.declined_summary:
                pass

            self.listener.stop()

            if self.declined_summary:
                log.info('Summary declined.')
                return False

        self.history = ([History(MessageRole.ASSISTANT.value, summary)]
                        + self.history[-config('PRESERVE_HISTORY_LINES', cast=int):])

        log.info('Summary accepted.')
        return True

    def save(self):
        pickle.dump(self, open(f'saves/{self.name}.sierra', 'wb'))

    def load(self, file_name):
        self.history = pickle.load(open(file_name, 'rb')).history
        log.info(
            f'Loaded history:\n\t{f"{nl}{tab}".join([repr(entry) for entry in self.history])}'
        )

    def on_press(self, key):
        if key == ACCEPT_SUMMARY_BINDING:
            self.accepted_summary = True
        elif key == DECLINE_SUMMARY_BINDING:
            self.declined_summary = True
