import requests
from flask import request

from ai.input import Input
from input import sierra
from sessions import Session


@sierra.route("/chat", methods=["POST"])
def receive():
    session = Session()
    session.input_queue.put(Input(request.json))
    return "Good job!", 200


def submit(message, character):
    requests.post("http://localhost:8008/chat",
                  json={"message": message,
                        "character": character})
