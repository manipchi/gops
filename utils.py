def calculate_elo(winner, loser, k=32):
    """
    Standard Elo update for a decisive result.
    winner and loser are User objects.
    """
    R_A = winner.elo
    R_B = loser.elo

    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 - E_A

    # Winner gets S=1, loser gets S=0
    winner.elo = winner.elo + int(k * (1 - E_A))
    loser.elo = loser.elo + int(k * (0 - E_B))

def calculate_elo_tie(player1, player2, k=16):
    """
    Minimal Elo adjustments for a tie.
    """
    R_A = player1.elo
    R_B = player2.elo

    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 - E_A

    # On a tie, S=0.5 for both
    player1.elo = player1.elo + int(k * (0.5 - E_A))
    player2.elo = player2.elo + int(k * (0.5 - E_B))
