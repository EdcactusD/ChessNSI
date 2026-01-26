import random
from chess import Board

class IA_Aleatoire:
    def __init__(self,board: Board, name: str = "IA aléatoire"):
        self.board = board
        self.name = name

    def coup(self) -> str:
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        move = random.choice(legal_moves)
        return move.uci()
    
    def __str__(self):
        return self.name