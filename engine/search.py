import chess
from engine.evaluation import evaluer
from engine.move_ordering import ordonner_coups

INF = 10_000_000
PROF_MAX = 20
coups_tueurs = [[None, None] for _ in range(PROF_MAX)]

_historique_coups = []


def fixer_historique_coups(historique: list) -> None:
    global _historique_coups
    _historique_coups = [m.uci() for m in historique]


def _deja_joue_recemment(coup: chess.Move, regard_arriere: int = 8) -> bool:
    uci = coup.uci()
    # On regarde les coups du même joueur : indices -2, -4, -6, -8
    recent = _historique_coups[-regard_arriere:]
    coups_meme_joueur = recent[-2::-2]  # un coup sur deux en remontant
    return uci in coups_meme_joueur


def stocker_tueur(coup: chess.Move, profondeur: int) -> None:
    if profondeur < PROF_MAX:
        if coups_tueurs[profondeur][0] != coup:
            coups_tueurs[profondeur][1] = coups_tueurs[profondeur][0]
            coups_tueurs[profondeur][0] = coup


def quiesci(board: chess.Board, alpha: int, beta: int) -> int:
    position_neutre = evaluer(board)
    if position_neutre >= beta:
        return beta
    if alpha < position_neutre:
        alpha = position_neutre
    captures = ordonner_coups(board, [m for m in board.legal_moves if board.is_capture(m)])
    for coup in captures:
        board.push(coup)
        score = -quiesci(board, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def alpha_beta(board: chess.Board, profondeur: int, alpha: int, beta: int,
               ply: int = 0, utiliser_quiesci: bool = True) -> int:

    if board.is_repetition(2):
        return -500  # Répétition = mauvais score

    if profondeur == 0:
        return quiesci(board, alpha, beta) if utiliser_quiesci else evaluer(board)

    if board.is_game_over():
        return -INF + ply if board.is_checkmate() else 0

    coups = ordonner_coups(board, board.legal_moves)

    for coup in coups:
        board.push(coup)
        score = -alpha_beta(board, profondeur - 1, -beta, -alpha, ply + 1, utiliser_quiesci)
        board.pop()

        if score >= beta:
            if not board.is_capture(coup):
                stocker_tueur(coup, ply)
            return beta
        if score > alpha:
            alpha = score

    return alpha


def minimax_racine(board: chess.Board, profondeur: int,
                 utiliser_quiesci: bool = True) -> tuple:
    global coups_tueurs
    coups_tueurs = [[None, None] for _ in range(PROF_MAX)]

    coups_legaux = list(ordonner_coups(board, board.legal_moves))

    #Sépare STRICTEMENT coups nouveaux et coups répétitifs
    coups_frais = [m for m in coups_legaux if not _deja_joue_recemment(m)]
    coups_repetes = [m for m in coups_legaux if _deja_joue_recemment(m)]

    meilleur_coup = None
    meilleur_score = -INF

    # Explore UNIQUEMENT les coups non répétitifs
    for coup in coups_frais:
        board.push(coup)
        if board.is_repetition(2):
            board.pop()
            continue  # On skip même si c'est le seul — on cherche encore
        score = -alpha_beta(board, profondeur - 1, -INF, INF, 1, utiliser_quiesci)
        board.pop()

        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = coup

    # on autorise les répétitifs (évite le crash si position bloquée)
    if meilleur_coup is None:
        print("[Search] Aucun coup frais disponible, utilisation coup répétitif")
        for coup in coups_repetes:
            board.push(coup)
            score = -alpha_beta(board, profondeur - 1, -INF, INF, 1, utiliser_quiesci)
            board.pop()
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

    # Dernier recours absolu
    if meilleur_coup is None and coups_legaux:
        meilleur_coup = coups_legaux[0]

    return meilleur_coup, meilleur_score