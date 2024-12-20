from flask import Flask, render_template, request, redirect, flash, url_for
from flask_socketio import SocketIO, emit
from game_logic import Game
import random

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from utils import calculate_elo, calculate_elo_tie


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

        # Check if username or email is already taken
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username is already taken.")
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email is already registered.")

        # Create the new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Use the set_password method to hash the password
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error="Username does not exist.")

        # Check the password using the check_password method
        if not user.check_password(password):
            return render_template('login.html', error="Incorrect password.")

        # Log in the user
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('index'))

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
    username = current_user.username
    sid = request.sid  # Get the session ID of the player

    print(f"Join event received from user: {username}, session ID: {sid}")  # Debugging log

    # Check if the player is trying to join a game against themselves
    if waiting_player and waiting_player['sid'] == sid:
        emit('error', {'message': 'You cannot join a game against yourself.'}, to=sid)
        return

    if waiting_player is None:
        # If no waiting player, make the current player wait
        waiting_player = {'username': username, 'sid': sid}
        emit('waiting', {'message': 'Waiting for another player to join...'}, to=sid)
        print(f"{username} is now waiting for an opponent.")  # Debugging log
    else:
        # Match the current player with the waiting player
        player1 = waiting_player['username']
        player1_sid = waiting_player['sid']
        player2 = username
        player2_sid = sid
        waiting_player = None  # Reset the waiting player

        # Create a unique room for this game
        room = f'room_{player1}_{player2}'

        # Add both players to the room
        socketio.server.enter_room(player1_sid, room)
        socketio.server.enter_room(player2_sid, room)

        print(f"Game initialized for room {room}")  # Debugging log
        print(f"Players: {player1}, {player2}")

        # Notify both players that the game has started
        socketio.emit('game_start', {'players': [player1, player2]}, room=room)

        # Initialize the game
        game = Game(room, [player1, player2], [player1_sid, player2_sid])
        games[room] = game

        # Emit the initial hands and prize card to both players
        for player in game.players:
            hand = game.get_player_hand(player)
            player_sid = game.player_sids[player]
            print(f"Hand for {player}: {hand}")  # Debugging log
            socketio.emit('update_hand', {'hand': hand}, to=player_sid)

        prize_card = game.next_prize_card()
        accumulated_prizes = game.get_accumulated_prizes_display()
        print(f"Next prize card: {prize_card}, Accumulated prizes: {accumulated_prizes}")  # Debugging log
        socketio.emit('update_prize', {'prize_card': prize_card, 'accumulated_prizes': accumulated_prizes}, room=room)



@socketio.on('select_card')
def on_select_card(data):
    username = current_user.username
    card = int(data['card'])  # Card is now guaranteed to be a number

    # Find the game this player is in
    room = None
    for game_room, game in games.items():
        if username in game.players:
            room = game_room
            break

    if not room:
        emit('error', {'message': 'Game not found.'}, to=request.sid)
        return

    game = games.get(room)
    game.update_selected_card(username, card)

    print(f"Player {username} selected card: {card}")  # Debug log

    # Check if both players have made a selection
    if game.both_players_selected():
        print(f"Both players have selected: {game.selected_cards}")  # Debug log

        # Process the round
        result_player1, result_player2 = game.resolve_round()

        # Emit round results
        player1_sid = game.player_sids[game.players[0]]
        player2_sid = game.player_sids[game.players[1]]

        socketio.emit('round_result', result_player1, to=player1_sid)
        socketio.emit('round_result', result_player2, to=player2_sid)

        # Check if the game is over
        if game.is_over():
            winner_username = game.get_winner()
            players = game.players

            player1 = User.query.filter_by(username=players[0]).first()
            player2 = User.query.filter_by(username=players[1]).first()

            if not player1 or not player2:
                print("Error: Could not find user records for Elo calculation.")
            else:
                print(f"Game ended. Winner: {winner_username}. Updating Elo...")

                if winner_username == 'Tie':
                    # Tie logic
                    calculate_elo_tie(player1, player2, k=16)
                else:
                    # Winner-loser logic
                    if winner_username == player1.username:
                        winner, loser = player1, player2
                    else:
                        winner, loser = player2, player1
                    calculate_elo(winner, loser, k=32)

                db.session.commit()
                print(f"Elo updated: {player1.username}: {player1.elo}, {player2.username}: {player2.elo}")

            # Now emit the event to the clients if you want them to know the game ended
            game_details = {
                'winner': winner_username,
                'players': players,
                'final_scores': game.scores
            }
            socketio.emit('game_over', game_details, room=room)
            print("Game over event emitted to clients.")
            del games[room]


        else:
            # Emit updated hands and next prize card
            for player in game.players:
                hand = game.get_player_hand(player)
                player_sid = game.player_sids[player]
                socketio.emit('update_hand', {'hand': hand}, to=player_sid)

            prize_card = game.next_prize_card()
            accumulated_prizes = game.get_accumulated_prizes_display()
            socketio.emit('update_prize', {'prize_card': prize_card, 'accumulated_prizes': accumulated_prizes}, room=room)

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
