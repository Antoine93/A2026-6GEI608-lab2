# lancement commun des algorithmes de la partie 2 depuis la ligne de commande, par exemple :
#   uv run -m src.sudoku.genetic_hc data/input-sudoku/Sudoku-07-expert.txt 10   (10 exécutions de ce puzzle)
#   uv run -m src.sudoku.genetic_hc data/input-sudoku/Sudoku-07-expert.txt      (N_RUNS du module)
#   uv run -m src.sudoku.genetic_hc 10                 (sans fichier : les 10 puzzles de data/input-sudoku)
# arguments : des fichiers de puzzle et/ou un nombre d'exécutions (un entier), dans n'importe quel ordre
# chaque lancement reçoit un identifiant (date et heure, ex. 20261025-014233) et son propre dossier :
#   results/sudoku/<algorithme>/<ID>/<puzzle>/runNN.log : les messages du logging (INFO = présentation des résultats ;
#                                                         DEBUG = détail de chaque itération)
#   results/sudoku/<algorithme>/<ID>/<puzzle>/runNN.txt : le fichier de résultats (une ligne par itération, puis
#                                                         itérations, temps, redémarrages)
#   results/sudoku/<algorithme>/<ID>/<puzzle>/stats.txt : les statistiques des exécutions de ce puzzle
#   results/sudoku/<algorithme>/<ID>/stats.txt          : le récapitulatif de tous les puzzles du lancement
import glob
import logging
import os
import statistics
import sys
import time
from datetime import datetime

from .commun import ROWS, conflicts, is_valid_config
from .parser import parse_sudoku_file
from src.utils import write_run_file

INPUT_DIR = os.path.join("data", "input-sudoku")
RESULTS_DIR = os.path.join("results", "sudoku")


# grille de 81 cases en 9 lignes de texte (même présentation que print_board)
def board_to_text(board):
    lines = []
    for r, row in enumerate(ROWS):
        if r % 3 == 0 and r != 0:
            lines.append("------+-------+------")
        cells = [board[i] for i in row]
        lines.append(" ".join(cells[0:3]) + " | " + " ".join(cells[3:6]) + " | " + " ".join(cells[6:9]))
    return "\n".join(lines)


# moyenne, écart-type, minimum et maximum d'une liste de valeurs (écart-type nul s'il n'y a qu'une valeur)
def describe(values):
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return f"moyenne={statistics.mean(values):.2f}, écart-type={std:.2f}, min={min(values):.2f}, max={max(values):.2f}"


# statistiques des exécutions d'un puzzle ; runs : liste de (n° d'exécution, temps, itérations, redémarrages, conflits)
def stats_text(algo, launch_id, puzzle_file, runs):
    solved = [r for r in runs if r[4] == 0]
    lines = [f"algorithme : {algo}", f"lancement : {launch_id}", f"puzzle : {puzzle_file}",
             f"exécutions : {len(runs)}", f"résolues : {len(solved)}/{len(runs)} ({100 * len(solved) / len(runs):.0f} %)", "",
             "exécution\ttemps (s)\titérations\tredémarrages\tconflits restants"]
    lines += [f"{n}\t{t:.3f}\t{it}\t{rs}\t{c}" for n, t, it, rs, c in runs]
    lines += ["", "toutes les exécutions :",
              f"  temps (s)    : {describe([r[1] for r in runs])}",
              f"  itérations   : {describe([r[2] for r in runs])}",
              f"  redémarrages : {describe([r[3] for r in runs])}",
              f"  conflits     : {describe([r[4] for r in runs])}"]
    if solved:
        lines += ["exécutions résolues seulement :",
                  f"  temps (s)    : {describe([r[1] for r in solved])}",
                  f"  itérations   : {describe([r[2] for r in solved])}"]
    return "\n".join(lines) + "\n"


