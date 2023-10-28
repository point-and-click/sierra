import json

import audioread
import pyaudio
import requests
import pygame

from decouple import config

from utils.logging import log
from utils.word_wrap import WordWrap


class PlayHt:
    @staticmethod
    def fetch_voices():
        url = "https://play.ht/api/v2/cloned-voices"

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID")
        }

        response = requests.get(url, headers=headers)

        print(response.text)
        return response.text

    @staticmethod
    def fetch_audio_file(text, voice):
        url = "https://play.ht/api/v2/tts/stream"

        payload = {
            "quality": config('PLAY_HT_QUALITY'),
            "output_format": "mp3",
            "speed": 1,
            "sample_rate": config('SAMPLE_RATE', cast=int),
            "voice": voice,
            "text": text
        }
        headers = {
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID"),
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        audio_stream_url = json.loads(str(response.text))['href']

        session = requests.Session()

        headers = {
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID")
        }

        response = session.get(audio_stream_url, headers=headers, stream=True)

        while response.status_code == 504:
            log.info("Play.HT Gateway timeout. Retrying...")
            response = session.get(audio_stream_url, headers=headers, stream=True)

        if response.status_code == 200:
            return response.content
        else:
            raise Exception("Womp womp.")
