import time

from src.sudoku.hill_climbing import hill_climbing
from src.sudoku.commun import print_board
from src.sudoku.parser import parse_sudoku_file
from src.sudoku.solvability import isValid
from src.sudoku.genetic import genetic_algorithm

# ajout d'un dictionnaire pour mapper les algorithmes aux fonctions correspondantes
SOLVERS = {
    "hill_climbing": hill_climbing,
    "genetic": genetic_algorithm
}

if __name__ == '__main_sudoku__':

    # filename = "data\input-sudoku\Sudoku-01-simple.txt"
    filename = str(input("Nom du fichier (relatif) : "))
    parsed = parse_sudoku_file(filename)

    # Gestion des erreurs de parsing
    if parsed is False:
        print("Erreur lors de l'analyse du fichier. Veuillez vérifier le format.")
        exit(1)

    # demander à l'utilisateur quel algorithme utiliser
    algo = input("Algorithme à utiliser (hill_climbing, genetic) : ").strip().lower()
    if algo not in SOLVERS:
        print(f" '{algo}' non reconnu. Veuillez choisir parmi : {', '.join(SOLVERS.keys())}.")
        exit(1)

    solve = SOLVERS[algo]
    board = parsed[0]

    # condition pour vérifier si le sudoku est solvable avant de lancer la recherche
    if not isValid(board):
        print("Le sudoku n'est pas solvable.")
        exit(1)

    print('Initial State loaded from file:')
    print_board(board)