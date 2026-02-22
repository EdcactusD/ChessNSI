import json
import os
import random
import chess

BOOK_FILE = os.path.join(os.path.dirname(__file__), "opening_book.json")

_book_cache = None


def load_book() -> dict:
    global _book_cache
    if _book_cache is not None:
        return _book_cache
    if os.path.exists(BOOK_FILE):
        try:
            with open(BOOK_FILE, "r") as f:
                _book_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            _book_cache = {}
    else:
        _book_cache = {}
    return _book_cache


def get_opening_move(board: chess.Board):
    book = load_book()
    fen_key = board.board_fen()
    entries = book.get(fen_key)

    if not entries:
        return None

    # Filtre les coups légaux uniquement
    legal_entries = []
    for entry in entries:
        try:
            move = chess.Move.from_uci(entry["move"])
            if move in board.legal_moves:
                legal_entries.append((move, entry.get("weight", 1)))
        except ValueError:
            continue

    if not legal_entries:
        return None

    # Sélection pondérée (plus le weight est élevé, plus c'est joué)
    moves, weights = zip(*legal_entries)
    chosen = random.choices(moves, weights=weights, k=1)[0]
    return chosen