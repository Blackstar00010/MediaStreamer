import sqlite3
from backend.db_utils import get_elo_rating
from backend.config import DB_PATH

K = 32  # Elo rating adjustment factor

def update_elo_rating(winner_id: int, loser_id: int):
    """Update the Elo ratings of two albums after a comparison."""
    winner_elo = get_elo_rating(winner_id)
    loser_elo = get_elo_rating(loser_id)

    # Expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_loser = 1 - expected_winner

    # New ratings
    new_winner_elo = round(winner_elo + K * (1 - expected_winner))
    new_loser_elo = round(loser_elo + K * (0 - expected_loser))

    # Update database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE albums SET elo = ? WHERE id = ?", (new_winner_elo, winner_id))
    cursor.execute("UPDATE albums SET elo = ? WHERE id = ?", (new_loser_elo, loser_id))
    conn.commit()
    conn.close()

    return {"message": "Elo ratings updated", "winner_new_elo": new_winner_elo, "loser_new_elo": new_loser_elo}