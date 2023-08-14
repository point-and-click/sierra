class History:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def __repr__(self):
        return f'{self.role}: {self.content}'
