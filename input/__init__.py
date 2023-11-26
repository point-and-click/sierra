from flask import Flask, request
from ai.input import AiInput

from sessions.session import Session

app = Flask("input")


@app.route("/", methods=["POST"])
def ai_input():
    session = Session()
    session.input_queue.put(AiInput(request.json))
    return "Good job!", 200
