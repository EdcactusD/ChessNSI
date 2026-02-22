import argparse
import chess
import time
from engine.engine import trouver_meilleur_coup
from engine.memory import sauvegarder_memoire
from engine.engine import trouver_meilleur_coup, reinitialiser_historique_jeu

def jouer_partie(profondeur: int) -> str:
    board = chess.Board()
    reinitialiser_historique_jeu()  # Nouveau jeu = historique vide
    nombre_coups = 0

    while not board.is_game_over() and nombre_coups < 150:
        coup = trouver_meilleur_coup(board, profondeur=profondeur, entrainement=True)
        if coup is None:
            break
        board.push(coup)
        nombre_coups += 1

    return board.result()


def entrainer(nombre_parties: int, profondeur: int) -> None:
    print(f"[Train] {nombre_parties} parties | profondeur {profondeur} | mode rapide")
    print(f"[Train] Estimation : ~{nombre_parties * (2 ** profondeur) // 200}s\n")

    resultats = {}
    total_coups = 0
    start = time.time()

    for i in range(nombre_parties):
        t0 = time.time()
        resultat = jouer_partie(profondeur)
        t1 = time.time()

        resultats[resultat] = resultats.get(resultat, 0) + 1
        duree = t1 - t0
        total = time.time() - start
        restant = (total / (i + 1)) * (nombre_parties - i - 1)

        print(f"  Partie {i+1:>4}/{nombre_parties} | {resultat} | "
              f"{duree:.1f}s | restant ~{restant:.0f}s")

        # Sauvegarde toutes les 10 parties
        if (i + 1) % 10 == 0:
            sauvegarder_memoire()
            print(f"  [Save] memory.json sauvegardé ({i+1} parties)\n")

    sauvegarder_memoire()

    total_time = time.time() - start
    print(f"\n{'='*50}")
    print(f"[Train] Terminé en {total_time:.1f}s")
    print(f"  Blancs : {resultats.get('1-0', 0)}")
    print(f"  Noirs  : {resultats.get('0-1', 0)}")
    print(f"  Nulles : {resultats.get('1/2-1/2', 0)}")
    print(f"  Autres : {resultats.get('*', 0)}")
    print(f"[Train] memory.json sauvegardé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=200)
    parser.add_argument("--depth", type=int, default=2)  #défaut à 2 pour training
    args = parser.parse_args()
    entrainer(args.games, args.depth)