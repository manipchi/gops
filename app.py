# app.py

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import Game
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store active games
games = {}
users_in_room = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    join_room(room)
    users_in_room.setdefault(room, []).append(username)

    if len(users_in_room[room]) == 2:
        # Start the game when two players have joined
        game = Game(room, users_in_room[room])
        games[room] = game

        # Notify both players that the game is starting
        socketio.emit('game_start', {'players': users_in_room[room]}, room=room)

        # Send initial game state to both players
        for player in users_in_room[room]:
            hand = game.get_player_hand(player)
            socketio.emit('update_hand', {'hand': hand}, room=room, include_self=False)

        # Draw the first prize card
        prize_card = game.next_prize_card()
        socketio.emit('update_prize', {'prize_card': prize_card}, room=room)
    else:
        # Wait for another player
        emit('waiting', {'message': 'Waiting for another player to join...'}, room=room)

@socketio.on('play_card')
def on_play_card(data):
    room = data['room']
    username = data['username']
    card = data['card']

    game = games.get(room)
    if game:
        game.play_card(username, card)

        if game.both_players_played():
            result = game.resolve_round()
            # Send round result to both players
            socketio.emit('round_result', result, room=room)

            # Check if the game is over
            if game.is_over():
                winner = game.get_winner()
                socketio.emit('game_over', {'winner': winner}, room=room)
                # Clean up
                del games[room]
                del users_in_room[room]
            else:
                # Send updated hands and next prize card
                for player in game.players:
                    hand = game.get_player_hand(player)
                    socketio.emit('update_hand', {'hand': hand}, room=room, include_self=False)

                prize_card = game.next_prize_card()
                socketio.emit('update_prize', {'prize_card': prize_card}, room=room)
        else:
            # Wait for the other player
            pass

@socketio.on('disconnect')
def on_disconnect():
    # Handle player disconnection
    pass

if __name__ == '__main__':
    socketio.run(app)
