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
        if self.prize_deck:
            self.current_prize_card = self.prize_deck.pop(0)
            self.accumulated_prizes.append(self.current_prize_card)
            return self.card_value_to_display(self.current_prize_card)
        else:
            self.current_prize_card = None
            return None

    def update_selected_card(self, player, card):
        card = int(card)  # Ensure the card is an integer
        if card in self.hands[player]:
            self.selected_cards[player] = card

    def both_players_selected(self):
        return all(card is not None for card in self.selected_cards.values())

    def resolve_round(self):
        player1, player2 = self.players
        card1 = self.selected_cards[player1]
        card2 = self.selected_cards[player2]

        # Remove the played cards from players' hands
        self.hands[player1].remove(card1)
        self.hands[player2].remove(card2)

        result = {
            'player1': player1,
            'player2': player2,
            'card1': self.card_value_to_display(card1),
            'card2': self.card_value_to_display(card2),
            'message': ''
        }

        if card1 > card2:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player1] += total_prize
            result['message'] = f"{player1} wins the accumulated prizes worth {total_prize}!"
            self.accumulated_prizes.clear()
        elif card2 > card1:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player2] += total_prize
            result['message'] = f"{player2} wins the accumulated prizes worth {total_prize}!"
            self.accumulated_prizes.clear()
        else:
            result['message'] = "It's a tie! The prize cards accumulate."

        result['scores'] = self.scores.copy()
        return result

    def clear_selected_cards(self):
        for player in self.players:
            self.selected_cards[player] = None

    def is_over(self):
        return not self.prize_deck and not self.accumulated_prizes

    def get_winner(self):
        player1, player2 = self.players
        score1 = self.scores[player1]
        score2 = self.scores[player2]
        if score1 > score2:
            return player1
        elif score2 > score1:
            return player2
        else:
            return 'Tie'

    def get_player_hand(self, player):
        return [self.card_value_to_display(card) for card in self.hands[player]]
    
    def get_accumulated_prizes_display(self):
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