# lance solve sur les puzzles demandés (ou tous), n_runs fois chacun
# module : le module de l'algorithme (fournit logger, add_elapsed, N_RUNS)
# solve : la fonction de l'algorithme, qui retourne (grille, itérations, coûts, redémarrages)
def run(module, solve):
    algo = module.__spec__.name.split(".")[-1]          # ex. genetic_hc (fonctionne aussi avec -m)
    logger = module.logger
    numbers = [a for a in sys.argv[1:] if a.isdigit()]
    n_runs = int(numbers[0]) if numbers else module.N_RUNS
    filenames = [a for a in sys.argv[1:] if not a.isdigit()] or sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt")))
    launch_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    launch_dir = os.path.join(RESULTS_DIR, algo, launch_id)   # dossier de ce lancement
    print(f"lancement {launch_id} : {algo}, {len(filenames)} puzzle(s), {n_runs} exécution(s) chacun, dans {launch_dir}")

    summary = []   # (puzzle, résolues, exécutions, temps moyen, itérations moyennes)

    for filename in filenames:
        name = os.path.splitext(os.path.basename(filename))[0]
        parsed = parse_sudoku_file(filename)
        if parsed is False:
            print(f"{filename} : erreur lors de l'analyse du fichier, puzzle ignoré.")
            continue
        puzzle, _ = parsed
        if not is_valid_config(puzzle):
            print(f"{filename} : le sudoku contient des doublons, puzzle ignoré.")
            continue

        out_dir = os.path.join(launch_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        runs = []

        for run_id in range(1, n_runs + 1):
            prefix = os.path.join(out_dir, f"run{run_id:02d}")
            # fichier de log de cette exécution, même format et même niveau que la console
            handler = logging.FileHandler(prefix + ".log", mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter("[%(levelname)s %(elapsed)7.1f s] %(message)s"))
            handler.addFilter(module.add_elapsed)
            logger.addHandler(handler)
            try:
                module.run_start = time.perf_counter()      # temps des logs remis à zéro dès l'en-tête
                logger.info(f"===== {algo} sur {os.path.basename(filename)} "
                            f"(lancement {launch_id}, exécution {run_id}/{n_runs}) =====")
                logger.info("grille de départ :\n" + board_to_text(puzzle))

                start = time.perf_counter()
                board, iterations, costs, restart_count = solve(puzzle)
                elapsed = time.perf_counter() - start

                remaining = conflicts(board)
                status = "résolu" if remaining == 0 else f"échec ({remaining} conflits restants)"
                logger.info(f"résultat : {status}, temps={elapsed:.2f} s, itérations={iterations}, "
                            f"redémarrages={restart_count}")
                logger.info("grille obtenue :\n" + board_to_text(board))

                write_run_file(prefix + ".txt", costs, iterations, elapsed, restart_count)
                runs.append((run_id, elapsed, iterations, restart_count, remaining))
            finally:
                logger.removeHandler(handler)
                handler.close()

        # statistiques des exécutions de ce puzzle
        stats_path = os.path.join(out_dir, "stats.txt")
        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(stats_text(algo, launch_id, os.path.basename(filename), runs))
        solved = sum(1 for r in runs if r[4] == 0)
        summary.append((name, solved, len(runs), statistics.mean(r[1] for r in runs), statistics.mean(r[2] for r in runs)))
        print(f"{name} : {solved}/{len(runs)} résolu(s), statistiques dans {stats_path}")

    # récapitulatif de tous les puzzles du lancement
    if summary:
        path = os.path.join(launch_dir, "stats.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"algorithme : {algo}\nlancement : {launch_id}\nexécutions par puzzle : {n_runs}\n\n")
            f.write("puzzle\trésolues\ttemps moyen (s)\titérations moyennes\n")
            for name, solved, total, t, it in summary:
                f.write(f"{name}\t{solved}/{total}\t{t:.3f}\t{it:.1f}\n")
            total_solved = sum(s[1] for s in summary)
            total_runs = sum(s[2] for s in summary)
            f.write(f"\ntotal : {total_solved}/{total_runs} résolues ({100 * total_solved / total_runs:.0f} %)\n")
        print(f"récapitulatif du lancement dans {path}")
