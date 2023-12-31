from os import path

import requests

from settings.secrets import Secrets
from settings.settings import Settings
from utils.logging import log


class Speak:
    @staticmethod
    def fetch_voices():
        url = "https://play.ht/api/v2/cloned-voices"

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": f'Bearer {secrets.get("api_key")}',
            "X-USER-ID": secrets.get("user_id")
        }

        response = requests.get(url, headers=headers)

        log.info(response.text)
        return response.text

    @staticmethod
    def send(text, voice):
        url = "https://play.ht/api/v2/tts/stream"

        payload = {
            "quality": settings.get('quality'),
            "output_format": "mp3",
            "speed": 1,
            "sample_rate": settings.get('sample_rate'),
            "voice": voice,
            "text": text,
            "voice_engine": "PlayHT2.0-turbo",
            "voice_guidance": 5,
            "temperature": 0.5
        }
        headers = {
            "AUTHORIZATION": f'Bearer {secrets.get("api_key")}',
            "X-USER-ID": secrets.get("user_id"),
            "accept": "audio/mpeg",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        # audio_stream_url = json.loads(str(response.text))['href']

        # session = requests.Session()
        #
        # headers = {
        #     "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
        #     "X-USER-ID": config("PLAY_HT_USER_ID")
        # }
        #
        # response = session.get(audio_stream_url, headers=headers, stream=True)

        while response.status_code == 504:
            log.info("Play.HT Gateway timeout. Retrying...")
            response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.content
        else:
            raise CustomException("Womp womp.", None)


class CustomException(Exception):
    pass

    def __init__(self, message, errors):
        super().__init__(message)

        self.errors = errors


secrets = Secrets(path.join(*__name__.split('.'), 'secrets.yaml'))
settings = Settings(path.join(*__name__.split('.'), 'settings.yaml'))
