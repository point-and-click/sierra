from flask import Flask

from server.chat import chats
from server.rule import rules

sierra = Flask("input")
sierra.register_blueprint(chats)
sierra.register_blueprint(rules)
