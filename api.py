import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import jsonify
from flask import request
from flask import session
from flask import url_for
from db import get_db
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_cors import cross_origin
import json

bp = Blueprint('api', __name__, url_prefix='/api')

#########################################
#########################################
# Authentication
#########################################
#########################################


@bp.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    username = data['usernameInput']
    password = data['passwordInput']
    # Get the database
    db = get_db()

    if not username or not password:
        response = jsonify(error='Please fill out the form')
        return response
    
    # Check if this user already exists
    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        response = jsonify(error='User with this username already exists')
        return response

    # Create user
    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)', 
        (username, generate_password_hash(password))
    )  
    db.commit()

    # Log in the user
    user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    session.clear()
    session['user_id'] = user['id']
    response = jsonify(success='Account successfully created.')
    return response


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = json.loads(request.data)
        username = data['usernameInput']
        password = data['passwordInput']

        # Get the database
        db = get_db()
        # Set an error variable
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        
        # Unhash the password
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            # Restore the session and add user's id
            session.clear()
            session['user_id'] = user['id']
            response = jsonify(success='Successfully logged in')
            return response
        else:
            response = jsonify(error=error)
            return response

    # This is used to check if user is logged in
    elif request.method == 'GET':
        # Check if user is already logged in
        if 'user' in session:
            response = jsonify(success='User is already logged in')
            return response
        else:
            response = jsonify(error='User is not logged in')
            return response

    response = jsonify(error='Something went wrong')
    return response

@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    response = jsonify(success='User is logged out')
    return response

