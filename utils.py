def calculate_elo(winner, loser, k=32):
    # winner and loser are User objects
    expected_winner = 1 / (1 + 10 ** ((loser.elo - winner.elo) / 400))
    expected_loser = 1 - expected_winner

    # Winner gets 1 point, loser gets 0
    winner.elo += int(k * (1 - expected_winner))
    loser.elo += int(k * (0 - expected_loser))

def calculate_elo_tie(player1, player2, k=32):
    """
    Adjust Elo ratings for a tie.
    Using a smaller k (e.g., 16) so that changes are minimal.
    """
    R_A = player1.elo
    R_B = player2.elo

    # Calculate expected scores
    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 - E_A

    # Both players get S=0.5 for a tie
    # Rating update:
    # R_A' = R_A + k*(0.5 - E_A)
    # R_B' = R_B + k*(0.5 - E_B)

    player1.elo = player1.elo + int(k * (0.5 - E_A))
    player2.elo = player2.elo + int(k * (0.5 - E_B))

