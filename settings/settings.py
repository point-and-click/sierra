from yaml import safe_load


class Settings:
    def __init__(self, file_name):
        with open(file_name) as file:
            yaml = safe_load(file)

        self._items = {item.get('key'): item.get('value') for item in yaml.get('items')}

    def get(self, name, default=None):
        return self._items.get(name) if self._items.get(name) else default
