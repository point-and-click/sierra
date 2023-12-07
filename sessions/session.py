import asyncio
import pickle
import queue
import sys
from datetime import datetime
from threading import Thread

import pygame
from decouple import config
from pynput import keyboard

from ai import open_ai
from ai.open_ai import ChatGPT, MessageRole
from ai.output import AiOutput
from play import characters, tasks
from sessions.history import History
from utils.logging import log
from utils.logging._format import nl, tab
from utils.pygame_manager import SCREEN

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
            self.characters = {character_name: characters.get(character_name) for character_name in
                               config('CHARACTERS').split(',')}

            self.task = tasks.get(config('TASK'))

            self.user_rules = []
            self.history = []
            self.output_queue = queue.Queue()
            self.input_queue = queue.Queue()

            self.response_word_count = 0

            self.playback = Playback()
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
        for key in ['listener', 'input_queue', 'output_queue']:
            del state[key]
        return state

    def __repr__(self):
        return '\n'.join(
            [
                f'\tHistory:',
                *[f'\t\t{entry.role}: {entry.content}' for entry in self.history]
            ]
        )

    async def process(self):
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
        await output.character.speak(output, self.playback)
        SCREEN.fill((0, 255, 0))
        pygame.display.update()

    def get_chat_response(self, ai_input):
        self.pre_process()

        log.info(f"Getting chat response for: {ai_input.message}")
        prompt = ai_input.message
        character = self.characters[ai_input.character]

        messages = [
            {"role": MessageRole.SYSTEM.value,
             "content": f'You will be playing the part of multiple characters. Respond as the character described. Ignore character names within parentheses. No need to announce which character is speaking. I will understand.'},
            {"role": MessageRole.USER.value,
             "content": f'{self.task.description} {character.motivation} {character.rules}'},
            *[{"role": entry.role, "content": entry.content} for entry in self.history],
            {"role": MessageRole.USER.value,
             "content": f'{" ".join([rule.text for rule in character.user_rules])} {prompt}'}
        ]
        response, usage, audio_file = character.chat(messages)

        if audio_file is not None:
            self.output_queue.put(AiOutput(character, audio_file))

        if config('OPENAI_CHAT_COMPLETION_REMOVE_FORMAT', cast=bool):
            response = response.replace('\n', '')

        open_ai.TOKENS += usage.get("total_tokens")

        self.response_word_count += len(response.split())

        if self.task.summary.user:
            self.history.append(History(MessageRole.USER.value, prompt))
        if self.task.summary.assistant:
            self.history.append(History(MessageRole.ASSISTANT.value, f'({character.name}): {response}'))

        self.post_process(usage)

    def pre_process(self):
        for character in self.characters.values():
            character.user_rules = [rule for rule in character.user_rules if rule.expiration_time > datetime.now()]
            log.info(f'Rules:\n{(nl + tab).join([rule.text for rule in character.user_rules])}')

    def post_process(self, usage):
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

        self.save()

    def summarize(self):
        self.accepted_summary = False
        self.declined_summary = False

        messages = [
            *[{"role": entry.role, "content": entry.content} for entry in self.history.history_lines],
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
                f'Loaded rules for ({character.name}):\n\t{f"{nl}{tab}".join([repr(entry) for entry in character.user_rules])}'
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
