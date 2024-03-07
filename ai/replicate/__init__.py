from os import path

from replicate import Client

from settings.secrets import Secrets
from settings.settings import Settings

secrets = Secrets(path.join(path.split(path.relpath(__file__))[0], 'secrets.yaml'))
settings = Settings(path.join(path.split(path.relpath(__file__))[0], 'settings.yaml'))


class Chat:
    client = Client(
        api_token=secrets.get("api_token"),
    )

    @staticmethod
    def send(prompt, session, character=None):
        completion = Chat.client.run(
            "meta/llama-2-7b-chat:f1d50bb24186c52daae319ca8366e53debdaa9e0ae7ff976e918df752732ccc4",
            input={
                "top_p": 1,
                "prompt": "Plan a day of sightseeing for me in San Francisco.",
                "temperature": 0.75,
                "system_prompt": "You are an old-timey gold prospector who came to San Francisco for the gold rush and then was teleported to the present day. Despite being from 1849, you have great knowledge of present-day San Francisco and its attractions. You are helpful, polite, and prone to rambling. ",
                "max_new_tokens": 100,
                "repetition_penalty": 1
            }
        )

        return completion
