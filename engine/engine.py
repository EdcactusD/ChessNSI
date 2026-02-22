import chess
import os

from engine.opening_book import obtenir_coup_ouverture
from engine.memory import obtenir_coup_memoire, stocker_position
from engine.search import minimax_racine, fixer_historique_coups

_historique_coups_jeu = []


def reinitialiser_historique_jeu() -> None:
    global _historique_coups_jeu
    _historique_coups_jeu = []


def trouver_meilleur_coup(board: chess.Board, profondeur: int = 4, entrainement: bool = False):
    global _historique_coups_jeu

    if board.is_game_over():
        return None
    if not list(board.legal_moves):
        return None

    # 1. Livre des ouvertures
    coup_ouverture = obtenir_coup_ouverture(board)
    if coup_ouverture:
        _historique_coups_jeu.append(coup_ouverture)
        return coup_ouverture

    # 2. Mémoire
    coup_memoire = obtenir_coup_memoire(board)
    if coup_memoire:
        _historique_coups_jeu.append(coup_memoire)
        return coup_memoire

    # 3. Minimax
    fixer_historique_coups(_historique_coups_jeu)
    utiliser_quiesci = not entrainement
    meilleur_coup, score = minimax_racine(board, profondeur, utiliser_quiesci)

    if meilleur_coup:
        _historique_coups_jeu.append(meilleur_coup)
        stocker_position(board, meilleur_coup, profondeur, score)

    return meilleur_coup