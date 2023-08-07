class Palette:
    def __init__(self, colors):
        self.red = colors.get('red')
        self.pink = colors.get('pink')
        self.purple = colors.get('purple')
        self.indigo = colors.get('indigo')
        self.blue = colors.get('blue')
        self.cyan = colors.get('cyan')
        self.green = colors.get('green')
        self.yellow = colors.get('yellow')
        self.orange = colors.get('orange')
        self.brown = colors.get('brown')
        self.gray = colors.get('gray')


_material_colors = {
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

material = Palette(_material_colors)
