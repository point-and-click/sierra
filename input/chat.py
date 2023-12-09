import requests
from flask import request

from ai.input import AiInput
from input import sierra
from sessions.session import Session


@sierra.route("/chat", methods=["POST"])
def receive():
    session = Session()
    session.input_queue.put(AiInput(request.json))
    return "Good job!", 200


def submit(message, character):
    requests.post("http://localhost:8008/chat",
                  json={"message": message,
                        "character": character})
