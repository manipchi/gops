from flask import Flask, render_template, request, redirect, flash, url_for
from flask_socketio import SocketIO, emit
from game_logic import Game
import random

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from utils import calculate_elo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://uqhmspm21ctn8:p1edca59a081df27c91fa6a40914e581578d80b12699508ca023022295ace9a2c@cbdhrtd93854d5.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8to4qqo86v29d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Store active games and waiting player
games = {}
waiting_player = None  # Holds the waiting player's info (username and session ID)


@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.elo.desc()).all()
    return render_template('leaderboard.html', users=users)

@socketio.on('join')
def on_join():
    global waiting_player

    if not current_user.is_authenticated:
        emit('error', {'message': 'You must be logged in to join a game.'}, to=request.sid)
        print("Join event failed: User not logged in.")  # Debug log
        return

    username = current_user.username
    sid = request.sid  # Get the session ID of the player

    print(f"Player {username} (SID: {sid}) is attempting to join.")  # Debug log

    if waiting_player and waiting_player['sid'] == sid:
        emit('error', {'message': 'You cannot join a game against yourself.'}, to=sid)
        print(f"Player {username} tried to join against themselves.")  # Debug log
        return

    if waiting_player is None:
        waiting_player = {'username': username, 'sid': sid}
        emit('waiting', {'message': 'Waiting for another player to join...'}, to=sid)
        print(f"Player {username} is now waiting for an opponent.")  # Debug log
    else:
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
        print(f"Game started between {player1} and {player2} in room {room}.")  # Debug log

        # Start the game
        game = Game(room, [player1, player2], [player1_sid, player2_sid])
        games[room] = game

        # Send initial game state to both players individually
        for player in game.players:
            hand = game.get_player_hand(player)
            player_sid = game.player_sids[player]
            print(f"Sending hand to {player}: {hand}")  # Debug log
            socketio.emit('update_hand', {'hand': hand}, to=player_sid)


        # Draw the first prize card
        prize_card = game.next_prize_card()
        accumulated_prizes = game.get_accumulated_prizes_display()
        print(f"Prize card: {prize_card}, Accumulated prizes: {accumulated_prizes}")  # Debug log
        socketio.emit('update_prize', {'prize_card': prize_card, 'accumulated_prizes': accumulated_prizes}, room=room)


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
            # Process the round and get personalized results
            result_player1, result_player2 = game.resolve_round()

            # Send results to each player
            player1_sid = game.player_sids[game.players[0]]
            player2_sid = game.player_sids[game.players[1]]

            socketio.emit('round_result', result_player1, to=player1_sid)
            socketio.emit('round_result', result_player2, to=player2_sid)

            # Clear selected cards for the next round
            game.clear_selected_cards()

            # Check if the game is over
            if game.is_over():
                game_details = game.get_game_over_details()
                socketio.emit('game_over', game_details, room=room)
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
                accumulated_prizes = game.get_accumulated_prizes_display()
                socketio.emit('update_prize', {'prize_card': prize_card, 'accumulated_prizes': accumulated_prizes}, room=room)

@socketio.on('game_over')
def handle_game_over(data):
    winner_username = data.get('winner')
    players = data.get('players')
    room = data.get('room')

    if not winner_username or not players or not room:
        return

    player1 = User.query.filter_by(username=players[0]).first()
    player2 = User.query.filter_by(username=players[1]).first()

    if not player1 or not player2:
        return

    # Update Elo ratings based on the game outcome
    if winner_username == player1.username:
        calculate_elo(player1, player2)
    elif winner_username == player2.username:
        calculate_elo(player2, player1)

    db.session.commit()

    # Notify players of updated Elo ratings
    socketio.emit('elo_update', {
        'player1': {'username': player1.username, 'elo': player1.elo},
        'player2': {'username': player2.username, 'elo': player2.elo}
    }, room=room)


@socketio.on('disconnect')
def on_disconnect():
    global waiting_player
    sid = request.sid

    if waiting_player and waiting_player['sid'] == sid:
        waiting_player = None  # Remove the waiting player
    else:
        # Handle disconnection during a game
        for room, game in list(games.items()):
            if sid in game.player_sids.values():
                # Find the other player in the game
                other_player_sid = None
                for player_sid in game.player_sids.values():
                    if player_sid != sid:
                        other_player_sid = player_sid
                        break

                # Notify the other player about the disconnection
                if other_player_sid:
                    socketio.emit(
                        'player_disconnected',
                        {'message': 'Your opponent has disconnected. The game is over.'},
                        to=other_player_sid
                    )

                # Remove the game from active games
                del games[room]
                break


if __name__ == '__main__':
    socketio.run(app)
