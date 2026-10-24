# Algorithme génétique augmenté : version de base (genetic.py) + élitisme + mutation adaptative en vague
# (structure inspirée de aima-python, Figure 4.8 ; ancienne version AIMA non adaptée : genetic_aima.py)
import logging
import random

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme
POP_SIZE = 1000            # nombre d'individus par génération
TOURNAMENT_K = 2          # nombre de candidats par tournoi
MAX_GENERATIONS = 5000    # arrêt (échec) si aucune solution avant
ELITE_RATE = 0.01         # fraction des meilleurs recopiés tels quels dans la génération suivante (au moins 1)

# mutation adaptative en vague : quand la recherche stagne, un niveau de mutation monte palier par palier
# (le taux d'abord, puis le nombre d'échanges), reste un palier au sommet, redescend, puis la vague recommence
# un nouveau record ramène au niveau 0 (taux de base, 1 échange)
MUTATION_BASE_RATE = 0.1  # probabilité qu'un enfant soit muté, au niveau 0
STAGNATION_INCREMENT = 200 # durée d'un palier : générations sans nouveau record avant de changer de niveau
MUTATION_INCREMENT = 0.1  # hausse du taux par niveau
MUTATION_MAX_RATE = 1.0   # plafond du taux
MUTATION_MAX_SWAPS = 3    # une fois le taux au plafond, chaque niveau ajoute un échange par mutation, jusqu'à ce plafond

RATE_LEVELS = round((MUTATION_MAX_RATE - MUTATION_BASE_RATE) / MUTATION_INCREMENT)  # niveaux où monte le taux
TOP_LEVEL = RATE_LEVELS + MUTATION_MAX_SWAPS - 1                                    # sommet de la vague

# affichage : logging.INFO = début, progression et fin ; logging.DEBUG = détail de chaque génération
# logging.WARNING = rien (pour les mesures de temps)
LOG_LEVEL = logging.DEBUG
LOG_EVERY = 100           # en INFO, une ligne de progression toutes les LOG_EVERY générations

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)


# sélection par tournoi : tire k individus au hasard et retourne celui dont la fitness est la plus petite
# (fitness à minimiser, ex. conflicts)
def tournament_selection(population, fitness_fn, k):
    candidates = random.sample(population, k)
    return min(candidates, key=fitness_fn)


# crossover par lignes : lignes 0 à c-1 du parent 1, lignes c à 8 du parent 2
# les lignes restent entières, donc valides, et les cases données sont conservées
def crossover(parent1, parent2):
    c = random.randint(1, 8)
    return parent1[:9 * c] + parent2[9 * c:]


# mutation : répète swaps fois l'échange de deux cases modifiables d'une même ligne (la ligne reste valide)
# à chaque échange, la ligne est tirée parmi celles qui ont au moins 2 cases modifiables
def mutate(board, fixed, swaps=1):
    rows = [[i for i in row if not fixed[i]] for row in ROWS]
    rows = [free for free in rows if len(free) >= 2]
    if not rows:
        return board
    child = board[:]
    for _ in range(swaps):
        a, b = random.sample(random.choice(rows), 2)
        child[a], child[b] = child[b], child[a]
    return child


# taux et nombre d'échanges correspondant à un niveau de mutation
# niveaux 0 à RATE_LEVELS : le taux monte, 1 échange ; au-delà : taux au plafond, un échange de plus par niveau
def mutation_params(level):
    rate = round(MUTATION_BASE_RATE + MUTATION_INCREMENT * min(level, RATE_LEVELS), 2)
    swaps = 1 + max(0, level - RATE_LEVELS)
    return rate, swaps


