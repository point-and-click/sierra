import logging
from math import ceil
import random
from glob import glob
from os import path
from subprocess import run

from pydub import AudioSegment

from play.subtitles import transcript_from_text

words_per_segment = 10
time_per_word = 0.3

affected_characters = {
    'Eight Ball': 'shake',
    'Wah': 'wah'
}


class Initialize:
    @staticmethod
    def hook(session, character):
        sox = run(['command', '-v', 'sox'], capture_output=True, text=True)
        if sox.returncode != 0 or sox.stderr or not sox.stdout:
            logging.warning('Plugin: Requirement `sox` is not installed.')


class PreSpeech:
    @staticmethod
    def hook(session, character, chat, speech):
        if character.name in affected_characters.keys():
            character.skip_speech = True


class PostSpeech:
    @staticmethod
    def hook(session, character, chat, speech):
        if character.name in affected_characters.keys():
            voice_bank = glob(path.join('plugins', 'mumbo_jumbo', 'assets', affected_characters.get(character.name), '*'))
            total_time = len(chat.response.split()) * time_per_word

            speech_time = 0
            mumbo_jumbo = []
            while speech_time < total_time:
                voice_chunk = random.choice(voice_bank)
                speech_time += AudioSegment.from_file(voice_chunk).duration_seconds
                mumbo_jumbo.append(voice_chunk)

            run(['sox', *mumbo_jumbo, 'plugins/mumbo_jumbo/output.mp3'])
            with open('plugins/mumbo_jumbo/output.mp3', 'rb') as output_file:
                speech.set(output_file.read(), 'mp3')

            character.skip_speech = False


class PreTranscribe:
    @staticmethod
    def hook(session, character, chat, speech, subtitles):
        if character.name in affected_characters.keys():
            character.skip_transcribe = True


class PostTranscribe:
    @staticmethod
    def hook(session, character, chat, speech, subtitles):
        if character.name in affected_characters.keys():
            subtitles.set(
                transcript_from_text(
                    chat.response,
                    AudioSegment.from_file(speech.path).duration_seconds,
                    int(ceil(len(chat.response.split()) / words_per_segment))
                )
            )
