from flask import Flask

from input.chat import chats
from input.rule import rules

sierra = Flask("input")
sierra.register_blueprint(chats)
sierra.register_blueprint(rules)
