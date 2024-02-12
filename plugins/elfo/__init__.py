class PreChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name == "Elfo":
            character.skip_chat = True


class PostChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name == "Elfo":
            chat.set("Hi, I'm Elfo!")
            character.skip_chat = False
