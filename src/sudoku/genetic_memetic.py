# Algorithme MÉMÉTIQUE (hybride génétique + recherche locale) : genetic_truncation.py + quelques pas de hill climbing
# appliqués à une fraction des enfants avant leur entrée dans la population
# le génétique explore (sélection par troncature uniforme, crossover, mutation) ; la recherche locale « finit » les enfants
# (derniers échanges précis que le génétique seul ne trouve pas) ; à présenter comme un hybride, pas comme un génétique pur
import logging
import random
import time

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme
POP_SIZE = 500            # nombre d'individus par génération (petit : chaque enfant coûte plus cher)
TRUNCATION_QUANTILE = 0.95 # seuil, de 0.0 à 1.0 : seuls les individus au plus à ce quantile des scores sont parents (0.5 = médiane)
MATING_TOLERANCE = None      # accouplement assortatif : le 2e parent a un score à ± MATING_TOLERANCE du 1er
                          # (0 = même score exactement ; None = désactivé, 2e parent au hasard parmi les admissibles)
MUTATION_RATE = 0.01       # probabilité qu'un enfant soit muté
MUTATION_SWAP_RATE = 1.0 # fraction des cases modifiables touchées par une mutation, de 0.0 à 1.0 (1.0 = toutes en moyenne)
                          # nombre d'échanges = taux × cases modifiables ÷ 2 (un échange touche 2 cases), au moins 1
MAX_GENERATIONS = 50000    # arrêt (échec) si aucune solution avant
CROSSOVER = "uniform"     # "uniform" : chaque ligne vient au hasard de P1 ou de P2 ; "one_point" : une coupe entre deux lignes

# recherche locale (partie mémétique)
LOCAL_SEARCH_RATE = 0.1   # fraction des enfants qui reçoivent la recherche locale (0 = génétique pur)
LOCAL_SEARCH_STEPS = 5    # pas de hill climbing au plus par enfant (arrêt plus tôt si aucun voisin n'est meilleur)

# redémarrage : quand la population a convergé (distance moyenne < RESTART_DISTANCE), on recrée toute la population
RESTART_DISTANCE = 1.0    # distance moyenne (en cases) sous laquelle la population est jugée figée (0 = désactivé)

# affichage : logging.INFO = début, progression et fin ; logging.DEBUG = détail de chaque génération
# logging.WARNING = rien (pour les mesures de temps)
LOG_LEVEL = logging.DEBUG
LOG_EVERY = 100           # en INFO, une ligne de progression toutes les LOG_EVERY générations

# mesures de diversité affichées dans les logs
DIVERSITY_SAMPLES = 200   # paires d'individus tirées pour estimer la distance moyenne entre grilles
FROZEN_THRESHOLD = 0.95   # une case est « figée » si au moins cette fraction de la population y a le même chiffre

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


# admissibles regroupés par score, une fois par génération : score -> indices
def group_by_score(indices, scores):
    groups = {}
    for i in indices:
        groups.setdefault(scores[i], []).append(i)
    return groups


# accouplement assortatif : 2e parent tiré uniformément parmi les admissibles dont le score est à ± tolerance de score ;
# on choisit d'abord un niveau de score au prorata de sa taille, puis un individu dans ce niveau (même résultat
# qu'un tirage uniforme dans la fenêtre, sans construire la liste) ; fenêtre vide → impossible ici (score lui-même inclus)
def assortative_mate(groups, score, tolerance):
    window = [(s, groups[s]) for s in range(score - tolerance, score + tolerance + 1) if s in groups]
    r = random.randrange(sum(len(members) for _, members in window))
    for _, members in window:
        if r < len(members):
            return members[r]
        r -= len(members)


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


# crossover par lignes : lignes 0 à c-1 du parent 1, lignes c à 8 du parent 2
# les lignes restent entières, donc valides, et les cases données sont conservées
def crossover(parent1, parent2):
    c = random.randint(1, 8)
    return parent1[:9 * c] + parent2[9 * c:]


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