# boucle des générations : s'arrête sur une solution (0 conflit) ou après MAX_GENERATIONS (échec)
# la mutation suit une vague liée à la stagnation (voir MUTATION_BASE_RATE et suivants)
# retourne (meilleure grille vue, nombre de générations, conflits du meilleur à chaque génération, 0 redémarrage)
def genetic_algorithm(puzzle):
    fixed = get_fixed(puzzle)
    population = [fill_rows(puzzle) for _ in range(POP_SIZE)]
    scores = [conflicts(b) for b in population]   # conflits calculés une seule fois par individu

    costs = []
    record = min(scores)          # meilleur score vu depuis le début
    stagnation = 0                # générations sans battre le record
    level = 0                     # niveau de mutation (0 = taux de base, 1 échange)
    direction = "montée"          # "montée", "sommet" ou "descente"
    mutation_rate, swaps = mutation_params(level)
    restart_count = 0             # pas de redémarrage : gardé pour le format de retour commun avec le hill climbing
    overall_best = population[scores.index(record)]   # meilleure grille vue (le meilleur peut disparaître d'une génération à l'autre)
    elite_count = max(1, int(POP_SIZE * ELITE_RATE))

    logger.info(f"début : population={POP_SIZE}, élites={elite_count}, k={TOURNAMENT_K}, "
                f"mutation {MUTATION_BASE_RATE} → {MUTATION_MAX_RATE} puis 1 → {MUTATION_MAX_SWAPS} échanges "
                f"(paliers de {STAGNATION_INCREMENT} générations, sommet au niveau {TOP_LEVEL}), "
                f"max={MAX_GENERATIONS}, meilleur initial={record} conflits")

    for generation in range(1, MAX_GENERATIONS + 1):
        # le tournoi travaille sur les indices : fitness_fn lit le score déjà calculé
        score_of = lambda i: scores[i]

        # élitisme : les elite_count meilleurs passent tels quels, sans crossover ni mutation
        elite_indices = sorted(range(POP_SIZE), key=score_of)[:elite_count]
        next_generation = [population[i] for i in elite_indices]

        mutations = 0
        for _ in range(POP_SIZE - elite_count):
            parent1 = population[tournament_selection(range(POP_SIZE), score_of, TOURNAMENT_K)]
            parent2 = population[tournament_selection(range(POP_SIZE), score_of, TOURNAMENT_K)]
            child = crossover(parent1, parent2)
            if random.random() < mutation_rate:
                child = mutate(child, fixed, swaps)
                mutations += 1
            next_generation.append(child)
        population = next_generation
        scores = [conflicts(b) for b in population]

        best_score = min(scores)
        best = population[scores.index(best_score)]
        costs.append(best_score)

        logger.debug(f"génération {generation} : meilleur={best_score}, moyenne={sum(scores) / POP_SIZE:.1f}, "
                     f"pire={max(scores)}, mutations={mutations}, niveau={level} ({direction}), "
                     f"taux={mutation_rate:.1f}, échanges={swaps}, stagnation={stagnation}")
        if generation % LOG_EVERY == 0:
            logger.info(f"génération {generation} : meilleur={best_score} conflits, record={record}, "
                        f"niveau={level} ({direction}), taux={mutation_rate:.1f}, échanges={swaps}")

        if best_score == 0:
            logger.info(f"solution trouvée à la génération {generation}")
            return best, generation, costs, restart_count

        # nouveau record : retour au niveau 0, en montée
        # sinon, à chaque palier : la vague monte d'un niveau, attend un palier au sommet, redescend, puis recommence
        if best_score < record:
            record = best_score
            overall_best = best
            stagnation = 0
            level, direction = 0, "montée"
        else:
            stagnation += 1
            if stagnation % STAGNATION_INCREMENT == 0:
                if direction == "montée":
                    level += 1
                    if level == TOP_LEVEL:
                        direction = "sommet"
                elif direction == "sommet":
                    direction = "descente"
                else:
                    level -= 1
                    if level == 0:
                        direction = "montée"
                logger.info(f"génération {generation} : bloqué à {record} conflits depuis {stagnation} générations, "
                            f"niveau={level} ({direction})")
        mutation_rate, swaps = mutation_params(level)

    logger.info(f"échec : {MAX_GENERATIONS} générations atteintes, meilleur={record} conflits")
    return overall_best, MAX_GENERATIONS, costs, restart_count
