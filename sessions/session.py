import logging

from decouple import config

from ai.open_ai import Whisper, ChatGPT, MessageRole
from characters.character import Character
from sessions.history import History
from sessions.recorder import Recorder, RECORD_BINDING
from utils import log_format, palette


class Session:
    def __init__(self, character_name, task_name):
        self.recorder = Recorder()

        self.character = Character(character_name)
        self.character.set_task(task_name)

        self.history = []

        self.response_word_count = 0

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def begin(self):
        while True:
            logging.info(
                f'{log_format.color(palette.material.orange)}'
                f'Input'
                f'{log_format.reset()}: '
                f'Press {str(RECORD_BINDING)} to record.'
            )
            self.recorder.record('temp/input.wav')
            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'Whisper'
                f'{log_format.reset()}: '
                f'Transcribing recorded audio.'
            )
            prompt = Whisper.transcribe('temp/input.wav')

            logging.info(
                f'{log_format.color(palette.material.cyan)}'
                f'Whisper'
                f'{log_format.reset()}: '
                f'{log_format.color(palette.material.orange)}'
                f'Transcribed'
                f'{log_format.reset()}: '
                f'{prompt}'
            )

            messages = [
                {"role": MessageRole.SYSTEM.value, "content": f'{self.character.motivation} '
                                                              f'{self.character.task.description} '
                                                              f'{self.character.format}'},
                *[{"role": entry.role, "content": entry.content} for entry in self.history],
                {"role": MessageRole.USER.value, "content": prompt}
            ]
            response = self.character.chat(messages)
            self.response_word_count += len(response.split())

            if self.character.task.user_history:
                self.history.append(History(MessageRole.USER.value, prompt))
            if self.character.task.assistant_history:
                self.history.append(History(MessageRole.ASSISTANT.value, response))

            self.assess()

    def assess(self):
        history_word_count = sum([len(entry.content.split()) for entry in self.history])

        logging.critical(
            f'History word count: {history_word_count} / {config("OPENAI_CHAT_COMPLETION_MAX_WORD_COUNT", cast=int)}')

        if history_word_count > config("OPENAI_CHAT_COMPLETION_MAX_WORD_COUNT", cast=int):
            self.summarize()

    def summarize(self):
        messages = [
            {"role": MessageRole.SYSTEM.value, "content": f'{self.character.task.description}'},
            {"role": "system", "content": self.character.task.summary},
            *[{"role": entry.role, "content": entry.content} for entry in self.history]
        ]

        summary = ChatGPT.chat(messages)

        self.history = [History(MessageRole.ASSISTANT.value, summary)]

        logging.info(
            f'{log_format.color(palette.material.cyan)}'
            f'OpenAI'
            f'{log_format.reset()}: '
            f'Summarized history: '
            f'{summary}'
        )
