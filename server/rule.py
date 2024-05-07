from json import dumps

import requests
from flask import request, Blueprint

from play.rules import RuleType, TemporaryRule
from play.sessions import Session

rules = Blueprint('rule', __name__)


@rules.route("/rules", methods=["GET"])
def display_rules():
    """
     :return: str, int
     """
    session = Session()
    return '\n'.join(
            [f'{name}: {character.serialize_rules(RuleType.TEMPORARY)}' for name, character in session.characters.items()]), 200


@rules.route("/rule", methods=["POST"])
def rule_receive():
    """
    :return: str, int
    """
    session = Session()
    session.characters.get(request.json.get('character')).add_rule(RuleType.TEMPORARY, TemporaryRule(request.json))
    return "Good job!", 200


def submit(rule, character):
    """
    :param rule: str
    :param character: str
    """
    requests.post("http://localhost:8008/rule",
                  json={"rule": rule, "character": character})
