import json

import requests
from flask import request

from input import sierra
from sessions.session import Session


@sierra.route("/rule", methods=["POST"])
def rule_receive():
    session = Session()
    session.characters.get(request.json.get('character')).add_rule(request.json)
    return "Good job!", 200


@sierra.route("/rule", methods=["GET"])
def rule_list():
    session = Session()
    return json.dumps(session.user_rules.rules), 200


def submit(rule, character):
    requests.post("http://localhost:8008/rule",
                  json={"rule": rule, "character": character})
