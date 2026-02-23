Moteur d'échecs en Python basé sur l'algorithme Minimax avec élagage Alpha-Bêta.
Il s'intègre à une interface graphique Tkinter et peut s'entraîner en mode
IA vs IA pour enrichir sa mémoire de positions.

Bibliothèques utilisées (déjà incluses avec Python) :
  tkinter, json, os, threading, random, time, argparse


LANCER LE JEU

  python main.py

L'interface s'ouvre. Les deux IAs jouent automatiquement l'une contre l'autre.
Pour changer la profondeur de réflexion, modifie dans main.py :

ia_blanc = JoueurIA(board, profondeur=4)
ia_noir  = JoueurIA(board, profondeur=4)

  depth=2 : très rapide ,débutant
  depth=3 :  rapide, intermédiaire
  depth=4 :  équilibré, correct
  depth=5 :  lent, fort
  depth=6 :  très lent , avancé


ENTRAÎNEMENT (train.py)

Lance des parties IA vs IA sans interface pour remplir memory.json.
Plus memory.json est grand, plus l'IA est rapide sur les positions connues.

  python train.py --games 500 --depth 2     rapide, recommandé pour commencer
  python train.py --games 2000 --depth 3    bon équilibre qualité/vitesse
  python train.py --games 5000 --depth 4    entraînement plus long

Notes :
  - La sauvegarde se fait automatiquement toutes les 10 parties
  - Le training ignore la règle de répétition pour forcer des parties complètes
  - Chaque partie dure maximum 150 coups
  - Ne pas mélanger train.py et main.py en même temps
