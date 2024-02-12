from utils.logging import log


class Initialize:
    @staticmethod
    def hook():
        log.info("Plugin: Initialize ran!")


class PreChat:
    @staticmethod
    def hook():
        log.info("Plugin: PreChat ran!")


class PostChat:
    @staticmethod
    def hook():
        log.info("Plugin: PostChat ran!")


class PreSpeech:
    @staticmethod
    def hook():
        log.info("Plugin: PreSpeech ran!")


class PostSpeech:
    @staticmethod
    def hook():
        log.info("Plugin: PostSpeech ran!")


class PreTranscribe:
    @staticmethod
    def hook():
        log.info("Plugin: PreTranscribe ran!")


class PostTranscribe:
    @staticmethod
    def hook():
        log.info("Plugin: PostTranscribe ran!")
