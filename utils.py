def calculate_elo(winner, loser, k=32):
    """
    Adjust Elo ratings for the winner and loser based on the Elo formula.

    Args:
        winner (User): The User object of the winner.
        loser (User): The User object of the loser.
        k (int): The adjustment factor (default: 32).
    """
    # Calculate expected scores
    expected_winner = 1 / (1 + 10 ** ((loser.elo - winner.elo) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.elo - loser.elo) / 400))

    # Update Elo ratings
    winner.elo += int(k * (1 - expected_winner))
    loser.elo += int(k * (0 - expected_loser))
