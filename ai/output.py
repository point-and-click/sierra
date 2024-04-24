class Output:
    """
    Output class to store the output of the AI
    """
    def __init__(self, _id, character, chat, speech, subtitles):
        """
        :param _id: str
        :param character: Character
        :param chat: Chat
        :param speech: Speech
        :param subtitles: Subtitles
        """
        self.id = _id
        self.character = character
        self.chat = chat
        self.speech = speech
        self.subtitles = subtitles
