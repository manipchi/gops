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
                # Clear selected cards for the next round
                game.clear_selected_cards()
