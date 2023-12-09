from datetime import datetime, timedelta


class Rule:
    def __init__(self, json):
        self.text = json.get('rule')
        self.expiration_time = datetime.now() + timedelta(minutes=json.get('duration', 30))

    def __repr__(self):
        return self.text
