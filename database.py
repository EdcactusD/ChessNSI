# database.py
import sqlite3
from datetime import datetime

DB_NAME = "chess_games.db"

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        white_ai TEXT,
        black_ai TEXT,
        result TEXT,
        moves_white TEXT,
        moves_black TEXT,
        date_played TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_game(white_ai, black_ai, result, moves_white, moves_black):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO games (white_ai, black_ai, result, moves_white, moves_black, date_played)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        white_ai,
        black_ai,
        result,
        " ".join(moves_white),
        " ".join(moves_black),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
