import pyaudio


class Bind:
    def __init__(self, json):
        self.vk = json.get('vk', 0)
        self.character = json.get('character', None)


class Audio:
    def __init__(self, json):
        self.device = json.get('device', None)
        self.rate = json.get('rate', 44100)
        self.chunks = json.get('chunks', 1024)
        self.channels = json.get('channels', 2)
        self.fs = json.get('fs', 44100)
        self.sample_format = json.get('sample_format', pyaudio.paInt16)
        self.chunk = json.get('chunk', 1024)
