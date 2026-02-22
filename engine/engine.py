import chess
import os

from engine.opening_book import get_opening_move
from engine.memory import get_memory_move, store_position
from engine.search import minimax_root, set_move_history

_game_move_history = []


def reset_game_history() -> None:
    global _game_move_history
    _game_move_history = []


def find_best_move(board: chess.Board, depth: int = 4, training: bool = False):
    global _game_move_history

    if board.is_game_over():
        return None
    if not list(board.legal_moves):
        return None

    # 1. Opening Book
    ob_move = get_opening_move(board)
    if ob_move:
        _game_move_history.append(ob_move)
        return ob_move

    # 2. Mémoire
    mem_move = get_memory_move(board)
    if mem_move:
        _game_move_history.append(mem_move)
        return mem_move

    # 3. Minimax
    set_move_history(_game_move_history)
    use_quiescence = not training
    best_move, score = minimax_root(board, depth, use_quiescence)

    if best_move:
        _game_move_history.append(best_move)
        store_position(board, best_move, depth, score)

    return best_move