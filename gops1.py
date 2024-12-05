import tkinter as tk
from tkinter import messagebox
import random

# -------------------- Customizable Settings --------------------

# Font Settings
FONT_NAME = "Courier New"  # Change to your preferred font
FONT_SIZES = {
    'prize_label': 40,          # Adjusted font size
    'accumulated_label': 36,    # Adjusted font size
    'hand_label': 20,           # Adjusted font size
    'button': 40,               # Adjusted font size
    'score_label': 20,          # Adjusted font size
    'last_bids_label': 30,      # Adjusted font size
    'round_result_label': 20    # Adjusted font size
}

# Color Settings
THEME_COLOR = "#37A908"  # Main theme color
TEXT_COLOR = "white"     # Text color for labels
BUTTON_BG_COLOR = "white"  # Button background color
BUTTON_TEXT_COLOR = THEME_COLOR  # Button text color

# Delay Settings
DELAY_BETWEEN_ROUNDS = 1000  # Delay between rounds in milliseconds

# Window Settings
INITIAL_WINDOW_SIZE = "600x500"  # Width x Height

# ---------------------------------------------------------------

class GoofspielGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Goofspiel Game")
        self.master.geometry(INITIAL_WINDOW_SIZE)
        self.master.resizable(True, True)  # Allow window resizing

        # Set the background color
        self.master.configure(bg=THEME_COLOR)

        # Initialize decks
        self.prize_deck = self.create_deck()
        random.shuffle(self.prize_deck)
        self.player_hand = self.create_deck()
        self.ai_hand = self.create_deck()

        # Initialize scores and accumulated prizes
        self.player_score = 0
        self.ai_score = 0
        self.accumulated_prizes = []

        # Initialize messages
        self.last_bids_message = ""
        self.round_result_message = ""

        # Set up GUI elements
        self.setup_gui()

        # Start the game
        self.next_round()

    def create_deck(self):
        """Create a deck with face cards represented as 'J', 'Q', 'K'."""
        deck = list(range(1, 14))
        return deck

    def card_value_to_display(self, value):
        """Convert numeric card value to display value."""
        if value == 11:
            return 'J'
        elif value == 12:
            return 'Q'
        elif value == 13:
            return 'K'
        else:
            return str(value)

    def display_to_card_value(self, display):
        """Convert display value back to numeric card value."""
        if display == 'J':
            return 11
        elif display == 'Q':
            return 12
        elif display == 'K':
            return 13
        else:
            return int(display)

    def setup_gui(self):
        # Configure grid layout
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(list(range(7)), weight=1)

        # Prize card display
        self.prize_label = tk.Label(
            self.master,
            text="Prize Card: ",
            font=(FONT_NAME, FONT_SIZES['prize_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.prize_label.grid(row=0, column=0, pady=5, sticky="N")

        # Accumulated prizes display
        self.accumulated_label = tk.Label(
            self.master,
            text="Accumulated Prizes: ",
            font=(FONT_NAME, FONT_SIZES['accumulated_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.accumulated_label.grid(row=1, column=0, pady=5, sticky="N")

        # Last bids display
        self.last_bids_label = tk.Label(
            self.master,
            text="",
            font=(FONT_NAME, FONT_SIZES['last_bids_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.last_bids_label.grid(row=2, column=0, pady=5, sticky="N")

        # Round result display
        self.round_result_label = tk.Label(
            self.master,
            text="",
            font=(FONT_NAME, FONT_SIZES['round_result_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.round_result_label.grid(row=3, column=0, pady=5, sticky="N")

        # Player's hand
        self.hand_label = tk.Label(
            self.master,
            text="Your Hand:",
            font=(FONT_NAME, FONT_SIZES['hand_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.hand_label.grid(row=4, column=0, pady=5, sticky="N")

        self.card_buttons_frame = tk.Frame(self.master, bg=THEME_COLOR)
        self.card_buttons_frame.grid(row=5, column=0, sticky="NSEW", padx=10, pady=5)
        self.card_buttons_frame.columnconfigure(tuple(range(13)), weight=1)

        self.card_buttons = []
        for idx, card in enumerate(sorted(self.player_hand)):
            display_value = self.card_value_to_display(card)
            btn = tk.Button(
                self.card_buttons_frame,
                text=display_value,
                font=(FONT_NAME, FONT_SIZES['button']),
                command=lambda c=card: self.player_bid(c),
                bg=BUTTON_BG_COLOR,
                fg=BUTTON_TEXT_COLOR,
                activebackground=THEME_COLOR,
                activeforeground=TEXT_COLOR,
                highlightbackground=THEME_COLOR
            )
            btn.grid(row=0, column=idx, sticky="NSEW", padx=2, pady=2)
            self.card_buttons.append(btn)

        # Score display
        self.score_label = tk.Label(
            self.master,
            text="Scores - You: 0 | AI: 0",
            font=(FONT_NAME, FONT_SIZES['score_label']),
            bg=THEME_COLOR,
            fg=TEXT_COLOR
        )
        self.score_label.grid(row=6, column=0, pady=10, sticky="S")

        # Remove the dynamic font resizing by commenting out the binding
        # self.master.bind('<Configure>', self.on_resize)

    # Remove or comment out the on_resize method
    # def on_resize(self, event):
    #     pass

    def update_hand_buttons(self):
        for btn in self.card_buttons:
            card_value = self.display_to_card_value(btn['text'])
            if card_value in self.player_hand:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)

    def next_round(self):
        if not self.prize_deck and not self.accumulated_prizes:
            self.end_game()
            return

        # Draw the next prize card
        if self.prize_deck:
            prize_card = self.prize_deck.pop(0)
            self.accumulated_prizes.append(prize_card)
            display_value = self.card_value_to_display(prize_card)
            self.prize_label.config(text=f"Prize Card: {display_value}")
        else:
            self.prize_label.config(text="No more prize cards.")

        accumulated_display = [self.card_value_to_display(val) for val in self.accumulated_prizes]
        self.accumulated_label.config(text=f"Accumulated Prizes: {accumulated_display}")
        self.update_hand_buttons()

        # Clear last bids and round result messages
        self.last_bids_label.config(text="")
        self.round_result_label.config(text="")

    def player_bid(self, bid):
        self.player_hand.remove(bid)
        self.update_hand_buttons()

        # AI makes a bid
        ai_bid = self.ai_make_bid()

        # Display bids
        player_bid_display = self.card_value_to_display(bid)
        ai_bid_display = self.card_value_to_display(ai_bid)
        self.last_bids_message = f"You bid: {player_bid_display} | AI bids: {ai_bid_display}"
        self.last_bids_label.config(text=self.last_bids_message)

        # Determine the winner
        if bid > ai_bid:
            total_prize = sum(self.accumulated_prizes)
            self.player_score += total_prize
            self.round_result_message = f"You win the accumulated prizes worth {total_prize}!"
            self.accumulated_prizes.clear()
        elif ai_bid > bid:
            total_prize = sum(self.accumulated_prizes)
            self.ai_score += total_prize
            self.round_result_message = f"AI wins the accumulated prizes worth {total_prize}!"
            self.accumulated_prizes.clear()
        else:
            self.round_result_message = "It's a tie! The prize cards accumulate."

        # Update round result display
        self.round_result_label.config(text=self.round_result_message)

        # Update scores
        self.score_label.config(text=f"Scores - You: {self.player_score} | AI: {self.ai_score}")
        accumulated_display = [self.card_value_to_display(val) for val in self.accumulated_prizes]
        self.accumulated_label.config(text=f"Accumulated Prizes: {accumulated_display}")

        # Proceed to the next round after a short delay
        self.master.after(DELAY_BETWEEN_ROUNDS, self.next_round)

    def ai_make_bid(self):
        # Simple AI strategy
        if not self.ai_hand:
            return 0

        # AI tries to win if accumulated prizes are high
        if sum(self.accumulated_prizes) > 20:
            bid = max(self.ai_hand)
            self.ai_hand.remove(bid)
            return bid

        # AI bids randomly from available cards
        bid = random.choice(self.ai_hand)
        self.ai_hand.remove(bid)
        return bid

    def end_game(self):
        # Determine the winner
        if self.player_score > self.ai_score:
            winner_message = "Congratulations! You win the game!"
        elif self.ai_score > self.player_score:
            winner_message = "AI wins the game! Better luck next time."
        else:
            winner_message = "The game is a tie!"

        # Display final scores and winner
        final_message = f"Final Scores - You: {self.player_score} | AI: {self.ai_score}\n{winner_message}"
        messagebox.showinfo("Game Over", final_message)

        # Disable all buttons
        for btn in self.card_buttons:
            btn.config(state=tk.DISABLED)

        # Optionally, ask to play again
        play_again = messagebox.askyesno("Play Again", "Do you want to play again?")
        if play_again:
            self.restart_game()
        else:
            self.master.quit()

    def restart_game(self):
        # Reset game state
        self.prize_deck = self.create_deck()
        random.shuffle(self.prize_deck)
        self.player_hand = self.create_deck()
        self.ai_hand = self.create_deck()
        self.player_score = 0
        self.ai_score = 0
        self.accumulated_prizes = []
        self.last_bids_message = ""
        self.round_result_message = ""

        # Reset GUI elements
        self.prize_label.config(text="Prize Card: ")
        self.accumulated_label.config(text="Accumulated Prizes: ")
        self.score_label.config(text="Scores - You: 0 | AI: 0")
        self.last_bids_label.config(text="")
        self.round_result_label.config(text="")

        for btn in self.card_buttons:
            btn.config(state=tk.NORMAL)

        # Start the game
        self.next_round()

if __name__ == "__main__":
    root = tk.Tk()
    game = GoofspielGame(root)
    root.mainloop()
