from .account import account
from flask import Flask
from config import config

def create_app(config_name=config['default']):
    app = Flask(__name__)

    app.config.from_object(config_name)
    # blueprints here
    app.register_blueprint(account)

    return app
