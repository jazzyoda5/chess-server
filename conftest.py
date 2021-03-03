import pytest
from tempfile import mkstemp
import os
from app import create_app
from db import init_db, get_db
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


def test_app():
    assert 5

"""
class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, username='test', password='test'):
        data = json.loads({
            'username': username,
            'password': password
        })
        self._client.post(
            '/api/login',
            data=data,
            headers={'Content-Type': 'application/json'}
        )

    
    def logout(self):
        self._client.get('/api/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
"""