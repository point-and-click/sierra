import asyncio
from datetime import datetime


class AsyncInput:
    def __init__(self, input_queue):
        self.input_queue = input_queue

    async def put_in_queue(self):
        while True:
            self.input_queue.put(f'Baba {datetime.now()}')
            await asyncio.sleep(20)
