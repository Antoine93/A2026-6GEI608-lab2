# Fichier d'implémentation du hill climbing (adapté de aima-python, search.py)
import logging
import random
import time

from .commun import ROWS, get_fixed, fill_rows, conflicts

# affichage : logging.INFO = début, progression et fin ; logging.DEBUG = détail de chaque itération et redémarrage
# logging.WARNING = rien (pour les mesures de temps)
LOG_LEVEL = logging.INFO
LOG_EVERY = 1000          # en INFO, une ligne de progression toutes les LOG_EVERY itérations

# chaque message affiche le temps écoulé depuis le début de l'exécution (remis à zéro par hill_climbing)
run_start = time.perf_counter()

def add_elapsed(record):
    record.elapsed = time.perf_counter() - run_start
    return True

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s %(elapsed)7.1f s] %(message)s"))
    handler.addFilter(add_elapsed)
    logger.addHandler(handler)

# mélange une copie de la liste
def shuffled(iterable):
    items = list(iterable)
    random.shuffle(items)
    return items

# retourne l'élément avec la plus grande valeur de key, égalités départagées au hasard
def argmax_random_tie(seq, key):
    return max(shuffled(seq), key=key)

# voisins : échange de deux cases non fixes d'une même ligne (les lignes restent valides)
def get_neighbors(board, fixed):
    neighbors = []
    for row in ROWS:
        free = [i for i in row if not fixed[i]]
        for a in range(len(free)):
            for b in range(a + 1, len(free)):
                new_board = board[:]
                new_board[free[a]], new_board[free[b]] = new_board[free[b]], new_board[free[a]]
                neighbors.append(new_board)
    return neighbors

# maximise une valeur : on prend l'opposé du nombre de conflits
def value(board):
    return -conflicts(board)

# redémarre d'une nouvelle grille quand il est bloqué et s'arrete quand le sudoku est résolu
def hill_climbing(puzzle):
    global run_start
    run_start = time.perf_counter()
    fixed = get_fixed(puzzle)
    current = fill_rows(puzzle)

    iterations = 0
    costs = []
    restart_count = 0
    record = conflicts(current)   # meilleur coût vu, tous redémarrages confondus (pour l'affichage)

    logger.info(f"début : coût initial={record} conflits")

    while True:

        #cout de l'état courant à chaque itération, avant de chercher un voisin
        cost = conflicts(current)
        costs.append(cost)
        record = min(record, cost)

        iterations += 1

        logger.debug(f"itération {iterations} : coût={cost}, record={record}, redémarrages={restart_count}")
        if iterations % LOG_EVERY == 0:
            logger.info(f"itération {iterations} : coût={cost}, record={record}, redémarrages={restart_count}")

        if cost == 0:
            logger.info(f"solution trouvée à l'itération {iterations} après {restart_count} redémarrage(s)")
            return current, iterations, costs, restart_count

        neighbors = get_neighbors(current, fixed)
        if not neighbors:
            logger.info(f"aucun voisin possible à l'itération {iterations}, arrêt à {cost} conflits")
            return current, iterations, costs, restart_count

        neighbor = argmax_random_tie(neighbors, key=value)
        if value(neighbor) <= value(current):
            # bloqué, on redémarre une nouvelle grille
            restart_count += 1
            logger.debug(f"itération {iterations} : optimum local à {cost} conflits, redémarrage n° {restart_count}")
            current = fill_rows(puzzle)
        else:
            current = neighbor
