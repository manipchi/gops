from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from game_logic import Game
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store active games and waiting player
games = {}
waiting_player = None  # Holds the waiting player's info (username and session ID)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    global waiting_player
    username = data['username']
    sid = request.sid  # Get the session ID of the player

    if waiting_player is None:
        # No players are waiting, so this player waits
        waiting_player = {'username': username, 'sid': sid}
        emit('waiting', {'message': 'Waiting for another player to join...'}, to=sid)
    else:
        # Pair this player with the waiting player
        player1 = waiting_player['username']
        player1_sid = waiting_player['sid']
        player2 = username
        player2_sid = sid
        waiting_player = None  # Reset waiting player

        room = f'room_{player1}_{player2}'

        # Make both players join the room
        socketio.server.enter_room(player1_sid, room)
        socketio.server.enter_room(player2_sid, room)

        # Notify both players
        socketio.emit('game_start', {'players': [player1, player2]}, room=room)

        # Start the game
        game = Game(room, [player1, player2], [player1_sid, player2_sid])
        games[room] = game

        # Send initial game state to both players individually
        for player in game.players:
            hand = game.get_player_hand(player)
            player_sid = game.player_sids[player]
            socketio.emit('update_hand', {'hand': hand}, to=player_sid)

        # Draw the first prize card
        prize_card = game.next_prize_card()
        socketio.emit('update_prize', {'prize_card': prize_card}, room=room)

@socketio.on('select_card')
def on_select_card(data):
    username = data['username']
    card = int(data['card'])  # Convert card to integer

    # Find the game this player is in
    room = None
    for game_room, game in games.items():
        if username in game.players:
            room = game_room
            break

    if room is None:
        emit('error', {'message': 'Game not found.'}, to=request.sid)
        return

    game = games.get(room)
    if game:
        game.update_selected_card(username, card)

        # Check if both players have made a selection
        if game.both_players_selected():
            # Process the round
            result = game.resolve_round()
            # Send round result to both players
            socketio.emit('round_result', result, room=room)

            # Check if the game is over
            if game.is_over():
                winner = game.get_winner()
                socketio.emit('game_over', {'winner': winner}, room=room)
                # Clean up
                del games[room]
            else:
                # Send updated hands to each player individually
                for player in game.players:
                    hand = game.get_player_hand(player)
                    player_sid = game.player_sids[player]
                    socketio.emit('update_hand', {'hand': hand}, to=player_sid)

                # Send next prize card to the room
                prize_card = game.next_prize_card()
                socketio.emit('update_prize', {'prize_card': prize_card}, room=room)
                # Clear selected cards for the next round
                game.clear_selected_cards()
        else:
            # Notify the other player that a selection has been made
            pass  # No action needed at this point

@socketio.on('disconnect')
def on_disconnect():
    global waiting_player
    sid = request.sid
    if waiting_player and waiting_player['sid'] == sid:
        waiting_player = None
    else:
        # Handle disconnection during a game
        # Find the game the player was in and notify the other player
        for room, game in list(games.items()):
            if sid in game.player_sids.values():
                other_player_sid = None
                for player_sid in game.player_sids.values():
                    if player_sid != sid:
                        other_player_sid = player_sid
                        break
                if other_player_sid:
                    socketio.emit('player_disconnected', {'message': 'The other player has disconnected.'}, to=other_player_sid)
                del games[room]
                break

if __name__ == '__main__':
    socketio.run(app)
