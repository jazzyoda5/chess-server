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

    db = get_db()

    if not username or not password:
        response = jsonify(error='Form is not complete')
        return response
    
    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        response = jsonify(error='User already exists')
        return response

    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)', 
        (username, generate_password_hash(password))
    )  
    db.commit()
    response = jsonify(success='Account successfully created.')
    return response


@bp.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['usernameInput']
    password = data['passwordInput']

    db = get_db()

    # Not complete

    response = jsonify(success='Successfully logged in')
    return response