# recherche locale : jusqu'à steps pas de hill climbing ; un pas teste tous les échanges de deux cases modifiables
# d'une même ligne et garde le meilleur s'il réduit les conflits (égalités départagées au hasard) ; sinon on s'arrête
# retourne (grille améliorée, ses conflits)
def local_search(board, rows, steps):
    board = board[:]
    cost = conflicts(board)
    for _ in range(steps):
        if cost == 0:
            break
        best_cost, best_moves = cost, []
        for free in rows:
            for x in range(len(free)):
                for y in range(x + 1, len(free)):
                    a, b = free[x], free[y]
                    board[a], board[b] = board[b], board[a]
                    c = conflicts(board)
                    board[a], board[b] = board[b], board[a]
                    if c < best_cost:
                        best_cost, best_moves = c, [(a, b)]
                    elif c == best_cost and best_moves:
                        best_moves.append((a, b))
        if not best_moves:
            break                       # optimum local : aucun échange ne réduit les conflits
        a, b = random.choice(best_moves)
        board[a], board[b] = board[b], board[a]
        cost = best_cost
    return board, cost


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
    restart_count = 0             # nombre de redémarrages de la population (population figée)
    overall_best = population[scores.index(record)]   # meilleure grille vue (le meilleur peut disparaître d'une génération à l'autre)

    cross = crossover_uniform if CROSSOVER == "uniform" else crossover

    logger.info(f"début : population={POP_SIZE}, troncature au quantile {TRUNCATION_QUANTILE}, "
                f"accouplement assortatif ± {MATING_TOLERANCE}, crossover={CROSSOVER}, "
                f"recherche locale sur {LOCAL_SEARCH_RATE} des enfants ({LOCAL_SEARCH_STEPS} pas max), "
                f"redémarrage si distance < {RESTART_DISTANCE}, "
                f"mutation={MUTATION_RATE} ({swaps} échange(s) = {MUTATION_SWAP_RATE} × {modifiable} cases ÷ 2), "
                f"max={MAX_GENERATIONS}, meilleur initial={record} conflits")

    for generation in range(1, MAX_GENERATIONS + 1):
        # troncature : seuil = quantile des scores ; les parents sont tirés uniformément parmi les admissibles
        threshold = quantile(scores, TRUNCATION_QUANTILE)
        parents = eligible_parents(scores, threshold)
        groups = group_by_score(parents, scores) if MATING_TOLERANCE is not None else None
        next_generation = []
        next_scores = []
        mutations = searched = improved = gain = 0
        for _ in range(POP_SIZE):
            i1 = random.choice(parents)
            if MATING_TOLERANCE is None:
                i2 = random.choice(parents)
            else:
                i2 = assortative_mate(groups, scores[i1], MATING_TOLERANCE)
            parent1, parent2 = population[i1], population[i2]
            child = cross(parent1, parent2)
            if random.random() < MUTATION_RATE:
                child = mutate(child, rows, swaps)
                mutations += 1
            if random.random() < LOCAL_SEARCH_RATE:
                before = conflicts(child)
                child, cost = local_search(child, rows, LOCAL_SEARCH_STEPS)
                searched += 1
                if cost < before:
                    improved += 1
                    gain += before - cost
            else:
                cost = conflicts(child)
            next_generation.append(child)
            next_scores.append(cost)
        population = next_generation
        scores = next_scores

        best_score = min(scores)
        best = population[scores.index(best_score)]
        costs.append(best_score)
        if best_score < record:
            record = best_score
            overall_best = best
        distance = mean_distance(population, DIVERSITY_SAMPLES)   # calculée à chaque génération (≈ 1 ms)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"génération {generation} : meilleur={best_score}, moyenne={sum(scores) / POP_SIZE:.1f}, "
                         f"pire={max(scores)}, seuil={threshold}, parents admissibles={len(parents)}, mutations={mutations}, "
                         f"recherche locale={searched} enfants ({improved} améliorés, gain moyen "
                         f"{gain / improved if improved else 0:.1f} conflits), "
                         f"distance moyenne={distance:.1f}/{modifiable}")
        if generation % LOG_EVERY == 0:
            logger.info(f"génération {generation} : meilleur={best_score} conflits, seuil={threshold}, "
                        f"parents admissibles={len(parents)}, record={record}, redémarrages={restart_count}, "
                        f"distance moyenne={distance:.1f}/{modifiable}, "
                        f"cases figées={frozen_ratio(population, cells, FROZEN_THRESHOLD):.0f} %")

        if best_score == 0:
            logger.info(f"solution trouvée à la génération {generation} après {restart_count} redémarrage(s)")
            return best, generation, costs, restart_count

        # population figée : on la recrée entièrement (le record reste dans overall_best)
        if distance < RESTART_DISTANCE:
            population = [fill_rows(puzzle) for _ in range(POP_SIZE)]
            scores = [conflicts(b) for b in population]
            restart_count += 1
            logger.info(f"génération {generation} : population figée (distance {distance:.1f}, meilleur {best_score}), "
                        f"redémarrage n° {restart_count}")

    logger.info(f"échec : {MAX_GENERATIONS} générations atteintes, meilleur={record} conflits, "
                f"{restart_count} redémarrage(s)")
    return overall_best, MAX_GENERATIONS, costs, restart_count
