import random

class Game:
    def __init__(self, room, players, sids):
        self.room = room
        self.players = players
        self.player_sids = dict(zip(players, sids))  # Map usernames to session IDs
        self.hands = {player: self.create_deck() for player in players}  # Generate hands
        self.scores = {player: 0 for player in players}  # Initialize scores
        self.selected_cards = {player: None for player in players}
        self.prize_deck = self.create_deck()  # Generate prize deck
        random.shuffle(self.prize_deck)  # Shuffle the prize deck
        self.accumulated_prizes = []
        self.current_prize_card = None

        # Debugging logs
        print(f"Game initialized for room {self.room}")
        print(f"Players: {self.players}")
        print(f"Initial hands: {self.hands}")
        print(f"Shuffled prize deck: {self.prize_deck}")

    def create_deck(self):
        """Create a standard deck of cards as numbers 1-13."""
        return list(range(1, 14))  # 1-13 where 1=A, 11=J, 12=Q, 13=K

    def display_card(self, card):
        """Convert a numerical card to its display value (A, 2-10, J, Q, K)."""
        display_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        return display_map.get(card, str(card))  # Default to the number as a string

    def next_prize_card(self):
        """
        Draw the next prize card from the deck and add it to accumulated prizes.
        Returns:
            int: The current prize card.
        """
        if self.prize_deck:
            self.current_prize_card = self.prize_deck.pop(0)
            self.accumulated_prizes.append(self.current_prize_card)
            print(f"Next prize card: {self.current_prize_card}, Accumulated prizes: {self.accumulated_prizes}")  # Debug log
            return self.current_prize_card
        print("No more prize cards in the deck.")  # Debug log
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
            print(f"{player} selected card {card}. Selected cards: {self.selected_cards}")  # Debug log


    def both_players_selected(self):
        """
        Check if both players have selected their cards.
        Returns:
            bool: True if both players have selected a card, False otherwise.
        """
        return all(card is not None for card in self.selected_cards.values())


    def resolve_round(self):
        player1, player2 = self.players

        card1 = self.selected_cards[player1]
        card2 = self.selected_cards[player2]

        # Remove the selected cards from the players' hands
        self.hands[player1].remove(card1)
        self.hands[player2].remove(card2)

        # Determine round outcome
        if card1 > card2:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player1] += total_prize
            self.accumulated_prizes = []
            result_player1 = {
                'opponent_card': self.display_card(card2),
                'your_card': self.display_card(card1),
                'message': f"You win the prize worth {total_prize}!",
                'scores': self.scores.copy()
            }
            result_player2 = {
                'opponent_card': self.display_card(card1),
                'your_card': self.display_card(card2),
                'message': f"Your opponent wins the prize worth {total_prize}!",
                'scores': self.scores.copy()
            }
        elif card2 > card1:
            total_prize = sum(self.accumulated_prizes)
            self.scores[player2] += total_prize
            self.accumulated_prizes = []
            result_player1 = {
                'opponent_card': self.display_card(card2),
                'your_card': self.display_card(card1),
                'message': f"Your opponent wins the prize worth {total_prize}!",
                'scores': self.scores.copy()
            }
            result_player2 = {
                'opponent_card': self.display_card(card1),
                'your_card': self.display_card(card2),
                'message': f"You win the prize worth {total_prize}!",
                'scores': self.scores.copy()
            }
        else:
            self.accumulated_prizes.append(self.current_prize_card)
            result_player1 = {
                'opponent_card': self.display_card(card2),
                'your_card': self.display_card(card1),
                'message': "It's a tie! The prize cards accumulate.",
                'scores': self.scores.copy()
            }
            result_player2 = {
                'opponent_card': self.display_card(card1),
                'your_card': self.display_card(card2),
                'message': "It's a tie! The prize cards accumulate.",
                'scores': self.scores.copy()
            }
            print(f"Tie! Accumulated prizes: {self.accumulated_prizes}")  # Debug log

        # Reset selected cards for the next round
        self.selected_cards = {player: None for player in self.players}

        print(f"Scores after round: {self.scores}")  # Debug log
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
        Get the player's current hand as display-friendly values.
        Args:
            player (str): The username of the player.
        Returns:
            list: The player's hand as display values.
        """
        print(f"Hand for {player}: {self.hands[player]}")  # Debug log
        return [self.display_card(card) for card in self.hands[player]]


    def get_accumulated_prizes_display(self):
        """
        Get a display-friendly version of the accumulated prizes.
        Returns:
            list: The accumulated prizes as display values.
        """
        return [self.display_card(card) for card in self.accumulated_prizes]

