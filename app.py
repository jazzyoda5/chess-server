import os
from flask import Flask
import api
import db
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'chessdb.sqlite'),
    )

    app.register_blueprint(api.bp)
    db.init_app(app)
    
    CORS(app)

    return app