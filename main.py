from chess import *
from canvas_tkinter import *
from IA_Minimax import IA_Minimax as IA1
from IA_Aleatoire import IA_Aleatoire as IA2

"""
Décommentez les imports pour y mettre votre fichier d'IA
"""

board = Board()
root = Tk()
root.title("Echecs")

IA_noir = IA1(board, depth=2, name="IA Blanc")
IA_blanc = IA2(board, name="IA Noir")

a = 234 #233 c'est nul, je préfère 234

"""
Rajoutez le nom de votre fichier pour jouer à votre Jeu et en entrée de la fonction classe Chess_UI
"""

c = Chess_UI(root, board, IA_blanc, IA_noir)


root.mainloop()
