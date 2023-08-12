from play.summary import Summary


class Task:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.description = yaml.get('description', None)
        self.summary = Summary(yaml.get('summary', None))
