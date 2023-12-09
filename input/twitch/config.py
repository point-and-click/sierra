from enum import Enum


class FunctionType(Enum):
    CHAT = "chat"
    RULE = "rule"


class Secrets:
    def __init__(self, secrets):
        self.app_id = secrets.get('app_id', None)
        self.app_secret = secrets.get('app_secret', None)

        if any([self.app_id is None, self.app_secret is None]):
            raise Exception("Twitch is not configured!")


class Emotes:
    def __init__(self, emotes):
        self.prefix = emotes.get('prefix', '')
        self.characters = emotes.get('characters', [])


class Events:
    def __init__(self, events):
        self.map = {}

        for event in events:
            if 'titles' in event:
                self.map[event.get('type')] = {title.get('title', ''): self._TitleEvent(title) for title in
                                               event.get('titles', [])}
            elif 'tiers' in event:
                self.map[event.get('type')] = {tier.get('tier', ''): self._TierEvent(tier) for tier in
                                               event.get('tiers', [])}

    class _TitleEvent:
        def __init__(self, event):
            self.title = event.get('title', '')
            self.type = FunctionType(event.get('function', 'chat'))
            self.message = event.get('message', '')

    class _TierEvent:
        def __init__(self, event):
            self.tier = event.get('tier', 0)
            self.type = FunctionType(event.get('function', 'chat'))
            self.message = event.get('message', '')
