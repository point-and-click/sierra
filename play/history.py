import ai
from utils.logging import log


class History:
    def __init__(self, session, settings):
        self._session = session
        self.max_active_size = settings.max_active_size
        self.summary_max_active_size = settings.summary.max_active_size
        self.moments = []
        self.summary = None
        self._ai = settings.summary.ai

    def get(self, size=None):
        return self.moments[-(size if size else self.max_active_size):]

    def add(self, moment):
        self.moments.append(moment)

    def is_stale(self):
        return len(self.moments) // self.summary_max_active_size == self.summary_max_active_size - 1

    def summarize(self, task):
        messages = [
            *[{"role": ai.Role.ASSISTANT.value if entry.character else ai.Role.USER.value, "content": entry.response}
              for entry in
              self.get(self.summary_max_active_size)],
            {"role": ai.Role.SYSTEM, "content": task.summary.description}
        ]

        summary = ai.load(self._ai, ai.Function.CHAT)().send(messages, self._session)
        self.summary = Moment(None, summary)
        log.info(f'History: Summary: {self.summary}')


class Moment:
    def __init__(self, character, response):
        self.character = character
        self.response = response

    def __repr__(self):
        return f'{self.character if self.character else "You"}: {self.response}'

    def serialize(self, compare=None):
        return {'role': ai.Role.ASSISTANT.value if compare == self.character else ai.Role.USER.value,
                'content': self.response}
