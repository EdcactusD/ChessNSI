import chess
from engine.evaluation import VALEURS_PIECES


def noter_coup(board: chess.Board, coup: chess.Move) -> int:
    score = 0
    if coup.promotion:
        score += VALEURS_PIECES.get(coup.promotion, 0)
    if board.is_capture(coup):
        victime = board.piece_at(coup.to_square)
        attaquant = board.piece_at(coup.from_square)
        if victime and attaquant:
            score += 10 * VALEURS_PIECES.get(victime.piece_type, 0) - VALEURS_PIECES.get(attaquant.piece_type, 0)
        else:
            score += 500  # en passant
    return score


def ordonner_coups(board: chess.Board, coups) -> list:
    return sorted(coups, key=lambda m: noter_coup(board, m), reverse=True)