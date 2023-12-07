import requests

from decouple import config

from utils.logging import log


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

        log.info(response.text)
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
            "text": text,
            "voice_engine": "PlayHT2.0-turbo"
        }
        headers = {
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID"),
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


if __name__ == '__main__':
    PlayHt.fetch_voices()