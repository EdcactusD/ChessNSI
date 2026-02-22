import json
import os
import random
import chess

FICHIER_LIVRE = os.path.join(os.path.dirname(__file__), "opening_book.json")

_cache_livre = None


def charger_livre() -> dict:
    global _cache_livre
    if _cache_livre is not None:
        return _cache_livre
    if os.path.exists(FICHIER_LIVRE):
        try:
            with open(FICHIER_LIVRE, "r") as f:
                _cache_livre = json.load(f)
        except (json.JSONDecodeError, IOError):
            _cache_livre = {}
    else:
        _cache_livre = {}
    return _cache_livre


def obtenir_coup_ouverture(board: chess.Board):
    livre = charger_livre()
    cle_fen = board.board_fen()
    entrees = livre.get(cle_fen)

    if not entrees:
        return None

    # Filtre les coups légaux uniquement
    entrees_legales = []
    for entree in entrees:
        try:
            coup = chess.Move.from_uci(entree["move"])
            if coup in board.legal_moves:
                entrees_legales.append((coup, entree.get("weight", 1)))
        except ValueError:
            continue

    if not entrees_legales:
        return None

    # Sélection pondérée (plus le weight est élevé, plus c'est joué)
    coups, poids = zip(*entrees_legales)
    choisi = random.choices(coups, weights=poids, k=1)[0]
    return choisi