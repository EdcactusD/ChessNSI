import chess
from engine.evaluation import evaluate
from engine.move_ordering import order_moves

INF = 10_000_000
MAX_PLY = 20
killer_moves = [[None, None] for _ in range(MAX_PLY)]

_move_history = []


def set_move_history(history: list) -> None:
    global _move_history
    _move_history = [m.uci() for m in history]


def _already_played_recently(move: chess.Move, lookback: int = 8) -> bool:
    uci = move.uci()
    # On regarde les coups du même joueur : indices -2, -4, -6, -8
    recent = _move_history[-lookback:]
    same_player_moves = recent[-2::-2]  # un coup sur deux en remontant
    return uci in same_player_moves


def store_killer(move: chess.Move, ply: int) -> None:
    if ply < MAX_PLY:
        if killer_moves[ply][0] != move:
            killer_moves[ply][1] = killer_moves[ply][0]
            killer_moves[ply][0] = move


def quiescence(board: chess.Board, alpha: int, beta: int) -> int:
    stand_pat = evaluate(board)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
    captures = order_moves(board, [m for m in board.legal_moves if board.is_capture(m)])
    for move in captures:
        board.push(move)
        score = -quiescence(board, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def alpha_beta(board: chess.Board, depth: int, alpha: int, beta: int,
               ply: int = 0, use_quiescence: bool = True) -> int:

    if board.is_repetition(2):
        return -500  # Répétition = mauvais score

    if depth == 0:
        return quiescence(board, alpha, beta) if use_quiescence else evaluate(board)

    if board.is_game_over():
        return -INF + ply if board.is_checkmate() else 0

    moves = order_moves(board, board.legal_moves)

    for move in moves:
        board.push(move)
        score = -alpha_beta(board, depth - 1, -beta, -alpha, ply + 1, use_quiescence)
        board.pop()

        if score >= beta:
            if not board.is_capture(move):
                store_killer(move, ply)
            return beta
        if score > alpha:
            alpha = score

    return alpha


def minimax_root(board: chess.Board, depth: int,
                 use_quiescence: bool = True) -> tuple:
    global killer_moves
    killer_moves = [[None, None] for _ in range(MAX_PLY)]

    legal_moves = list(order_moves(board, board.legal_moves))

    #Sépare STRICTEMENT coups nouveaux et coups répétitifs
    fresh_moves = [m for m in legal_moves if not _already_played_recently(m)]
    stale_moves = [m for m in legal_moves if _already_played_recently(m)]

    best_move = None
    best_score = -INF

    # Explore UNIQUEMENT les coups non répétitifs
    for move in fresh_moves:
        board.push(move)
        if board.is_repetition(2):
            board.pop()
            continue  # On skip même si c'est le seul — on cherche encore
        score = -alpha_beta(board, depth - 1, -INF, INF, 1, use_quiescence)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    # on autorise les répétitifs (évite le crash si position bloquée)
    if best_move is None:
        print("[Search] Aucun coup frais disponible, utilisation coup répétitif")
        for move in stale_moves:
            board.push(move)
            score = -alpha_beta(board, depth - 1, -INF, INF, 1, use_quiescence)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move

    # Dernier recours absolu
    if best_move is None and legal_moves:
        best_move = legal_moves[0]

    return best_move, best_score