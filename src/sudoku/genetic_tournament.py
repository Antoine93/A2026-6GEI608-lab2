# Algorithme génétique à sélection par tournoi, version de base
# adapté du code du livre (Russell et Norvig, AIMA, Figure 4.8 ; aima-python, search.py : genetic_algorithm)
import logging
import random
import time

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme
POP_SIZE = 1000         # nombre d'individus par génération
TOURNAMENT_K = 2        # nombre de candidats par tournoi
TOURNAMENT_P = 0.8      # probabilité que le meilleur candidat gagne (1.0 = tournoi classique)
MUTATION_RATE = 0.3     # probabilité qu'un enfant soit muté
MUTATION_SWAPS = 10     # nombre d'échanges par mutation
MAX_GENERATIONS = 5000  # arrêt (échec) si aucune solution avant

# nombre d'exécutions par puzzle quand le fichier est lancé directement (uv run -m src.sudoku.genetic_tournament <puzzle>)
N_RUNS = 1

# affichage : logging.INFO = présentation des résultats (paramètres, redémarrages, résultat final, grilles) ;
# logging.DEBUG = en plus, détail de chaque itération ; logging.WARNING = rien (pour les mesures de temps)
LOG_LEVEL = logging.DEBUG
LOG_EVERY = 100         # en DEBUG, une ligne de résumé toutes les LOG_EVERY générations

# chaque message affiche le temps écoulé depuis le début de l'exécution (remis à zéro par genetic_algorithm)
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


# sélection par tournoi probabiliste : tire k individus, les classe du meilleur au pire (fitness à minimiser) ;
# le meilleur gagne avec une probabilité p, sinon le suivant avec p, etc. ; le dernier gagne si aucun n'a été retenu
# avec p = 1.0, c'est le tournoi classique (le meilleur gagne toujours)
def tournament_selection(population, fitness_fn, k, p=1.0):
    candidates = sorted(random.sample(population, k), key=fitness_fn)
    for candidate in candidates[:-1]:
        if random.random() < p:
            return candidate
    return candidates[-1]


# crossover uniforme par lignes (adapté de recombine_uniform d'AIMA) : chaque ligne vient au hasard de P1 ou de P2
# 2^9 combinaisons possibles au lieu de 8 ; les lignes restent entières, donc valides, et les cases données sont conservées
def crossover_uniform(parent1, parent2):
    child = []
    for r in range(9):
        parent = parent1 if random.random() < 0.5 else parent2
        child += parent[9 * r : 9 * r + 9]
    return child


# indices des cases modifiables de chaque ligne, en ne gardant que les lignes qui en ont au moins 2
# ne dépend que du puzzle : calculé une seule fois, puis passé à mutate
def mutable_rows(fixed):
    rows = [[i for i in row if not fixed[i]] for row in ROWS]
    return [free for free in rows if len(free) >= 2]


# mutation : répète swaps fois l'échange de deux cases modifiables d'une même ligne (la ligne reste valide)
# à chaque échange, la ligne est tirée dans rows (résultat de mutable_rows)
def mutate(board, rows, swaps=1):
    if not rows:
        return board
    child = board[:]
    for _ in range(swaps):
        a, b = random.sample(random.choice(rows), 2)
        child[a], child[b] = child[b], child[a]
    return child


# boucle des générations : s'arrête sur une solution (0 conflit) ou après MAX_GENERATIONS (échec)
# retourne (meilleure grille vue, nombre de générations, conflits du meilleur à chaque génération, 0 redémarrage)
def genetic_algorithm(puzzle):
    global run_start
    run_start = time.perf_counter()
    rows = mutable_rows(get_fixed(puzzle))
    population = [fill_rows(puzzle) for _ in range(POP_SIZE)]
    scores = [conflicts(b) for b in population]   # conflits calculés une seule fois par individu

    costs = []
    record = min(scores)          # meilleur score vu depuis le début
    restart_count = 0             # pas de redémarrage : gardé pour le format de retour commun avec le hill climbing
    overall_best = population[scores.index(record)]   # meilleure grille vue (le meilleur peut disparaître d'une génération à l'autre)

    logger.info(f"début : population={POP_SIZE}, k={TOURNAMENT_K}, p={TOURNAMENT_P}, crossover uniforme, "
                f"mutation={MUTATION_RATE} ({MUTATION_SWAPS} échange(s)), "
                f"max={MAX_GENERATIONS}, meilleur initial={record} conflits")

    for generation in range(1, MAX_GENERATIONS + 1):
        # le tournoi travaille sur les indices : fitness_fn lit le score déjà calculé
        score_of = lambda i: scores[i]
        next_generation = []
        mutations = 0
        for _ in range(POP_SIZE):
            parent1 = population[tournament_selection(range(POP_SIZE), score_of, TOURNAMENT_K, TOURNAMENT_P)]
            parent2 = population[tournament_selection(range(POP_SIZE), score_of, TOURNAMENT_K, TOURNAMENT_P)]
            child = crossover_uniform(parent1, parent2)
            if random.random() < MUTATION_RATE:
                child = mutate(child, rows, MUTATION_SWAPS)
                mutations += 1
            next_generation.append(child)
        population = next_generation
        scores = [conflicts(b) for b in population]

        best_score = min(scores)
        best = population[scores.index(best_score)]
        costs.append(best_score)
        if best_score < record:
            record = best_score
            overall_best = best

        logger.debug(f"génération {generation} : meilleur={best_score}, moyenne={sum(scores) / POP_SIZE:.1f}, "
                     f"pire={max(scores)}, mutations={mutations}")
        if generation % LOG_EVERY == 0:
            logger.debug(f"génération {generation} : meilleur={best_score} conflits, record={record}")

        if best_score == 0:
            logger.info(f"solution trouvée à la génération {generation}")
            return best, generation, costs, restart_count

    logger.info(f"échec : {MAX_GENERATIONS} générations atteintes, meilleur={record} conflits")
    return overall_best, MAX_GENERATIONS, costs, restart_count


# lancement direct : uv run -m src.sudoku.genetic_tournament [fichier de puzzle] (sans argument : tous les puzzles)
if __name__ == "__main__":
    import sys
    from .runner import run
    run(sys.modules[__name__], genetic_algorithm)
