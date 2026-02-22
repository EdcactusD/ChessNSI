from chess import *
from tkinter import Tk
from canvas_tkinter import Chess_UI
from ai_player import AIPlayer

board = Board()
root = Tk()
root.title("Echec")

ai_blanc = AIPlayer(board, depth=4)
ai_noir  = AIPlayer(board, depth=4)

c = Chess_UI(root, board, ai_blanc, ai_noir)

root.mainloop()