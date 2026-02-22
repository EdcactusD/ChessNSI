import json
import os
import chess

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
MAX_MEMORY_SIZE = 5_000_000
MIN_VISITS_THRESHOLD = 2

_memory_cache = None


def load_memory() -> dict:
    global _memory_cache
    if _memory_cache is not None:
        return _memory_cache
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                _memory_cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            _memory_cache = {}
    else:
        _memory_cache = {}
    return _memory_cache


def save_memory() -> None:
    global _memory_cache
    if _memory_cache is None:
        return
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(_memory_cache, f, separators=(",", ":"))
    except IOError as e:
        print(f"[Memory] Erreur sauvegarde : {e}")


def get_memory_move(board: chess.Board):
    memory = load_memory()
    fen_key = board.board_fen()
    entry = memory.get(fen_key)
    if entry is None:
        return None
    move_uci = entry.get("best_move")
    if not move_uci:
        return None
    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        del memory[fen_key]
        return None
    if move in board.legal_moves:
        return move
    else:
        del memory[fen_key]
        return None


def store_position(board: chess.Board, move: chess.Move, depth: int, score: int) -> None:
    if depth < 1:
        return
    if board.is_checkmate():
        return
    if score == 0 and board.is_stalemate():
        return
    memory = load_memory()
    fen_key = board.board_fen()
    move_uci = move.uci()
    existing = memory.get(fen_key)
    if existing:
        if depth > existing.get("depth", 0):
            memory[fen_key] = {
                "best_move": move_uci,
                "depth": depth,
                "score": score,
                "visits": existing.get("visits", 1) + 1
            }
        else:
            existing["visits"] = existing.get("visits", 1) + 1
    else:
        memory[fen_key] = {
            "best_move": move_uci,
            "depth": depth,
            "score": score,
            "visits": 1
        }
    if len(memory) > MAX_MEMORY_SIZE:
        _cleanup_memory(memory)
    save_memory()


def _cleanup_memory(memory: dict) -> None:
    to_delete = [k for k, v in memory.items() if v.get("visits", 0) < MIN_VISITS_THRESHOLD]
    for k in to_delete:
        del memory[k]
    if len(memory) > MAX_MEMORY_SIZE:
        sorted_keys = sorted(memory.keys(), key=lambda k: (memory[k].get("depth", 0), memory[k].get("visits", 0)))
        for k in sorted_keys[:len(memory) - MAX_MEMORY_SIZE]:
            del memory[k]