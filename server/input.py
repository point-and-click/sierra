from uuid import uuid4


class Input:
    """
    `Input` class to represent an input.
    """
    def __init__(self, json):
        """
        :param json: dict
        """
        self.id = uuid4()
        self.character = json.get('character', None)
        self.message = json.get('message', None)
        self.source = json.get('source', None)
