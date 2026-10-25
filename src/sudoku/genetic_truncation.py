# Algorithme génétique à sélection par troncature uniforme : version de base (genetic_tournament.py) dont le tournoi est remplacé
# par un tirage uniforme parmi les individus dont le score est au plus celui du quantile TRUNCATION_QUANTILE
# la direction vient de l'élimination des pires (ils ne se reproduisent jamais), pas de la faveur aux meilleurs :
# parmi les admissibles, un individu à 5 conflits n'a pas plus de chances qu'un individu à 25 ; pas d'élitisme
import logging
import random
import time

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme
POP_SIZE = 50000            # nombre d'individus par génération
TRUNCATION_QUANTILE = 0.95  # seuil, de 0.0 à 1.0 : seuls les individus au plus à ce quantile des scores sont parents (0.5 = médiane)
MUTATION_RATE = 0.01        # probabilité qu'un enfant soit muté
MUTATION_SWAP_RATE = 1.0    # fraction des cases modifiables touchées par une mutation, de 0.0 à 1.0 (1.0 = toutes en moyenne)
                            # nombre d'échanges = taux × cases modifiables ÷ 2 (un échange touche 2 cases), au moins 1
MAX_GENERATIONS = 50000     # arrêt (échec) si aucune solution avant

# affichage : logging.INFO = début, progression et fin ; logging.DEBUG = détail de chaque génération
# logging.WARNING = rien (pour les mesures de temps)
LOG_LEVEL = logging.DEBUG
LOG_EVERY = 100             # en INFO, une ligne de progression toutes les LOG_EVERY générations

# mesures de diversité affichées dans les logs
DIVERSITY_SAMPLES = 200     # paires d'individus tirées pour estimer la distance moyenne entre grilles
FROZEN_THRESHOLD = 0.95     # une case est « figée » si au moins cette fraction de la population y a le même chiffre

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


# score du quantile q, de 0.0 à 1.0 (q = 0.0 : le meilleur ; q = 0.5 : la médiane ; q = 1.0 : le pire)
def quantile(scores, q):
    ordered = sorted(scores)
    return ordered[int(q * (len(ordered) - 1))]


# parents admissibles : indices des individus dont le score est au plus le seuil (égalités au seuil incluses)
def eligible_parents(scores, threshold):
    return [i for i, s in enumerate(scores) if s <= threshold]


# diversité réelle : nombre moyen de cases différentes entre deux individus, estimé sur un échantillon de paires
def mean_distance(population, samples):
    total = 0
    for _ in range(samples):
        a, b = random.sample(population, 2)
        total += sum(x != y for x, y in zip(a, b))
    return total / samples


# convergence par case : pourcentage des cases modifiables où au moins FROZEN_THRESHOLD de la population
# a le même chiffre (coûteux : calculé seulement toutes les LOG_EVERY générations)
def frozen_ratio(population, cells, threshold):
    frozen = 0
    for i in cells:
        counts = {}
        for board in population:
            counts[board[i]] = counts.get(board[i], 0) + 1
        if max(counts.values()) >= threshold * len(population):
            frozen += 1
    return 100 * frozen / len(cells)


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
    cells = [i for free in rows for i in free]      # cases modifiables (dans les lignes qui en ont au moins 2)
    modifiable = len(cells)
    swaps = max(1, round(MUTATION_SWAP_RATE * modifiable / 2))
    population = [fill_rows(puzzle) for _ in range(POP_SIZE)]
    scores = [conflicts(b) for b in population]   # conflits calculés une seule fois par individu

    costs = []
    record = min(scores)          # meilleur score vu depuis le début
    restart_count = 0             # pas de redémarrage : gardé pour le format de retour commun avec le hill climbing
    overall_best = population[scores.index(record)]   # meilleure grille vue (le meilleur peut disparaître d'une génération à l'autre)

    logger.info(f"début : population={POP_SIZE}, troncature au quantile {TRUNCATION_QUANTILE}, "
                f"crossover uniforme, "
                f"mutation={MUTATION_RATE} ({swaps} échange(s) = {MUTATION_SWAP_RATE} × {modifiable} cases ÷ 2), "
                f"max={MAX_GENERATIONS}, meilleur initial={record} conflits")

    for generation in range(1, MAX_GENERATIONS + 1):
        # troncature : seuil = quantile des scores ; les parents sont tirés uniformément parmi les admissibles
        threshold = quantile(scores, TRUNCATION_QUANTILE)
        parents = eligible_parents(scores, threshold)
        next_generation = []
        mutations = 0
        for _ in range(POP_SIZE):
            parent1 = population[random.choice(parents)]
            parent2 = population[random.choice(parents)]
            child = crossover_uniform(parent1, parent2)
            if random.random() < MUTATION_RATE:
                child = mutate(child, rows, swaps)
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

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"génération {generation} : meilleur={best_score}, moyenne={sum(scores) / POP_SIZE:.1f}, "
                         f"pire={max(scores)}, seuil={threshold}, parents admissibles={len(parents)}, mutations={mutations}, "
                         f"distance moyenne={mean_distance(population, DIVERSITY_SAMPLES):.1f}/{modifiable}")
        if generation % LOG_EVERY == 0:
            logger.info(f"génération {generation} : meilleur={best_score} conflits, seuil={threshold}, "
                        f"parents admissibles={len(parents)}, record={record}, "
                        f"distance moyenne={mean_distance(population, DIVERSITY_SAMPLES):.1f}/{modifiable}, "
                        f"cases figées={frozen_ratio(population, cells, FROZEN_THRESHOLD):.0f} %")

        if best_score == 0:
            logger.info(f"solution trouvée à la génération {generation}")
            return best, generation, costs, restart_count

    logger.info(f"échec : {MAX_GENERATIONS} générations atteintes, meilleur={record} conflits")
    return overall_best, MAX_GENERATIONS, costs, restart_count
