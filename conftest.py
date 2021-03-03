import pytest
from tempfile import mkstemp
import os
from main import socketio
from app import create_app
from db import init_db, get_db
from flask_socketio import SocketIO
import json


# Create a temporary db file to use for tests
with open(os.path.join(os.path.dirname(__file__), 'test.sql'), 'rb') as f:
    _test_sql = f.read().decode('utf8')

###############
# Fixtures
###############

@pytest.fixture
def app():
    db_fd, db_path = mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_test_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def socketio(app):
    return SocketIO(app)

