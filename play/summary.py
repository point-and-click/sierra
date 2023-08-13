class Summary:
    def __init__(self, yaml):
        self.assistant = yaml.get('assistant', None)
        self.user = yaml.get('user', None)
        self.description = yaml.get('description', None)
