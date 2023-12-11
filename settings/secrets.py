from yaml import safe_load


class Secrets:
    def __init__(self, file_name):
        with open(file_name, 'r') as file:
            yaml = safe_load(file)

        self._items = {item.get('name'): item.get('key') for item in yaml.get('items')}

    def get(self, name):
        return self._items.get(name)
