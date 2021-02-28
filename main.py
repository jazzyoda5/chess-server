from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from engine import get_move
from app import create_app
from flask_cors import CORS

# Initialize the app
app = create_app()
socketio = SocketIO(app, cors_allowed_origins='*')


##################################################
##################################################
# SOCKET
##################################################
##################################################


# Rooms are saved like this -> rooms = {{ Room: Num_Of_Users }}
rooms = {}
  

# When recieved a move from online mode
@socketio.on('move')
def handle_move(data):
    print('[RECIEVED] Move.')
    room = data['room_id']
    emit('move', data, room=room)


@socketio.on('message')
def handle_message(data):
    print('[MESSAGE RECIEVED] {}'.format(data))


# Join a multiplayer game
@socketio.on('join')
def handle_join():
    # If there are no active rooms
    if len(rooms) < 1:
        room = 'room1'
        rooms[room] = 1
        join_room(room)
        emit('room-data', {
            'room_id': room,
            'color': 'White'})

        print('[ROOM JOINED] Room ID: {}, Users: {}'.format(
            room, rooms[room]
        ))

    else:
        num_of_rooms = len(rooms)
        last_room = 'room' + str(num_of_rooms)
        print('[LAST ROOM] : ', last_room)

        # If it is NOT full join the room
        # Else create a new one and wait for next user

        if rooms[last_room] == 1:
            room = last_room
            rooms[room] = 2
            join_room(room)
            emit('room-data', {
                'room_id': room,
                'color': 'Black'
            })
            # Tell players the game can start because
            # Two users are in the room
            emit('full-room', room=room)
            print('[ROOM JOINED] Room ID: {}, Users: {}'.format(
                room, rooms[room]
            ))

        # If room is full
        elif rooms[last_room] == 2:
            # Create new room
            room = 'room' + str(num_of_rooms + 1)
            rooms[room] = 1
            join_room(room)
            emit('room-data', {
                'room_id': room,
                'color': 'White'
            })
            print('[ROOM JOINED] Room ID: {}, Users: {}'.format(
                room, rooms[room]
            ))


# Multiplayer checkmate
@socketio.on('checkmate')
def handle_checkmate(data):
    emit('checkmate', data, room=data['room_id'])


# Leave a multiplayer room
@socketio.on('leave')
def handle_leave(data):
    room = data['room_id']
    leave_room(room)

    # Check if room has to be deleted
    num_of_users_in_room = rooms[room] - 1
    rooms[room] = num_of_users_in_room

    print('[LEAVE] Room ID: {}, Users: {}'.format(room, num_of_users_in_room))


    # If room is empty delete it
    if num_of_users_in_room < 1:
        del rooms[room]
        print('[ROOM DELETED] Room ID: {}'.format(room))
    
    else:
        emit('opponent', 'left', room=room)


# Singleplayer move
@socketio.on('computer-move')
def handle_comp_move(data):
    print('[RECIEVED] Request for a move calculation.')
    move = get_move(data)
    emit('computer-move', move)
    print('[COMPUTER MOVE] Emitted.')


@socketio.on('connect')
def handle_connect():
    print('[NEW CONNECTION] New user connected.')


@socketio.on('disconnect')
def handle_disconnect():
    print('[DISCONNECTED] User has disconnected.')


if __name__ == '__main__':
    socketio.run(app)
