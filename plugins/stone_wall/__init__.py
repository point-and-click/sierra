from random import choice

affected_characters = {
    'Eight Ball': [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",

        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",

        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ]
}


class PreChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name in affected_characters.keys():
            character.skip_chat = True


class PostChat:
    @staticmethod
    def hook(session, character, chat):
        if character.name in affected_characters.keys():
            chat.set(choice(affected_characters.get(character.name)))
            character.skip_chat = False
