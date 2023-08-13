class Palette:
    def __init__(self, colors):
        self.red = colors.get('red', None)
        self.pink = colors.get('pink', None)
        self.purple = colors.get('purple', None)
        self.indigo = colors.get('indigo', None)
        self.blue = colors.get('blue', None)
        self.cyan = colors.get('cyan', None)
        self.green = colors.get('green', None)
        self.yellow = colors.get('yellow', None)
        self.orange = colors.get('orange', None)
        self.brown = colors.get('brown', None)
        self.gray = colors.get('gray', None)


material = Palette(
    {
        'red': 'F44336',
        'pink': 'E91E63',
        'purple': '9C27B0',
        'indigo': '3F51B5',
        'blue': '2196F3',
        'cyan': '00BCD4',
        'green': '4CAF50',
        'yellow': 'FFEB3B',
        'orange': 'FF9800',
        'brown': '795548',
        'gray': '9E9E9E'
    }
)
