import random

class Game:
    def __init__(self, room, players, sids):
        self.room = room
        self.players = players  # List of player usernames
        self.player_sids = dict(zip(players, sids))  # Map usernames to session IDs
        self.hands = {}
        self.scores = {}
        self.selected_cards = {}  # Store the currently selected card for each player
        self.prize_deck = self.create_deck()
        random.shuffle(self.prize_deck)
        self.accumulated_prizes = []
        self.current_prize_card = None

        for player in players:
            self.hands[player] = self.create_deck()
            self.scores[player] = 0
            self.selected_cards[player] = None

    def create_deck(self):
        """Create a deck with face cards represented as 'A', 'J', 'Q', 'K'."""
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    def next_prize_card(self):
        """Draw the next prize card and add it to accumulated prizes."""
        if self.prize_deck:
            self.current_prize_card = self.prize_deck.pop(0)
            self.accumulated_prizes.append(self.current_prize_card)
            return self.card_value_to_display(self.current_prize_card)
        else:
            self.current_prize_card = None
            return None

    def update_selected_card(self, player, card):
        """Update the selected card for a player."""
        card = int(card)
        if card in self.hands[player]:
            self.selected_cards[player] = card

    def both_players_selected(self):
        """Check if both players have selected their cards."""
        return all(card is not None for card in self.selected_cards.values())

    def resolve_round(self):
        """Resolve the round and update the game state."""
        player1, player2 = self.players
        card1 = self.selected_cards[player1]
        card2 = self.selected_cards[player2]

        # Remove the played cards from players' hands
        if card1 in self.hands[player1]:
            self.hands[player1].remove(card1)
        if card2 in self.hands[player2]:
            self.hands[player2].remove(card2)

        # Generate round result messages
        result_player1 = {
            'opponent_card': self.card_value_to_display(card2),
            'your_card': self.card_value_to_display(card1),
            'scores': self.scores.copy(),
            'message': ''
        }

        result_player2 = {
            'opponent_card': self.card_value_to_display(card1),
            'your_card': self.card_value_to_display(card2),
            'scores': self.scores.copy(),
            'message': ''
        }

        if card1 > card2:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player1] += total_prize
            result_player1['message'] = f"Opponent played {self.card_value_to_display(card2)}. You win the prize worth {total_prize}!"
            result_player2['message'] = f"Opponent played {self.card_value_to_display(card1)}. They win the prize worth {total_prize}!"
            self.accumulated_prizes.clear()
        elif card2 > card1:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player2] += total_prize
            result_player1['message'] = f"Opponent played {self.card_value_to_display(card2)}. They win the prize worth {total_prize}!"
            result_player2['message'] = f"Opponent played {self.card_value_to_display(card1)}. You win the prize worth {total_prize}!"
            self.accumulated_prizes.clear()
        else:
            result_player1['message'] = f"Both players played {self.card_value_to_display(card1)}. It's a tie! The prize cards accumulate."
            result_player2['message'] = f"Both players played {self.card_value_to_display(card2)}. It's a tie! The prize cards accumulate."

        return result_player1, result_player2



    def clear_selected_cards(self):
        """Clear the selected cards for the next round."""
        for player in self.players:
            self.selected_cards[player] = None

    def is_over(self):
        """Check if the game is over."""
        return not self.prize_deck and not self.accumulated_prizes

    def get_winner(self):
        """Determine the winner of the game."""
        player1, player2 = self.players
        score1 = self.scores[player1]
        score2 = self.scores[player2]
        if score1 > score2:
            return player1
        elif score2 > score1:
            return player2
        else:
            return 'Tie'

    def get_game_over_details(self):
        """Return game over details including the winner and accumulated prizes."""
        return {
            'winner': self.get_winner(),
            'accumulated_prizes': self.get_accumulated_prizes_display() if self.get_winner() == 'Tie' else []
        }

    def get_player_hand(self, player):
        """Get the player's hand as display-friendly card values."""
        return [self.card_value_to_display(card) for card in self.hands[player]]

    def get_accumulated_prizes_display(self):
        """Get the accumulated prizes as display-friendly card values."""
        return [self.card_value_to_display(card) for card in self.accumulated_prizes]

    def card_value_to_display(self, value):
        """Convert numeric card value to display value."""
        if value == 1:
            return 'A'
        elif value == 11:
            return 'J'
        elif value == 12:
            return 'Q'
        elif value == 13:
            return 'K'
        else:
            return str(value)
