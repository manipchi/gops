import random


class Game:
    def __init__(self, room, players, sids):
        self.room = room
        self.players = players
        self.player_sids = dict(zip(players, sids))  # Map usernames to session IDs
        self.hands = {player: self.create_deck() for player in players}
        self.scores = {player: 0 for player in players}
        self.selected_cards = {player: None for player in players}
        self.prize_deck = self.create_deck()
        random.shuffle(self.prize_deck)
        self.accumulated_prizes = []
        self.current_prize_card = None

        # Debug logs
        print(f"Game initialized for room {self.room}")
        print(f"Players: {self.players}")
        print(f"Initial hands: {self.hands}")
        print(f"Shuffled prize deck: {self.prize_deck}")

    def create_deck(self):
        """Create a standard deck of cards (1 to 13)."""
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    def next_prize_card(self):
        """
        Draw the next prize card from the deck and add it to accumulated prizes.
        Returns:
            int: The current prize card.
        """
        if self.prize_deck:
            self.current_prize_card = self.prize_deck.pop(0)
            self.accumulated_prizes.append(self.current_prize_card)
            return self.current_prize_card
        return None

    def update_selected_card(self, player, card):
        """
        Update the card selected by the player.
        Args:
            player (str): The username of the player.
            card (int): The card selected by the player.
        """
        if card in self.hands[player]:
            self.selected_cards[player] = card

    def both_players_selected(self):
        """
        Check if both players have selected their cards.
        Returns:
            bool: True if both players have selected a card, False otherwise.
        """
        return all(card is not None for card in self.selected_cards.values())

    def resolve_round(self):
        """
        Resolve the current round and update the game state.
        Returns:
            tuple: Results for player1 and player2.
        """
        player1, player2 = self.players
        card1 = self.selected_cards[player1]
        card2 = self.selected_cards[player2]

        # Remove the selected cards from the players' hands
        self.hands[player1].remove(card1)
        self.hands[player2].remove(card2)

        # Determine round outcome
        result_player1 = {
            'opponent_card': card2,
            'your_card': card1,
            'message': '',
            'scores': self.scores.copy()
        }

        result_player2 = {
            'opponent_card': card1,
            'your_card': card2,
            'message': '',
            'scores': self.scores.copy()
        }

        if card1 > card2:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player1] += total_prize
            self.accumulated_prizes = []
            result_player1['message'] = f"You win the prize worth {total_prize}!"
            result_player2['message'] = f"Your opponent wins the prize worth {total_prize}!"
        elif card2 > card1:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player2] += total_prize
            self.accumulated_prizes = []
            result_player1['message'] = f"Your opponent wins the prize worth {total_prize}!"
            result_player2['message'] = f"You win the prize worth {total_prize}!"
        else:
            result_player1['message'] = "It's a tie! The prize cards accumulate."
            result_player2['message'] = "It's a tie! The prize cards accumulate."

        # Clear selected cards for the next round
        self.selected_cards = {player: None for player in self.players}

        return result_player1, result_player2

    def is_over(self):
        """
        Check if the game is over.
        Returns:
            bool: True if the game is over, False otherwise.
        """
        return not self.prize_deck and not self.accumulated_prizes

    def get_winner(self):
        """
        Determine the winner of the game based on scores.
        Returns:
            str: The username of the winner or 'Tie' if it's a tie.
        """
        player1, player2 = self.players
        if self.scores[player1] > self.scores[player2]:
            return player1
        elif self.scores[player2] > self.scores[player1]:
            return player2
        return 'Tie'

    def get_player_hand(self, player):
        """
        Get the player's current hand.
        Args:
            player (str): The username of the player.
        Returns:
            list: The player's hand.
        """
        return self.hands[player]

    def get_accumulated_prizes_display(self):
        """
        Get a display-friendly version of the accumulated prizes.
        Returns:
            list: The accumulated prizes.
        """
        return self.accumulated_prizes
