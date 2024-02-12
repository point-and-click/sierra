class Speech:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.path = f'temp/{timestamp}.wav'
        self.bytes = None

    def set(self, audio_bytes, audio_file_type):
        self.bytes = audio_bytes
        self.path = f'temp/{self.timestamp}.{audio_file_type}'

        self._save()

    def _save(self):
        with open(self.path, "wb") as audio_file:
            audio_file.write(self.bytes)
