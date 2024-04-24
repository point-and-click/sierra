from datetime import datetime, timedelta
from enum import Enum


class RuleType(Enum):
    PERMANENT = 'permanent'
    TEMPORARY = 'temporary'


class Rule:
    def __init__(self, rule):
        if isinstance(rule, dict):
            self.text = rule.get('rule')
        if isinstance(rule, str):
            self.text = rule

    def __repr__(self):
        return self.text


class TemporaryRule(Rule):
    def __init__(self, json):
        super().__init__(json)
        self.expiration_time = datetime.now() + timedelta(minutes=json.get('duration', 30))
