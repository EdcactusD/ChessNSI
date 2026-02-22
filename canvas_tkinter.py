from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from chess import *
import threading

largeur_plateau = 1024
hauteur_plateau = 1024
DELAI_MS = 800


class InterfaceEchecs:
    def __init__(self, root: Tk, board: Board, J_Blanc, J_Noir):
        self.dict_images = {
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
        self.joueur_blanc = J_Blanc
        self.joueur_noir = J_Noir
        self.cadre_principal = ttk.Frame(self.root)
        self.cadre_principal.grid()

        for i in range(8):
            Label(self.cadre_principal, text=chr(ord('A') + i), bg='white').grid(row=0, column=i + 1, sticky=S)
            Label(self.cadre_principal, text=chr(ord('1') + i), bg='white').grid(row=i + 1, column=0, sticky=E)

        self.historique_blanc = []
        self.historique_noir = []
        self.var_historique_blanc = StringVar(value=self.historique_blanc)
        self.listbox_historique_blanc = Listbox(self.cadre_principal, listvariable=self.var_historique_blanc, bg="white", height=48)
        self.listbox_historique_blanc.grid(row=1, column=9, rowspan=8, sticky=N)

        self.var_historique_noir = StringVar(value=self.historique_noir)
        self.listbox_historique_noir = Listbox(self.cadre_principal, listvariable=self.var_historique_noir, bg="white", height=48)
        self.listbox_historique_noir.grid(row=1, column=10, rowspan=8, sticky=N)

        self.canvas = Canvas(self.cadre_principal, bg="black", width=largeur_plateau, height=hauteur_plateau)
        self.canvas.grid(row=1, column=1, columnspan=8, rowspan=8)
        self.img_fond = Image.open('img/plateau.png')
        self.photo_fond = ImageTk.PhotoImage(self.img_fond)
        self.canvas.create_image(largeur_plateau / 2, hauteur_plateau / 2, image=self.photo_fond)

        self.liste_pieces = []
        self._en_reflexion = False
        self.actualiser_plateau()

    def obtenir_x_depuis_col(self, col: int) -> float:
        if col < 0 or col > 7:
            raise ValueError(col)
        return largeur_plateau / 8 * col + largeur_plateau / 16

    def obtenir_y_depuis_ligne(self, ligne: int) -> float:
        if ligne < 0 or ligne > 7:
            raise ValueError(ligne)
        return hauteur_plateau / 8 * ligne + hauteur_plateau / 16

    def afficher_piece(self, piece, col: int, ligne: int) -> None:
        self.liste_pieces.append(
            self.canvas.create_image(self.obtenir_x_depuis_col(col), self.obtenir_y_depuis_ligne(ligne), image=self.dict_images[piece])
        )

    def actualiser_plateau(self):
        for piece in self.liste_pieces:
            self.canvas.delete(piece)
        self.liste_pieces.clear()

        ligne = col = 0
        for piece in self.board.board_fen():
            if '1' <= piece <= '8':
                col += ord(piece) - ord('0')
            elif piece == '/':
                col = 0
                ligne += 1
            else:
                self.afficher_piece(piece, col, ligne)
                col += 1
        self.root.after(DELAI_MS, self.jouer)

    def actualiser_historique_blanc(self, entree):
        self.historique_blanc.append(entree)
        self.var_historique_blanc.set(self.historique_blanc)

    def actualiser_historique_noir(self, entree):
        self.historique_noir.append(entree)
        self.var_historique_noir.set(self.historique_noir)

    def jouer(self):
        if self._en_reflexion:
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
                largeur_plateau // 2, hauteur_plateau // 2,
                text=f"Partie terminée : {res}",
                font=("Arial", 24, "bold"), fill="red"
            )
            return

        self._en_reflexion = True

        def calculer():
            try:
                if self.board.turn == WHITE:
                    san = self.joueur_blanc.coup()
                else:
                    san = self.joueur_noir.coup()
                self.root.after(0, lambda: self._appliquer_coup(san))
            except Exception as e:
                print(f"[UI] Erreur IA : {e}")
                self._en_reflexion = False

        threading.Thread(target=calculer, daemon=True).start()

    def _appliquer_coup(self, san: str):
        try:
            coup = self.board.parse_san(san)
            if self.board.turn == WHITE:
                self.actualiser_historique_blanc(f"{self.board.fullmove_number}. {san}")
            else:
                self.actualiser_historique_noir(f"{self.board.fullmove_number}... {san}")
            self.board.push(coup)
        except Exception as e:
            print(f"[UI] Coup invalide '{san}' : {e}")
        finally:
            self._en_reflexion = False
            self.actualiser_plateau()