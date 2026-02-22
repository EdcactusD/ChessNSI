import chess
from engine.evaluation import PIECE_VALUES


def score_move(board: chess.Board, move: chess.Move) -> int:
    score = 0
    if move.promotion:
        score += PIECE_VALUES.get(move.promotion, 0)
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score += 10 * PIECE_VALUES.get(victim.piece_type, 0) - PIECE_VALUES.get(attacker.piece_type, 0)
        else:
            score += 500  # en passant
    return score


def order_moves(board: chess.Board, moves) -> list:
    return sorted(moves, key=lambda m: score_move(board, m), reverse=True)