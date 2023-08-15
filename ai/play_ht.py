import json

import audioread
import numpy as np
import pyaudio
import requests
import tempfile

from decouple import config

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

        return requests.get(url, headers=headers)

    @staticmethod
    def speak(text):
        audio_stream_url = PlayHt.fetch_audio_stream_url(text)

        session = requests.Session()

        headers = {
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID")
        }

        # Make a GET request to the audio URL
        response = session.get(audio_stream_url, headers=headers, stream=True)

        # Check if the request was successful
        if response.status_code == 200:

            p = pyaudio.PyAudio()
            # Create a temporary file to save the audio content
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file.seek(0)  # Move back to the beginning of the file

                with open('obs_text.txt', "w") as f:
                    f.write(WordWrap.word_wrap(text, 75))

                # Open a new stream for audio playback
                stream = p.open(format=pyaudio.paInt16,
                                channels=config('CHANNELS', cast=int),
                                rate=config('SAMPLE_RATE', cast=int),
                                output=True)

                # Create an audioread decoder
                with audioread.audio_open(temp_file.name) as f:
                    for buf in f:
                        pcm_data = np.frombuffer(buf, dtype=np.int16)
                        stream.write(pcm_data.tobytes())

                stream.stop_stream()
                stream.close()

            temp_file.close()

        session.close()

    @staticmethod
    def fetch_audio_stream_url(text):
        url = "https://play.ht/api/v2/tts/stream"

        payload = {
            "quality": config('PLAY_HT_QUALITY'),
            "output_format": "mp3",
            "speed": 1,
            "sample_rate": config('SAMPLE_RATE', cast=int),
            "voice": config('PLAY_HT_VOICE'),
            "text": text
        }
        headers = {
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID"),
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        return json.loads(str(response.text))['href']
