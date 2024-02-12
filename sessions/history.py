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
            *[{"role": entry.role, "content": entry.content} for entry in self.get(self.summary_max_active_size)],
            {"role": ai.Role.SYSTEM, "content": task.summary.description}
        ]

        summary = ai.load(self._ai, ai.Function.CHAT)().send(messages, self._session)
        self.summary = Moment(ai.Role.ASSISTANT, summary)
        log.info(f'History: Summary: {self.summary}')


class Moment:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def __repr__(self):
        return f'{self.role}: {self.content}'

    def serialize(self):
        return {'role': self.role, 'content': self.content}
