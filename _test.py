import sqlite3
import pytest
import json
from flask import session, g
from db import get_db
from app import create_app

# Test create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


# Test Database

def test_get_db(app):
    # Makes sure get_db always gets the same db
    with app.app_context():
        db = get_db()
        assert db is get_db()
    
    # Check if connection is closed outside app context
    with pytest.raises(sqlite3.ProgrammingError) as error:
        db.execute('SELECT 1')

    assert 'closed' in str(error.value)


# Test accounts

def test_login(client):
    response = client.post(
        '/api/login',
        data=json.dumps({'usernameInput': 'test', 'passwordInput': 'test'}),
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    assert response.json['success']


def test_register(client, app):
    # Check how it handles if user with this username already exists
    response_user_exists = client.post(
        '/api/register',
        data=json.dumps({'usernameInput': 'test', 'passwordInput': 'test'}),
        headers={'Content-Type': 'application/json'}
    )
    assert response_user_exists.status_code == 200
    assert response_user_exists.json['error']
    assert response_user_exists.json['error'] == 'User with this username already exists'

    # If it successfully saves new user in db
    response_new_user = client.post(
        '/api/register',
        data=json.dumps({'usernameInput': 'test2', 'passwordInput': 'test2'}),
        headers={'Content-Type': 'application/json'}
    )
    assert response_new_user.status_code == 200
    assert response_new_user.json['success']

    with app.app_context():
        db = get_db()
        test_user = db.execute(
            'SELECT * FROM user WHERE username = "test2"'
        ).fetchone()
        assert test_user is not None


# Test Leaderboard

def test_get_lb_data(client, app):
    response = client.get('/api/leaderboard_data', headers={'Content-Type': 'application/json'})

    assert response.status_code == 200
    assert len(response.json['data']) == 10
    assert response.json['success']
    assert response.json['data'].username == b'Anonymous'
