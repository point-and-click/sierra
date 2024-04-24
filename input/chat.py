import requests
from flask import request, Blueprint

from ai.input import Input
from play.sessions import Session

chats = Blueprint('chat', __name__)


@chats.route("/chat", methods=["POST"])
def receive():
    """
    `receive` function to receive a chat.
    :return: str, int
    """
    session = Session()
    session.input_queue.put(Input(request.json))
    return "Good job!", 200


def submit(message, character, source):
    """
    `submit` function to submit a chat.
    :param message: str
    :param character: str
    :param source: str
    """
    requests.post("http://localhost:8008/chat",
                  json={"message": message,
                        "character": character,
                        "source": source})
