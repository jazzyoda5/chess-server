from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__, static_folder='../chess-client/build', static_url_path='/')
socketio = SocketIO(app)

# Room: Num_Of_Users
rooms = {}


@app.route('/')
def index():
    return app.send_static_file('index.html')
    


@app.route('/flaskserver')
def serve_app():
    return 'Welcome to me bitch.'

@socketio.on('move')
def handle_move(data):
    print('[RECIEVED] Move.')
    emit('move', data, broadcast=True)


@socketio.on('message')
def handle_message(data):
    print('[MESSAGE RECIEVED] {}'.format(data))


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


@socketio.on('leave')
def handle_leave(data):
    print('room_id', data['room_id'])
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


@socketio.on('connect')
def handle_connect():
    print('[NEW CONNECTION] New user connected.')


@socketio.on('disconnect')
def handle_disconnect():
    print('[DISCONNECTED] User has disconnected.')


if __name__ == '__main__':
    socketio.run(app)
