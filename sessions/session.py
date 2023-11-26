import asyncio
import pickle
import queue
from datetime import datetime

import pygame
from decouple import config
from pynput import keyboard

from ai import Usage
from ai.text.open_ai import ChatGPT, MessageRole
from play import characters, tasks
from sessions.history import History
from utils.logging import log
from utils.logging.format import nl, tab
from utils.text import word_wrap

ACCEPT_SUMMARY_BINDING = keyboard.Key.ctrl_r
DECLINE_SUMMARY_BINDING = keyboard.Key.shift_r


class Session:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.characters = []
        for character_name in config('CHARACTERS').split(','):
            self.characters.append(characters.get(character_name))

        self.task = tasks.get(config('TASK'))

        self.history = []
        self.input_queue = queue.Queue()

        self.listener = None
        self.accepted_summary = None

        self.usage = Usage()

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

        character_number = 0
        while True:
            while self.input_queue.empty():
                await asyncio.sleep(0.1)
                # character_number = self.recorder.record('temp/input.wav')

            prompt = self.input_queue.get().message
            with open('obs_ai.txt', "w") as f:
                f.write("")
            with open('obs_player.txt', "w") as f:
                f.write(word_wrap(prompt, 75))

            messages = [
                {"role": MessageRole.SYSTEM.value,
                 "content": f'You will be playing the part of multiple characters. In each prompt you will be given specific rules to the character you will be playing. Respond as the character described.'},
                {"role": MessageRole.USER.value,
                 "content": f'{self.task.description} {self.characters[character_number].motivation} {self.characters[character_number].rules} {prompt}'},
                *[{"role": entry.role, "content": entry.content} for entry in self.history],
                {"role": MessageRole.USER.value, "content": f'{prompt}'}
            ]
            response, usage = self.characters[character_number].chat(messages, screen)

            if config('OPENAI_CHAT_COMPLETION_REMOVE_FORMAT', cast=bool):
                response = response.replace('\n', '')

            self.usage.prompt_tokens = usage.get("prompt_tokens")
            self.usage.response_tokens = usage.get("completion_tokens")
            self.usage.prompt_words = len(prompt.split())
            self.usage.response_words = len(response.split())
            self.usage.prompt_characters = len(prompt)
            self.usage.response_characters = len(response)

            if self.task.summary.user:
                self.history.append(History(MessageRole.USER.value, prompt))
            if self.task.summary.assistant:
                self.history.append(History(MessageRole.ASSISTANT.value, response))

            self.assess()
            self.save()

    def assess(self):
        if config('DEBUG_USAGE', cast=bool):
            log.info(
                f'Usage: Text Completion'
                f'\n\tPrompt: '
                f'{self.usage.prompt_words} words | {self.usage.prompt_tokens} tokens'
                f'\n\tCompletion: '
                f'{self.usage.response_words} words | {self.usage.response_tokens} tokens'
            )
            log.info(
                f'Usage: Speech Synthesis'
                f'\n\tSynthesis: '
                f'{self.usage.response_characters} words'
            )

        if (sum([len(entry.content.split()) for entry in self.history])
                > config("OPENAI_CHAT_COMPLETION_MAX_WORD_COUNT", cast=int)):
            self.summarize()

    def summarize(self):
        self.accepted_summary = None

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
            while self.accepted_summary is None:
                continue

            self.listener.stop()

            if self.accepted_summary:
                log.info(f'OpenAI: Summary: Declined')
                return
            else:
                log.info(f'OpenAI: Summary: Accepted')

        self.history = [History(MessageRole.ASSISTANT.value, summary)].extend(
            self.history[-config('PRESERVE_HISTORY_LINES', cast=int):])

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
            self.accepted_summary = False
