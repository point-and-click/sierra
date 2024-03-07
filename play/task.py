class Task:
    """
    :param yaml: dict
    """
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.description = yaml.get('description', None)
        self.summary = self._Summary(yaml.get('summary', None))

    class _Summary:
        """
        :param yaml: dict
        """
        def __init__(self, yaml):
            self.assistant = yaml.get('assistant', None)
            self.user = yaml.get('user', None)
            self.description = yaml.get('description', None)
