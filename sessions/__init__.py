import asyncio
import pickle
import queue
import sys
from datetime import datetime
from threading import Thread

import ai

from ai.output import Output
from play import Play
from play.rules import RuleType
from sessions.history import Moment
from settings import sierra_settings as settings

from utils.logging import log
from utils.logging.format import nl, tab
from windows import Manager
from windows.subtitles import SubtitlesWindow


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

            self.windows = Manager()
            self.windows.subtitles = SubtitlesWindow()

            available_characters = Play.characters()
            self.characters = {
                character_name: available_characters.get(character_name) for character_name in settings.characters
            }
            available_tasks = Play.tasks()
            self.tasks = {
                task_name: available_tasks.get(task_name) for task_name in settings.tasks
            }

            # TODO: Rethink assigning tasks to characters
            for character in self.characters.values():
                character.assign_task(list(self.tasks.values())[0])

            self.history = []
            self.summary = None

            self.output_queue = queue.Queue()
            self.input_queue = queue.Queue()

            self.response_word_count = 0

            self._initialized = True

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['input_queue', 'output_queue', 'windows']:
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
                output = self.output_queue.get()
                await output.character.respond(output)
            else:
                await asyncio.sleep(0.1)

    def get_chat_response(self, ai_input):
        self.pre_process()

        log.info(f"Getting chat response for: {ai_input.message}")
        prompt = ai_input.message
        character = self.characters[ai_input.character]

        response, audio_bytes = character.converse(prompt, self.summary, self.history)

        if audio_bytes is not None:
            self.output_queue.put(Output(character, audio_bytes))

        self.response_word_count += len(response.split())

        if settings.summary.user:
            self.history.append(Moment(ai.Role.USER.value, prompt))
        if settings.summary.assistant:
            self.history.append(Moment(ai.Role.ASSISTANT.value, response))

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
            {"role": "system", "content": list(self.tasks.values())[0].summary.description}
        ]

        summary = ai.modules.get(settings.chat.module).Chat.send(messages)
        self.summary = Moment(ai.Role.ASSISTANT.value, summary)
        log.info(f'OpenAI: Summary: {self.summary}')

        return True

    def save(self):
        pass
        # pickle.dump(self, open(f'saves/{self.name}.sierra', 'wb'))

    def load(self, file_name):
        obj = pickle.load(open(file_name, 'rb'))
        self.characters = obj.characters
        for character in self.characters.values():
            log.info(
                f'''Loaded rules for ({character.name}):\n\t{f"{nl}{tab}".join(
                    [repr(entry) for entry in character.rules])}'''
            )
        self.history = obj.history
        log.info(
            f'Loaded history:\n\t{f"{nl}{tab}".join([repr(entry) for entry in self.history])}'
        )


def input_target(session: Session, ai_input):
    session.get_chat_response(ai_input)
    return sys.exit()
