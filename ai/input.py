class Input:

    def __init__(self, json):
        self.character = json.get("character", None)
        self.message = json.get("message", None)
