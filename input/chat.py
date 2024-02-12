import requests
from flask import request, Blueprint

from ai.input import Input
from sessions import Session

chats = Blueprint('chat', __name__)


@chats.route("/chat", methods=["POST"])
def receive():
    session = Session()
    session.input_queue.put(Input(request.json))
    return "Good job!", 200


def submit(message, character, source):
    requests.post("http://localhost:8008/chat",
                  json={"message": message,
                        "character": character,
                        "source": source})
