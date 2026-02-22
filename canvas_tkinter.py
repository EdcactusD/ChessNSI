from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from chess import *
import threading

board_width = 1024
board_height = 1024
DELAY_MS = 800


class Chess_UI:
    def __init__(self, root: Tk, board: Board, J_Blanc, J_Noir):
        self.img_dict = {
            'p': ImageTk.PhotoImage(Image.open('img/pion_noir.png').resize((100, 100))),
            'b': ImageTk.PhotoImage(Image.open('img/fou_noir.png').resize((100, 100))),
            'q': ImageTk.PhotoImage(Image.open('img/reine_noire.png').resize((100, 100))),
            'k': ImageTk.PhotoImage(Image.open('img/roi_noir.png').resize((100, 100))),
            'n': ImageTk.PhotoImage(Image.open('img/cavalier_noir.png').resize((100, 100))),
            'r': ImageTk.PhotoImage(Image.open('img/tour_noire.png').resize((100, 100))),
            'P': ImageTk.PhotoImage(Image.open('img/pion_blanc.png').resize((100, 100))),
            'B': ImageTk.PhotoImage(Image.open('img/fou_blanc.png').resize((100, 100))),
            'Q': ImageTk.PhotoImage(Image.open('img/reine_blanche.png').resize((100, 100))),
            'K': ImageTk.PhotoImage(Image.open('img/roi_blanc.png').resize((100, 100))),
            'N': ImageTk.PhotoImage(Image.open('img/cavalier_blanc.png').resize((100, 100))),
            'R': ImageTk.PhotoImage(Image.open('img/tour_blanche.png').resize((100, 100))),
        }
        self.root = root
        self.board = board
        self.Joueur_Blanc = J_Blanc
        self.Joueur_Noir = J_Noir
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid()

        for i in range(8):
            Label(self.mainframe, text=chr(ord('A') + i), bg='white').grid(row=0, column=i + 1, sticky=S)
            Label(self.mainframe, text=chr(ord('1') + i), bg='white').grid(row=i + 1, column=0, sticky=E)

        self.history_white = []
        self.history_black = []
        self.history_white_var = StringVar(value=self.history_white)
        self.history_white_listbox = Listbox(self.mainframe, listvariable=self.history_white_var, bg="white", height=48)
        self.history_white_listbox.grid(row=1, column=9, rowspan=8, sticky=N)

        self.history_black_var = StringVar(value=self.history_black)
        self.history_black_listbox = Listbox(self.mainframe, listvariable=self.history_black_var, bg="white", height=48)
        self.history_black_listbox.grid(row=1, column=10, rowspan=8, sticky=N)

        self.canvas = Canvas(self.mainframe, bg="black", width=board_width, height=board_height)
        self.canvas.grid(row=1, column=1, columnspan=8, rowspan=8)
        self.bg_img = Image.open('img/plateau.png')
        self.bg_photo = ImageTk.PhotoImage(self.bg_img)
        self.canvas.create_image(board_width / 2, board_height / 2, image=self.bg_photo)

        self.pieces_list = []
        self._thinking = False
        self.update_board()

    def get_x_from_col(self, col: int) -> float:
        if col < 0 or col > 7:
            raise ValueError(col)
        return board_width / 8 * col + board_width / 16

    def get_y_from_row(self, row: int) -> float:
        if row < 0 or row > 7:
            raise ValueError(row)
        return board_height / 8 * row + board_height / 16

    def display_piece(self, piece, col: int, row: int) -> None:
        self.pieces_list.append(
            self.canvas.create_image(self.get_x_from_col(col), self.get_y_from_row(row), image=self.img_dict[piece])
        )

    def update_board(self):
        for piece in self.pieces_list:
            self.canvas.delete(piece)
        self.pieces_list.clear()

        row = col = 0
        for piece in self.board.board_fen():
            if '1' <= piece <= '8':
                col += ord(piece) - ord('0')
            elif piece == '/':
                col = 0
                row += 1
            else:
                self.display_piece(piece, col, row)
                col += 1

        # ✅ root.after au lieu de sleep() → Tkinter reste réactif
        self.root.after(DELAY_MS, self.jouer)

    def update_history_white(self, entry):
        self.history_white.append(entry)
        self.history_white_var.set(self.history_white)

    def update_history_black(self, entry):
        self.history_black.append(entry)
        self.history_black_var.set(self.history_black)

    def jouer(self):
        if self._thinking:
            return

        if self.board.is_game_over():
            res = self.board.result()
            if res == "1-0":
                res = "Les blancs ont gagné !"
            elif res == "0-1":
                res = "Les noirs ont gagné !"
            else:
                res = "Égalité !"
            self.canvas.create_text(
                board_width // 2, board_height // 2,
                text=f"Partie terminée : {res}",
                font=("Arial", 24, "bold"), fill="red"
            )
            return

        self._thinking = True

        def calculate():
            try:
                if self.board.turn == WHITE:
                    san = self.Joueur_Blanc.coup()
                else:
                    san = self.Joueur_Noir.coup()
                self.root.after(0, lambda: self._apply_move(san))
            except Exception as e:
                print(f"[UI] Erreur IA : {e}")
                self._thinking = False

        threading.Thread(target=calculate, daemon=True).start()

    def _apply_move(self, san: str):
        try:
            move = self.board.parse_san(san)
            if self.board.turn == WHITE:
                self.update_history_white(f"{self.board.fullmove_number}. {san}")
            else:
                self.update_history_black(f"{self.board.fullmove_number}... {san}")
            self.board.push(move)
        except Exception as e:
            print(f"[UI] Coup invalide '{san}' : {e}")
        finally:
            self._thinking = False
            self.update_board()