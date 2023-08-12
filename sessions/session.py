from decouple import config

from ai import open_ai
from ai.open_ai import Whisper, ChatGPT, MessageRole
from play import characters, tasks
from sessions.history import History
from sessions.recorder import Recorder, RECORD_BINDING
from utils.logging import log


class Session:
    def __init__(self, character_name, task_name):
        self.recorder = Recorder()

        self.character = characters.get(character_name)
        self.task = tasks.get(task_name)

        self.history = []

        self.response_word_count = 0

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def begin(self):
        while True:
            log.info(f'Input: Press {str(RECORD_BINDING)} to record.')
            self.recorder.record('temp/input.wav')

            prompt = Whisper.transcribe('temp/input.wav')

            log.info(f'Whisper: Transcribed: {prompt}')

            messages = [
                {"role": MessageRole.SYSTEM.value, "content": f'{self.character.motivation} '
                                                              f'{self.task.description} '
                                                              f'{self.character.format}'},
                *[{"role": entry.role, "content": entry.content} for entry in self.history],
                {"role": MessageRole.USER.value, "content": prompt}
            ]
            response, usage = self.character.chat(messages)

            open_ai.TOKENS += usage.get("total_tokens")

            if config('DEBUG_USAGE'):
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

            self.response_word_count += len(response.split())

            if self.task.summary.user:
                self.history.append(History(MessageRole.USER.value, prompt))
            if self.task.summary.assistant:
                self.history.append(History(MessageRole.ASSISTANT.value, response))

            self.assess()

    def assess(self):
        history_word_count = sum([len(entry.content.split()) for entry in self.history])

        if config('DEBUG_USAGE'):
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
        messages = [
            {"role": MessageRole.SYSTEM.value, "content": f'{self.character.task.description}'},
            {"role": "system", "content": self.character.task.summary},
            *[{"role": entry.role, "content": entry.content} for entry in self.history]
        ]

        summary, usage = ChatGPT.chat(messages)

        self.history = [History(MessageRole.ASSISTANT.value, summary)]

        log.info(f'OpenAI: Summary: {summary}')
