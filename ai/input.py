from uuid import uuid4


class Input:

    def __init__(self, json):
        self.id = uuid4()
        self.character = json.get('character', None)
        self.message = json.get('message', None)
        self.source = json.get('source', None)
