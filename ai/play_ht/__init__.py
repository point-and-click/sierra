from os import path

import requests
from pyht import Client, TTSOptions, Format

from settings.secrets import Secrets
from settings.settings import Settings
from utils.logging import log


class Speak:
    """
    Sierra Speak class
    """
    @staticmethod
    def fetch_voices():
        """
        :return: str
        """
        url = "https://play.ht/api/v2/cloned-voices"

        headers = {
            "accept": "application/json",
            "AUTHORIZATION": f'Bearer {secrets.get("api_key")}',
            "X-USER-ID": secrets.get("user_id")
        }

        response = requests.get(url, headers=headers)

        log.debug(response.text)
        return response.text

    @staticmethod
    def send(text: str, voice: dict) -> tuple[bytes, str]:
        """
        :param text: str
        :param voice: dict
        :return: bytes, str
        """
        client = Client(secrets.get("user_id"), secrets.get("api_key"))
        options = TTSOptions(
            voice=voice.get('voice_id', settings.get('voice_id')),
            sample_rate=settings.get('sample_rate', 44100),
            format=Format.FORMAT_MP3,
            quality=voice.get('quality', settings.get('quality', 'faster')),
            speed=voice.get('speed', settings.get('speed', 1)),
            temperature=voice.get('temperature', settings.get('temperature')),
            top_p=voice.get('top_p', settings.get('top_p')),
            text_guidance=voice.get('text_guidance', settings.get('text_guidance')),
            voice_guidance=voice.get('voice_guidance', settings.get('voice_guidance')),
        )

        return b''.join(
            client.tts(
                text=text,
                voice_engine=voice.get('voice_engine', settings.get('voice_engine')),
                options=options
            )
        ), 'mp3'


secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))
