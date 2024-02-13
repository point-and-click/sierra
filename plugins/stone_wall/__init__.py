affected_characters = {'Elfo': "Hi, I'm Elfo!"}


class PreChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name in affected_characters.keys():
            character.skip_chat = True


class PostChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name in affected_characters.keys():
            chat.set(affected_characters.get(character.name))
            character.skip_chat = False
