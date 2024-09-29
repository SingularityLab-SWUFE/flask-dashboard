from .account import account
from .submission import submission
from .pages import pages
from flask import Flask
from config import config

def create_app(config_name=config['default']):
    app = Flask(__name__)

    app.config.from_object(config_name)
    # blueprints here
    app.register_blueprint(account)
    app.register_blueprint(submission)
    app.register_blueprint(pages)

    return app
