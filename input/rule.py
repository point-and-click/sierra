import json

import requests
from flask import request, Blueprint

from sessions import Session

rules = Blueprint('rule', __name__)


@rules.route("/rule", methods=["POST"])
def rule_receive():
    session = Session()
    session.characters.get(request.json.get('character')).add_rule(request.json)
    return "Good job!", 200


@rules.route("/rule", methods=["GET"])
def rule_list():
    session = Session()
    return json.dumps(session.user_rules.rules), 200


def submit(rule, character):
    requests.post("http://localhost:8008/rule",
                  json={"rule": rule, "character": character})
