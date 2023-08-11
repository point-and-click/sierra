from characters import tasks


class Task:
    def __init__(self, name):
        self.name = name

        # These values are populated by the task yaml definitions.
        self.description = None
        self.summary = None
        self.user_history = None
        self.assistant_history = None
        for k, v in tasks.get(name, self).items():
            setattr(self, k, v)
