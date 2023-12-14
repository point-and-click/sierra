import json

import requests
from flask import request, Blueprint

from play.rules import RuleType
from sessions import Session

rules = Blueprint('rule', __name__)


@rules.route("/rule", methods=["POST"])
def rule_receive():
    session = Session()
    session.characters.get(request.json.get('character')).add_rule(RuleType.TEMPORARY, request.json)
    return "Good job!", 200


def submit(rule, character):
    requests.post("http://localhost:8008/rule",
                  json={"rule": rule, "character": character})
