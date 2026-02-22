import json
import os
import chess

FICHIER_MEMOIRE = os.path.join(os.path.dirname(__file__), "memory.json")
TAILLE_MAX_MEMOIRE = 5_000_000
SEUIL_VISITES_MIN = 2

_cache_memoire = None


def charger_memoire() -> dict:
    global _cache_memoire
    if _cache_memoire is not None:
        return _cache_memoire
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f:
                _cache_memoire = json.load(f)
        except (json.JSONDecodeError, IOError):
            _cache_memoire = {}
    else:
        _cache_memoire = {}
    return _cache_memoire


def sauvegarder_memoire() -> None:
    global _cache_memoire
    if _cache_memoire is None:
        return
    try:
        with open(FICHIER_MEMOIRE, "w") as f:
            json.dump(_cache_memoire, f, separators=(",", ":"))
    except IOError as e:
        print(f"[Memory] Erreur sauvegarde : {e}")


def obtenir_coup_memoire(board: chess.Board):
    memoire = charger_memoire()
    cle_fen = board.board_fen()
    entree = memoire.get(cle_fen)
    if entree is None:
        return None
    coup_uci = entree.get("best_move")
    if not coup_uci:
        return None
    try:
        coup = chess.Move.from_uci(coup_uci)
    except ValueError:
        del memoire[cle_fen]
        return None
    if coup in board.legal_moves:
        return coup
    else:
        del memoire[cle_fen]
        return None


def stocker_position(board: chess.Board, coup: chess.Move, profondeur: int, score: int) -> None:
    if profondeur < 1:
        return
    if board.is_checkmate():
        return
    if score == 0 and board.is_stalemate():
        return
    memoire = charger_memoire()
    cle_fen = board.board_fen()
    coup_uci = coup.uci()
    entree_existante = memoire.get(cle_fen)
    if entree_existante:
        if profondeur > entree_existante.get("depth", 0):
            memoire[cle_fen] = {
                "best_move": coup_uci,
                "depth": profondeur,
                "score": score,
                "visits": entree_existante.get("visits", 1) + 1
            }
        else:
            entree_existante["visits"] = entree_existante.get("visits", 1) + 1
    else:
        memoire[cle_fen] = {
            "best_move": coup_uci,
            "depth": profondeur,
            "score": score,
            "visits": 1
        }
    if len(memoire) > TAILLE_MAX_MEMOIRE:
        _nettoyer_memoire(memoire)
    sauvegarder_memoire()


def _nettoyer_memoire(memoire: dict) -> None:
    a_supprimer = [k for k, v in memoire.items() if v.get("visits", 0) < SEUIL_VISITES_MIN]
    for k in a_supprimer:
        del memoire[k]
    if len(memoire) > TAILLE_MAX_MEMOIRE:
        cles_triees = sorted(memoire.keys(), key=lambda k: (memoire[k].get("depth", 0), memoire[k].get("visits", 0)))
        for k in cles_triees[:len(memoire) - TAILLE_MAX_MEMOIRE]:
            del memoire[k]