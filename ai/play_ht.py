import json

import audioread
import numpy
import numpy as np
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
    def speak(text, voice):
        if config('PLAY_HT_STREAM', cast=bool):
            PlayHt.stream_tts(text, voice)
        else:
            PlayHt.download_and_play_tts(text, voice)

    @staticmethod
    def download_and_play_tts(text, voice):
        audio_link = PlayHt.get_audio_link(text, voice)

        response = requests.get(audio_link)

        with open('obs_text.txt', "w") as f:
            f.write(WordWrap.word_wrap(text, 75))

        if response.status_code == 200:
            audio_data = response.content

            with open('temp/output.wav', 'wb') as temp_file:
                temp_file.write(audio_data)

            with audioread.audio_open(temp_file.name) as f:
                pcm_data = b"".join(chunk for chunk in f)

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=config('CHANNELS', cast=int),
                            rate=config('SAMPLE_RATE', cast=int),
                            output=True)

            stream.start_stream()
            stream.write(pcm_data)

            stream.stop_stream()
            stream.close()

            p.terminate()

            # Clean up the temporary file
            temp_file.close()
        else:
            print("Failed to retrieve audio data.")

    @staticmethod
    def get_audio_link(text, voice):
        url = "https://play.ht/api/v2/tts"
        headers = {
            "accept": "application/json",
            "AUTHORIZATION": f'Bearer {config("PLAY_HT_API_KEY")}',
            "X-USER-ID": config("PLAY_HT_USER_ID")
        }

        payload = {
            "quality": config('PLAY_HT_QUALITY'),
            "output_format": "mp3",
            "speed": 1,
            "sample_rate": config('SAMPLE_RATE', cast=int),
            "voice": voice,
            "text": text,
            "temperature": 1.25
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            job_id = response.json().get('id')
            url = f'https://play.ht/api/v2/tts/{job_id}'
            response = requests.get(url, headers=headers)
            while response.json().get('output') is None:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    log.info('Request for Play HT audio link failed.')
            return response.json().get('output')['url']
        else:
            log.info("Request to generate audio from Play HT failed.")

    @staticmethod
    def stream_tts(text, voice):

        pygame.init()
        screen = pygame.display.set_mode((275, 338))
        screen.fill((0, 255, 0))
        pygame.display.update()
        image = pygame.image.load('other_poop.png').convert_alpha()
        image_rect = image.get_rect()
        pygame.display.set_caption("Sierra")
        current_angle = 0
        max_angle = 35
        max_rotation = 3
        max_amplitude = 1000

        audio_stream_url = PlayHt.fetch_audio_stream_url(text, voice)

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
            p = pyaudio.PyAudio()

            with open('temp/output.wav', 'wb') as temp_file:
                temp_file.write(response.content)
                temp_file.seek(0)

                with open('obs_text.txt', "w") as f:
                    f.write(WordWrap.word_wrap(text, 75))

                # Open a new stream for audio playback
                stream = p.open(format=pyaudio.paInt16,
                                channels=config('CHANNELS', cast=int),
                                rate=config('SAMPLE_RATE', cast=int),
                                output=True)

                # Create an audioread decoder
                with audioread.audio_open(temp_file.name) as f:
                    prev_angle = 0
                    for buf in f:
                        audio_array = np.frombuffer(buf, dtype=np.int16)

                        amplitude = np.max(np.abs(audio_array))
                        if amplitude > max_amplitude:
                            max_amplitude = amplitude

                        scaled_amplitude = min(amplitude, max_amplitude) / max_amplitude
                        target_angle = scaled_amplitude * max_angle
                        target_rotation_amount = target_angle - prev_angle
                        actual_rotation_amount = max(-max_rotation, min(max_rotation, target_rotation_amount))
                        new_angle = max(-max_angle, min(max_angle, actual_rotation_amount + prev_angle))
                        rotated_image = pygame.transform.rotate(image, new_angle)
                        rotated_rect = rotated_image.get_rect(center=image_rect.center)
                        prev_angle = new_angle

                        pygame.event.get()
                        screen.fill((0, 255, 0))
                        screen.blit(rotated_image, rotated_rect)
                        pygame.display.update()

                        volume_adjusted_audio_bytes = PlayHt.audio_data_list_set_volume(audio_array, 1)

                        stream.write(volume_adjusted_audio_bytes.tobytes())

                print(max_amplitude)
                stream.stop_stream()
                stream.close()

            temp_file.close()

        pygame.quit()
        # session.close()

    @staticmethod
    def audio_data_list_set_volume(data_list, volume):
        adjusted_data_list = data_list.copy()

        for i in range(len(data_list)):
            chunk = numpy.fromstring(data_list[i], numpy.int16)

            chunk = chunk * volume

            adjusted_data_list[i] = chunk.astype(numpy.int16)

        return adjusted_data_list

    @staticmethod
    def fetch_audio_stream_url(text, voice):
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

        return json.loads(str(response.text))['href']
