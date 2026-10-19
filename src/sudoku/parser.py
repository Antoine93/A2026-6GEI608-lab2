# fichier pour parser un fichier sudoku et vérifier sa VALIDITÉ (!= RÉSOLVABILITÉ)

from typing import Literal

# symboles acceptés comme une case vide
BLANK_SYMBOLS = {".", "0", "*", "_", "%"}

# symbole utilisé en interne pour une case vide
BLANK = "."

# vérifie qu'une ligne contient 81 caractères valides, sinon affiche l'erreur et retourne False
def check_line(line: str, name: str) -> bool:

    if len(line) != 81:
        print(f"Erreur : la ligne du {name} doit contenir 81 caractères (trouvé : {len(line)}).")
        return False
    
    for i, val in enumerate(line):
        if val not in BLANK_SYMBOLS and val not in "123456789":
            print(f"Valeur inattendue '{val}' dans le {name} à la position {i + 1}")
            return False
    return True


# convertit une ligne en liste de caractères, en remplaçant tout symbole de case vide par BLANK
def to_list(line: str) -> list[str]:
    return [BLANK if val in BLANK_SYMBOLS else val for val in line]


# lit le fichier sudoku : ligne 1 = puzzle, ligne 2 = solution (les autres lignes qui sont des ratings sont ignorées)
# retourne (puzzle, solution), deux listes de 81 caractères, ou False en cas d'erreur de format
def parse_sudoku_file(filename: str) -> tuple[list[str], list[str]] | Literal[False]:
    with open(filename, "r", encoding="utf-8") as f:
        puzzle = f.readline().strip()
        solution = f.readline().strip()

    if not check_line(puzzle, "puzzle") or not check_line(solution, "solution"):
        return False

    return to_list(puzzle), to_list(solution)
