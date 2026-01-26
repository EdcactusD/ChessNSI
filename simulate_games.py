import chess
from IA_Aleatoire import IA_Aleatoire
from IA_Minimax import IA_Minimax
from database import create_db, save_game

N_GAMES = 500  # nombre de parties à générer

def play_one_game(game_id):
    board = chess.Board()

    ia_white = IA_Minimax(board, depth=2, name="Minimax")
    ia_black = IA_Aleatoire(board, name="Aleatoire")

    moves_white = []
    moves_black = []

    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = ia_white.coup()
            board.push_uci(move)
            moves_white.append(move)
        else:
            move = ia_black.coup()
            board.push_uci(move)
            moves_black.append(move)

    result = board.result()

    save_game(
        ia_white.name,
        ia_black.name,
        result,
        moves_white,
        moves_black
    )

    print(f"Partie {game_id} terminée : {result}")


def main():
    create_db()

    for i in range(N_GAMES):
        play_one_game(i+1)

    print("Toutes les parties sont terminées.")


if __name__ == "__main__":
    main()
