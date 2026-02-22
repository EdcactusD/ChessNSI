from chess import *
from tkinter import Tk
from canvas_tkinter import InterfaceEchecs
from ai_player import JoueurIA

board = Board()
root = Tk()
root.title("Echec")

ia_blanc = JoueurIA(board, profondeur=4)
ia_noir  = JoueurIA(board, profondeur=4)

ui = InterfaceEchecs(root, board, ia_blanc, ia_noir)

root.mainloop()