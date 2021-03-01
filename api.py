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


#########################################
#########################################
# Leaderboard
#########################################
#########################################


# Save the result to leaderboard table
def add_result_to_db(data):
    db = get_db()
    # If it is a draw
    if data['draw']:
        # Handle draw
        user1 = data['user1']
        user2 = data['user2']
    
    else:
        winner = data['winner']
        looser = data['looser']

        # Get winner's id
        winner_data = db.execute(
            'SELECT * FROM user WHERE username = ?', (winner,)
        ).fetchone()
        # Get winner's data in DB
        winners_leaderb_data = db.execute(
            'SELECT * FROM leaderboard WHERE user_id = ?', (winner_data['id'],)
        ).fetchone()

        # Winner already has some data on the leaderboard
        if winners_leaderb_data is not None:
            wins = winners_leaderb_data['wins']
            db.execute(
                'UPDATE leaderboard SET wins = ? WHERE user_id = ?', (wins + 1, winner_data['id'])
            )
        # Create a row for the user in the leaderboard
        else:
            db.execute(
                'INSERT INTO leaderboard (user_id, wins, draws, loses) VALUES (?, ?, ?, ?)',
                [winner_data['id'], 1, 0, 0]
            )

        # Repeat for looser
        looser_data = db.execute(
            'SELECT * FROM user WHERE username = ?', (looser,)
        ).fetchone()
        loosers_leaderb_data = db.execute(
            'SELECT * FROM leaderboard WHERE user_id = ?', (looser_data['id'],)
        ).fetchone()

        if loosers_leaderb_data is not None:
            loses = loosers_leaderb_data['loses']
            db.execute(
                'UPDATE leaderboard SET loses = ? WHERE user_id = ?', (loses + 1, looser_data['id'])
            )
        else:
            db.execute(
                'INSERT INTO leaderboard (user_id, wins, draws, loses) VALUES (?, ?, ?, ?)',
                [looser_data['id'], 0, 0, 1]
            )
        
        db.commit()


# Get the stats of players with top 10 wins
@bp.route('/leaderboard_data', methods=['GET'])
def get_lb_data():
    db = get_db()

    data = db.execute(
        'SELECT * from leaderboard ORDER BY wins DESC LIMIT 10'
    ).fetchall()

    # Convert Row Objects to Json Objects
    json_data = []
    for row in data:
        username = db.execute(
            'SELECT username FROM user WHERE id = ?', (str(row['user_id'],))
        ).fetchone()

        if username is None:
            username = 'Anonymous'
        
        json_data.append({
            'username': username['username'],
            'wins': row['wins'],
            'draws': row['draws'],
            'loses': row['loses']
        })
    
    return jsonify(data=json_data, success="Data successfully sent")
