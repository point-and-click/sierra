from datetime import datetime, timedelta
from enum import Enum


class RuleType(Enum):
    PERMANENT = 'permanent'
    TEMPORARY = 'temporary'


class Rule:
    def __init__(self, json):
        self.text = json.get('rule')

    def __repr__(self):
        return self.text


class TemporaryRule(Rule):
    def __init__(self, json):
        super().__init__(json)
        self.expiration_time = datetime.now() + timedelta(seconds=json.get('duration'))
