from random import choice

affected_characters = {
    'Eight Ball': [
        # Affirmative
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        # Non-committal
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        # Negative
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ],
    'D20': [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        '11',
        '12',
        '13',
        '14',
        '15',
        '16',
        '17',
        '18',
        '19',
        '20'
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
