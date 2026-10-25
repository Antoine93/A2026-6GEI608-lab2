import time

from src.sudoku.hill_climbing import hill_climbing
from src.sudoku.commun import print_board, is_valid_config
from src.sudoku.parser import parse_sudoku_file
from src.sudoku.genetic_tournament import genetic_algorithm as genetic_tournament_algorithm
from src.sudoku.genetic_truncation import genetic_algorithm as genetic_truncation_algorithm
from src.sudoku.genetic_memetic import genetic_algorithm as genetic_memetic_algorithm
from src.utils import write_run_file, output_path

# ajout d'un dictionnaire pour mapper les algorithmes aux fonctions correspondantes
SOLVERS = {
    "hill_climbing": hill_climbing,
    "genetic_tournament": genetic_tournament_algorithm,
    "genetic_truncation": genetic_truncation_algorithm,
    "genetic_memetic": genetic_memetic_algorithm
}

if __name__ == '__main__':

    # filename = "data\input-sudoku\Sudoku-01-simple.txt"
    filename = str(input("Nom du fichier (relatif) : "))
    parsed = parse_sudoku_file(filename)

    # Gestion des erreurs de parsing
    if parsed is False:
        print("Erreur lors de l'analyse du fichier. Veuillez vérifier le format.")
        exit(1)

    # demander à l'utilisateur quel algorithme utiliser
    algo = input("Algorithme à utiliser (hill_climbing, genetic_tournament, genetic_truncation, genetic_memetic) : ").strip().lower()
    if algo not in SOLVERS:
        print(f" '{algo}' non reconnu. Veuillez choisir parmi : {', '.join(SOLVERS.keys())}.")
        exit(1)

    solve = SOLVERS[algo]
    puzzle, solution = parsed

    # condition pour vérifier si le sudoku est solvable avant de lancer la recherche
    if not is_valid_config(puzzle):
        print("Le sudoku contient des doublons.")
        exit(1)

    print('Initial State loaded from file:')
    print_board(puzzle)

    # paramétrage du nombre de répétitions
    N_RUNS = 1
    total_time = 0.0
    result = None
    iterations = 0
    restart_count = 0

    print(f"Exécution de la recherche {N_RUNS} fois pour calcul de la moyenne...")

    # Boucle de benchmarking
    for run in range(1, N_RUNS + 1):
        start_time = time.perf_counter()
        result, iterations, costs, restart_count = solve(puzzle)
        end_time = time.perf_counter()
        total_time += (end_time - start_time)
        print(f"Nombre de redémarrages (dernière exécution) : {restart_count}")

        path = output_path("results/sudoku", algo, filename, run)
        write_run_file(path, costs, iterations, end_time - start_time)

    average_time = total_time / N_RUNS
    print(f"Temps d'exécution moyen sur {N_RUNS} essais : {average_time:.6f} secondes")

    # Affichage des résultats après la série de mesures
    print("Grille obtenue :")
    print_board(result)
    print(f"Nombre total d'itérations (dernière exécution) : {iterations}\n")
