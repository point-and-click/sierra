class Speech:
    def __init__(self, timestamp, audio_bytes, audio_format):
        self.bytes = audio_bytes
        self.path = f'temp/{timestamp}.{audio_format}'
        with open(self.path, "wb") as audio_file:
            audio_file.write(self.bytes)