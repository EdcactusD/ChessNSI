import chess
from engine.engine import find_best_move, reset_game_history


class AIPlayer:
    def __init__(self, board: chess.Board, depth: int = 4):
        self.board = board
        self.depth = depth
        reset_game_history()

    def coup(self) -> str:
        move = find_best_move(self.board, depth=self.depth)
        if move is None:
            legal = list(self.board.legal_moves)
            if legal:
                move = legal[0]
            else:
                raise RuntimeError("Aucun coup légal")
        return self.board.san(move)