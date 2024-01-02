from os import path

import requests

from settings.secrets import Secrets
from utils.logging import log


def fetch_voices():
    secrets = Secrets(path.join('ai', 'play_ht', 'secrets.yaml'))
    url = "https://play.ht/api/v2/cloned-voices"

    headers = {
        "accept": "application/json",
        "AUTHORIZATION": f'Bearer {secrets.get("api_key")}',
        "X-USER-ID": secrets.get("user_id")
    }

    response = requests.get(url, headers=headers)

    log.info(response.text)
    return response.text


if __name__ == "__main__":
    fetch_voices()
