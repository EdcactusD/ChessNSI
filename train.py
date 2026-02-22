import argparse
import chess
import time
from engine.engine import find_best_move
from engine.memory import save_memory
from engine.engine import find_best_move, reset_game_history

def play_game(depth: int) -> str:
    board = chess.Board()
    reset_game_history()  # Nouveau jeu = historique vide
    move_count = 0

    while not board.is_game_over() and move_count < 150:
        move = find_best_move(board, depth=depth, training=True)
        if move is None:
            break
        board.push(move)
        move_count += 1

    return board.result()


def train(num_games: int, depth: int) -> None:
    print(f"[Train] {num_games} parties | profondeur {depth} | mode rapide")
    print(f"[Train] Estimation : ~{num_games * (2 ** depth) // 200}s\n")

    results = {}
    total_moves = 0
    start = time.time()

    for i in range(num_games):
        t0 = time.time()
        result = play_game(depth)
        t1 = time.time()

        results[result] = results.get(result, 0) + 1
        elapsed = t1 - t0
        total = time.time() - start
        remaining = (total / (i + 1)) * (num_games - i - 1)

        print(f"  Partie {i+1:>4}/{num_games} | {result} | "
              f"{elapsed:.1f}s | restant ~{remaining:.0f}s")

        # Sauvegarde toutes les 10 parties
        if (i + 1) % 10 == 0:
            save_memory()
            print(f"  [Save] memory.json sauvegardé ({i+1} parties)\n")

    save_memory()

    total_time = time.time() - start
    print(f"\n{'='*50}")
    print(f"[Train] Terminé en {total_time:.1f}s")
    print(f"  Blancs : {results.get('1-0', 0)}")
    print(f"  Noirs  : {results.get('0-1', 0)}")
    print(f"  Nulles : {results.get('1/2-1/2', 0)}")
    print(f"  Autres : {results.get('*', 0)}")
    print(f"[Train] memory.json sauvegardé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=200)
    parser.add_argument("--depth", type=int, default=2)  #défaut à 2 pour training
    args = parser.parse_args()
    train(args.games, args.depth)