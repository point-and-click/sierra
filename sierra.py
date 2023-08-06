import openai
from decouple import config
import elevenlabs
from sessions.session import Session

openai.api_key = config('OPENAI_API_KEY')
elevenlabs.set_api_key(config('ELEVENLABS_API_KEY'))

if __name__ == '__main__':
    with Session(config('CHARACTER')) as session:
        session.begin()
