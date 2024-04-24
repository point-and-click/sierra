import asyncio
import pickle
import queue
import sys
from datetime import datetime
from threading import Thread

from ai.output import Output
from play import Play
from play.rules import RuleType
from play.history import Moment, History
from settings import sierra

from utils.logging import log
from utils.logging.format import nl, tab
from windows import Manager
from windows.queue import QueueWindow
from windows.subtitles import SubtitlesWindow


class Session:
    """
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            log.set_level(sierra.logging)
            self.name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            self.windows = Manager()
            self.windows.subtitles = SubtitlesWindow()
            self.windows.queue = QueueWindow()

            self.characters = {
                character_name: Play.characters().get(character_name) for character_name in sierra.characters
            }
            self.tasks = {
                task_name: Play.tasks().get(task_name) for task_name in sierra.tasks
            }

            # TODO: Rethink assigning tasks to characters
            for character in self.characters.values():
                character.assign_task(list(self.tasks.values())[0])

            self.history = History(self, sierra.history)

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
                *[f'\t\t{entry.role}: {entry.content}' for entry in self.history.get()]
            ]
        )

    async def gather(self):
        """
         :return: Coroutine[Any, Any, None]
        """
        input_task = asyncio.create_task(self.process_input())
        output_task = asyncio.create_task(self.process_output())

        await asyncio.gather(input_task, output_task)

    async def process_input(self):
        """
         :return: Coroutine[Any, Any, None]
        """
        while True:
            if not self.input_queue.empty():
                _input = self.input_queue.get()
                self.windows.queue.add_panel(_input)
                input_thread = Thread(target=input_target, args=(self, _input))
                input_thread.start()
            else:
                await asyncio.sleep(0.1)

    async def process_output(self):
        """
        :return: Coroutine[Any, Any, None]
        """
        while True:
            if not self.output_queue.empty():
                output = self.output_queue.get()
                await output.character.respond(output)
                self.windows.queue.remove_panel(output.id)
            else:
                await asyncio.sleep(0.1)

    def get_chat_response(self, _input):
        """
        `get_chat_response` method to get the chat response.
        :param _input: Input
        :return: None
        """
        self.pre_process()

        prompt = _input.message
        character = self.characters[_input.character]
        try:
            chat, speech, subtitles = character.converse(prompt, self)

            self.output_queue.put(Output(_input.id, character, chat, speech, subtitles))

            self.response_word_count += len(chat.response.split())

            if sierra.history.summary.user:
                self.history.add(Moment(None, prompt))
            if sierra.history.summary.assistant:
                self.history.add(Moment(_input.character, chat.response))

            self.post_process()
        # TODO: Implement specific exceptions
        except Exception as e:
            self.windows.queue.remove_panel(_input.id)

    def pre_process(self):
        """
        `pre_process` method to pre-process the session.
        """
        for character in self.characters.values():
            character.rules[RuleType.TEMPORARY] = [
                rule for rule in character.rules[RuleType.TEMPORARY] if rule.expiration_time > datetime.now()
            ]

    def post_process(self):
        """
        `post_process` method to post-process the session.
        """
        if self.history.is_stale():
            self.history.summarize(list(self.tasks.values())[0])

        self.save()

    def save(self):
        """
        `save` method to save the session.
        """
        pickle.dump(self, open(f'saves/{self.name}.sierra', 'wb'))

    def load(self, file_name):
        """
        `load` method to load the session.
        :param file_name:
        """
        obj = pickle.load(open(file_name, 'rb'))
        self.characters = obj.characters
        for character in self.characters.values():
            log.info(
                f'''Loaded rules for ({character.name}):\n\t{f"{nl}{tab}".join(
                    [repr(rule) for rule_type, rules in character.rules.items() for rule in rules])}'''
            )
        self.history = obj.history
        log.info(
            f'''Loaded history:\n\tmax:{self.history.max_active_size}\n\t{f"{nl}{tab}".join(
                [repr(entry) for entry in self.history.moments])}'''
        )


def input_target(session: Session, ai_input):
    """
    `input_target` function to target the input.
    :param session:
    :param ai_input:
    :return:
    """
    session.get_chat_response(ai_input)
    return sys.exit()
