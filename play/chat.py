class Chat:
    def __init__(self, timestamp, response):
        self.response = response
        self.path = f'temp/{timestamp}.txt'
        with open(self.path, "w") as text_file:
            text_file.write(self.response)