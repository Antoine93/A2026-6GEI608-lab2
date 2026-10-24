# fichier qui contient les fonctions communes, genre de convention

import random

from .parser import BLANK

# indices (0 à 80) des cases de chaque ligne, colonne et bloc 3x3
ROWS = [[9 * r + c for c in range(9)] for r in range(9)]
COLS = [[9 * r + c for r in range(9)] for c in range(9)]
BOXES = [[9 * (3 * br + r) + 3 * bc + c for r in range(3) for c in range(3)] for br in range(3) for bc in range(3)]

#  0   1   2 |  3   4   5 |  6   7   8 
#  9  10  11 | 12  13  14 | 15  16  17 
# 18  19  20 | 21  22  23 | 24  25  26 
#--------------------------------------
# 27  28  29 | 30  31  32 | 33  34  35 
# 36  37  38 | 39  40  41 | 42  43  44 
# 45  46  47 | 48  49  50 | 51  52  53 
#--------------------------------------
# 54  55  56 | 57  58  59 | 60  61  62 
# 63  64  65 | 66  67  68 | 69  70  71
# 72  73  74 | 75  76  77 | 78  79  80 


# retourne pour chaque case si elle a été donnée par l'énoncé?
def get_fixed(puzzle: list[str]) -> list[bool]:
    return [val != BLANK for val in puzzle]

#puzzle :  ['.', '.', '.', '.', '5', '.', '9', '.', '.', ...]
#fixed  :  [False, False, False, False, True, False, True, False, False, ...]


# remplit chaque ligne avec les chiffres manquants (placés au hasard dans les cases vides)
# les cases fixes ne sont pas modifiées, donc chaque ligne contient les chiffres 1 à 9 une seule fois
# ce board sera un point de départ (hill climbing) et population initiale (génétique)
def fill_rows(puzzle: list[str]) -> list[str]:
    board = puzzle[:]
    for row in ROWS:
        missing = [d for d in "123456789" if d not in [board[i] for i in row]]
        random.shuffle(missing)
        for i in row:
            if board[i] == BLANK:
                board[i] = missing.pop()
    return board


# nombre de paires de cases en conflit (même chiffre dans une même colonne ou un même bloc)
# vaut 0 seulement si le sudoku est résolu (les lignes sont déjà valides)
# compteur incrémental : la n-ième occurrence d'un chiffre forme n-1 nouvelles paires avec les précédentes
# (même résultat que count * (count - 1) // 2 par chiffre, environ 3 fois plus rapide que Counter)
def conflicts(board: list[str]) -> int:
    total = 0
    for unit in COLS + BOXES:
        seen = {}                       # chiffre -> nombre de fois vu jusqu'ici dans l'unité
        for i in unit:
            n = seen.get(board[i], 0)
            total += n
            seen[board[i]] = n + 1
    return total


# vérifie que les chiffres donnés du puzzle n'ont pas de doublon dans une ligne, une colonne ou un bloc
# pas un détecteur de solvabilité, juste un détecteur de configuration impossible
def is_valid_config(puzzle: list[str]) -> bool:
    for unit in ROWS + COLS + BOXES:
        digits = [puzzle[i] for i in unit if puzzle[i] != BLANK]
        if len(digits) != len(set(digits)):
            return False
    return True


# affiche une grille de 81 cases en 9 lignes, présentation finale
def print_board(board: list[str]) -> None:
    for r, row in enumerate(ROWS):
        if r % 3 == 0 and r != 0:
            print("------+-------+------")
        cells = [board[i] for i in row]
        print(" ".join(cells[0:3]), "|", " ".join(cells[3:6]), "|", " ".join(cells[6:9]))
