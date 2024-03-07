class Chat:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.path = None
        self.response = None

    def __repr__(self):
        return self.path

    def set(self, response):
        self.path = f'temp/{self.timestamp}.txt'
        self.response = response

        self._save()

    def _save(self):
        with open(self.path, "w") as text_file:
            text_file.write(self.response)
