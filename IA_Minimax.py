import chess
import math

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9
}


class IA_Minimax:
    def __init__(self, board, depth=2, name="IA Minimax"):
        self.board = board
        self.depth = depth
        self.name = name

    def coup(self):
        if self.board.turn == chess.WHITE:
            best_score = -math.inf
            best_move = None
            for move in self.board.legal_moves:
                self.board.push(move)
                score = self.minimax(self.depth-1, False, -math.inf, math.inf)
                self.board.pop()

                if score > best_score:
                    best_score = score
                    best_move = move
        else:  # NOIR
            best_score = math.inf
            best_move = None
            for move in self.board.legal_moves:
                self.board.push(move)
                score = self.minimax(self.depth-1, True, -math.inf, math.inf)
                self.board.pop()

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move.uci()


    def minimax(self, depth, maximizing, alpha, beta):

        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                return -10000
            else:
                return 10000

        if self.board.is_stalemate() or self.board.is_repetition(3):
            return 0

        if depth == 0:
            return self.evaluate()

        if maximizing:
            max_eval = -math.inf
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth-1, False, alpha, beta)
                self.board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = math.inf
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth-1, True, alpha, beta)
                self.board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self):
        score = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP,
                           chess.ROOK, chess.QUEEN]:
            score += len(self.board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            score -= len(self.board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
        return score
