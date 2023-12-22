class Character:
    def __init__(self, json):
        self.rank = json.get('rank', 0)
        self.name = json.get('character', None)
