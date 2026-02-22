import chess
from engine.engine import trouver_meilleur_coup, reinitialiser_historique_jeu


class JoueurIA:
    def __init__(self, board: chess.Board, profondeur: int = 4):
        self.board = board
        self.profondeur = profondeur
        reinitialiser_historique_jeu()

    def coup(self) -> str:
        coup = trouver_meilleur_coup(self.board, profondeur=self.profondeur)
        if coup is None:
            coups_legaux = list(self.board.legal_moves)
            if coups_legaux:
                coup = coups_legaux[0]
            else:
                raise RuntimeError("Aucun coup légal")
        return self.board.san(coup)