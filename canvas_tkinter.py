from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from chess import *
import threading

TAILLE_CASE = 90
TAILLE_PLATEAU = TAILLE_CASE * 8
MARGE = 40
PANNEAU_LATERAL = 260
DELAI_MS = 800

COULEUR_CASE_CLAIRE = "#F0D9B5"
COULEUR_CASE_FONCEE = "#B58863"
COULEUR_FOND = "#1A1A2E"
COULEUR_PANNEAU = "#16213E"
COULEUR_ACCENT = "#E94560"
COULEUR_TEXTE = "#EAEAEA"
COULEUR_TEXTE_SEC = "#A8A8B3"
COULEUR_COORD_CLAIR = "#8B6914"
COULEUR_COORD_FONCE = "#6B4A0E"
COULEUR_LAST_MOVE_CLAIR = "#CDD16E"
COULEUR_LAST_MOVE_FONCE = "#AAB340"


def creer_image_piece_stylisee(image_pil, taille):
    img = image_pil.resize((taille - 8, taille - 8), Image.LANCZOS).convert("RGBA")
    resultat = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
    ombre = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
    ombre_draw = ImageDraw.Draw(ombre)
    ombre_draw.ellipse([6, 6, taille - 2, taille - 2], fill=(0, 0, 0, 60))
    ombre = ombre.filter(ImageFilter.GaussianBlur(3))
    resultat.paste(ombre, (0, 0), ombre)
    resultat.paste(img, (4, 4), img)
    return resultat


