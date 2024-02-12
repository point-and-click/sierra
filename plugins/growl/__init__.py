class PostTranscribe:
    @staticmethod
    def hook(session, character, chat, speech, subtitles):
        if character.name == "Little Lextra":
            time = subtitles.segments[-1].end
            with open('plugins/growl/growl.mp3', 'rb') as growl_file:
                speech.set(growl_file.read(), 'mp3')

