import openai
from decouple import config
import elevenlabs
from characters import Character

openai.api_key = config('OPENAI_API_KEY')
elevenlabs.set_api_key(config('ELEVENLABS_API_KEY'))

if __name__ == '__main__':

    character = Character(config('CHARACTER'))

    character.chat("Should we venture into the closet to defeat Darkness?")