class InterfaceEchecs:
    def __init__(self, root: Tk, board: Board, J_Blanc, J_Noir):
        self.root = root
        self.board = board
        self.joueur_blanc = J_Blanc
        self.joueur_noir = J_Noir
        self._en_reflexion = False
        self._dernier_coup = None

        self.root.configure(bg=COULEUR_FOND)
        self.root.resizable(False, False)

        self._charger_images()
        self._construire_ui()
        self.actualiser_plateau()

    def _charger_images(self):
        fichiers = {
            'p': 'img/pion_noir.png', 'b': 'img/fou_noir.png',
            'q': 'img/reine_noire.png', 'k': 'img/roi_noir.png',
            'n': 'img/cavalier_noir.png', 'r': 'img/tour_noire.png',
            'P': 'img/pion_blanc.png', 'B': 'img/fou_blanc.png',
            'Q': 'img/reine_blanche.png', 'K': 'img/roi_blanc.png',
            'N': 'img/cavalier_blanc.png', 'R': 'img/tour_blanche.png',
        }
        self.dict_images = {}
        for code, chemin in fichiers.items():
            img_pil = Image.open(chemin)
            img_stylisee = creer_image_piece_stylisee(img_pil, TAILLE_CASE)
            self.dict_images[code] = ImageTk.PhotoImage(img_stylisee)

    def _construire_ui(self):
        self.frame_principal = Frame(self.root, bg=COULEUR_FOND)
        self.frame_principal.pack(padx=20, pady=20)

        self.frame_gauche = Frame(self.frame_principal, bg=COULEUR_FOND)
        self.frame_gauche.pack(side=LEFT)

        canvas_taille = MARGE + TAILLE_PLATEAU + MARGE
        self.canvas = Canvas(
            self.frame_gauche,
            width=canvas_taille, height=canvas_taille,
            bg=COULEUR_FOND, highlightthickness=0, bd=0
        )
        self.canvas.pack()
        self.liste_pieces = []

        self.frame_droit = Frame(self.frame_principal, bg=COULEUR_PANNEAU,
                                  width=PANNEAU_LATERAL, bd=0)
        self.frame_droit.pack(side=LEFT, padx=(20, 0), fill=Y)
        self.frame_droit.pack_propagate(False)

        self._creer_panneau_lateral()

    def _dessiner_fond_plateau(self):
        self.canvas.delete("fond")

        for ligne in range(8):
            for col in range(8):
                x1 = MARGE + col * TAILLE_CASE
                y1 = MARGE + ligne * TAILLE_CASE
                x2 = x1 + TAILLE_CASE
                y2 = y1 + TAILLE_CASE
                clair = (ligne + col) % 2 == 0
                couleur = COULEUR_CASE_CLAIRE if clair else COULEUR_CASE_FONCEE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="", tags="fond")

        f_coord = tkfont.Font(family="Georgia", size=10, weight="bold")
        for i in range(8):
            lettre = chr(ord('a') + i)
            x = MARGE + i * TAILLE_CASE + TAILLE_CASE // 2
            coul = COULEUR_COORD_CLAIR if i % 2 == 0 else COULEUR_COORD_FONCE
            self.canvas.create_text(x, MARGE + TAILLE_PLATEAU + 14, text=lettre,
                                    fill=coul, font=f_coord, tags="fond")
            self.canvas.create_text(x, MARGE - 14, text=lettre,
                                    fill=coul, font=f_coord, tags="fond")

        for i in range(8):
            chiffre = str(8 - i)
            y = MARGE + i * TAILLE_CASE + TAILLE_CASE // 2
            coul = COULEUR_COORD_CLAIR if i % 2 == 0 else COULEUR_COORD_FONCE
            self.canvas.create_text(MARGE - 14, y, text=chiffre,
                                    fill=coul, font=f_coord, tags="fond")
            self.canvas.create_text(MARGE + TAILLE_PLATEAU + 14, y, text=chiffre,
                                    fill=coul, font=f_coord, tags="fond")

        self.canvas.create_rectangle(
            MARGE - 2, MARGE - 2,
            MARGE + TAILLE_PLATEAU + 2, MARGE + TAILLE_PLATEAU + 2,
            outline="#5D4037", width=2, tags="fond"
        )

    def _surligner_dernier_coup(self):
        self.canvas.delete("highlight")
        if self._dernier_coup is None:
            return
        for sq in [self._dernier_coup.from_square, self._dernier_coup.to_square]:
            col = sq % 8
            ligne = 7 - sq // 8
            x1 = MARGE + col * TAILLE_CASE
            y1 = MARGE + ligne * TAILLE_CASE
            clair = (ligne + col) % 2 == 0
            couleur = COULEUR_LAST_MOVE_CLAIR if clair else COULEUR_LAST_MOVE_FONCE
            self.canvas.create_rectangle(x1, y1, x1 + TAILLE_CASE, y1 + TAILLE_CASE,
                                          fill=couleur, outline="", tags="highlight")

    def _creer_panneau_lateral(self):
        padding = 16
        f_titre = tkfont.Font(family="Georgia", size=14, weight="bold")
        f_sous_titre = tkfont.Font(family="Georgia", size=11, weight="bold")
        f_corps = tkfont.Font(family="Consolas", size=10)
        f_label = tkfont.Font(family="Arial", size=9, weight="bold")

        Label(self.frame_droit, text="♟  CHESS ENGINE",
              font=f_titre, bg=COULEUR_PANNEAU, fg=COULEUR_ACCENT,
              pady=16).pack(fill=X, padx=padding)

        Frame(self.frame_droit, height=1, bg=COULEUR_ACCENT).pack(fill=X, padx=padding, pady=(0, 12))

        frame_status = Frame(self.frame_droit, bg=COULEUR_PANNEAU)
        frame_status.pack(fill=X, padx=padding, pady=(0, 12))

        self.label_tour = Label(frame_status, text="● Blancs jouent",
                                font=f_sous_titre, bg=COULEUR_PANNEAU,
                                fg="#FFFFFF", anchor=W)
        self.label_tour.pack(fill=X)

        self.label_coup_num = Label(frame_status, text="Coup 1",
                                    font=f_corps, bg=COULEUR_PANNEAU,
                                    fg=COULEUR_TEXTE_SEC, anchor=W)
        self.label_coup_num.pack(fill=X)

        self.label_etat = Label(frame_status, text="",
                                font=f_corps, bg=COULEUR_PANNEAU,
                                fg=COULEUR_ACCENT, anchor=W)
        self.label_etat.pack(fill=X)

        Frame(self.frame_droit, height=1, bg="#2A2A4A").pack(fill=X, padx=padding, pady=8)

        Label(self.frame_droit, text="HISTORIQUE", font=f_label,
              bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SEC,
              anchor=W).pack(fill=X, padx=padding)

        frame_entetes = Frame(self.frame_droit, bg=COULEUR_PANNEAU)
        frame_entetes.pack(fill=X, padx=padding, pady=(4, 0))
        Label(frame_entetes, text="Blancs", width=10,
              font=f_corps, bg="#0F3460", fg="#FFFFFF", pady=4).pack(side=LEFT, padx=(0, 2))
        Label(frame_entetes, text="Noirs", width=10,
              font=f_corps, bg="#0F3460", fg="#FFFFFF", pady=4).pack(side=LEFT)

        frame_listes = Frame(self.frame_droit, bg=COULEUR_PANNEAU)
        frame_listes.pack(fill=BOTH, expand=True, padx=padding, pady=(2, 12))

        self.historique_blanc = []
        self.historique_noir = []
        self.var_historique_blanc = StringVar(value=self.historique_blanc)
        self.var_historique_noir = StringVar(value=self.historique_noir)

        self.listbox_historique_blanc = Listbox(
            frame_listes, listvariable=self.var_historique_blanc,
            bg="#0A0A1A", fg="#E8D5B7", selectbackground=COULEUR_ACCENT,
            font=f_corps, width=10, height=20,
            bd=0, highlightthickness=0, relief=FLAT
        )
        self.listbox_historique_blanc.pack(side=LEFT, fill=BOTH, expand=True)

        self.listbox_historique_noir = Listbox(
            frame_listes, listvariable=self.var_historique_noir,
            bg="#0A0A1A", fg="#C8C8C8", selectbackground=COULEUR_ACCENT,
            font=f_corps, width=10, height=20,
            bd=0, highlightthickness=0, relief=FLAT
        )
        self.listbox_historique_noir.pack(side=LEFT, fill=BOTH, expand=True)

        Frame(self.frame_droit, height=1, bg="#2A2A4A").pack(fill=X, padx=padding, pady=8)

        self.label_ia = Label(self.frame_droit, text="⚙  IA en réflexion...",
                              font=f_corps, bg=COULEUR_PANNEAU, fg=COULEUR_TEXTE_SEC)

    def _maj_status(self):
        couleur = "Blancs" if self.board.turn == WHITE else "Noirs"
        dot_color = "#FFFFFF" if self.board.turn == WHITE else "#888888"
        self.label_tour.config(text=f"● {couleur} jouent", fg=dot_color)
        self.label_coup_num.config(text=f"Coup {self.board.fullmove_number}")
        self.label_etat.config(text="⚠ Échec !" if self.board.is_check() else "")

    def obtenir_x_depuis_col(self, col: int) -> float:
        return MARGE + TAILLE_CASE * col + TAILLE_CASE // 2

    def obtenir_y_depuis_ligne(self, ligne: int) -> float:
        return MARGE + TAILLE_CASE * ligne + TAILLE_CASE // 2

    def afficher_piece(self, piece, col: int, ligne: int) -> None:
        self.liste_pieces.append(
            self.canvas.create_image(
                self.obtenir_x_depuis_col(col),
                self.obtenir_y_depuis_ligne(ligne),
                image=self.dict_images[piece]
            )
        )

    def actualiser_plateau(self):
        for piece in self.liste_pieces:
            self.canvas.delete(piece)
        self.liste_pieces.clear()

        self._dessiner_fond_plateau()
        self._surligner_dernier_coup()

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

        self._maj_status()
        self.root.after(DELAI_MS, self.jouer)

    def actualiser_historique_blanc(self, entree):
        self.historique_blanc.append(entree)
        self.var_historique_blanc.set(self.historique_blanc)
        self.listbox_historique_blanc.see(END)

    def actualiser_historique_noir(self, entree):
        self.historique_noir.append(entree)
        self.var_historique_noir.set(self.historique_noir)
        self.listbox_historique_noir.see(END)

    def jouer(self):
        if self._en_reflexion:
            return

        if self.board.is_game_over():
            res = self.board.result()
            if res == "1-0":
                res_txt, coul_res = "Les Blancs ont gagné !", "#FFD700"
            elif res == "0-1":
                res_txt, coul_res = "Les Noirs ont gagné !", "#C0C0C0"
            else:
                res_txt, coul_res = "Partie nulle !", "#88CCFF"

            cx = MARGE + TAILLE_PLATEAU // 2
            cy = MARGE + TAILLE_PLATEAU // 2
            self.canvas.create_rectangle(cx - 218, cy - 55, cx + 218, cy + 55,
                                          fill="#000000", stipple="gray50", outline="")
            self.canvas.create_rectangle(cx - 216, cy - 53, cx + 216, cy + 53,
                                          fill="#0F3460", outline=coul_res, width=2)
            self.canvas.create_text(cx, cy - 16, text="PARTIE TERMINÉE",
                                    font=tkfont.Font(family="Arial", size=13, weight="bold"),
                                    fill=COULEUR_TEXTE_SEC)
            self.canvas.create_text(cx, cy + 18, text=res_txt,
                                    font=tkfont.Font(family="Georgia", size=19, weight="bold"),
                                    fill=coul_res)
            self.label_tour.config(text="Partie terminée", fg=coul_res)
            self.label_etat.config(text=res_txt)
            return

        self._en_reflexion = True
        self.label_ia.pack(pady=(0, 12))

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
                self.root.after(0, self.label_ia.pack_forget)

        threading.Thread(target=calculer, daemon=True).start()

    def _appliquer_coup(self, san: str):
        try:
            coup = self.board.parse_san(san)
            self._dernier_coup = coup
            if self.board.turn == WHITE:
                self.actualiser_historique_blanc(f"{self.board.fullmove_number}.  {san}")
            else:
                self.actualiser_historique_noir(f"{self.board.fullmove_number}… {san}")
            self.board.push(coup)
        except Exception as e:
            print(f"[UI] Coup invalide '{san}' : {e}")
        finally:
            self._en_reflexion = False
            self.label_ia.pack_forget()
            self.actualiser_plateau()
