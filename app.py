import os
from flask import Flask
import api


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    app.register_blueprint(api.bp)

    return app