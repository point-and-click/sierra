from datetime import datetime, timedelta
from enum import Enum

from utils.logging import log


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
        log.info(f"Setting new rule: {json.get('rule')} for {json.get('duration')} minutes.")
        super().__init__(json)
        self.expiration_time = datetime.now() + timedelta(minutes=int(json.get('duration')))
