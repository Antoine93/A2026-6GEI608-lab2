# Fichier d'implémentation de l'algorithme génétique (structure inspirée de aima-python, Figure 4.8)
# ancienne version AIMA non adaptée : genetic_aima.py
import random

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme
POP_SIZE = 200            # nombre d'individus par génération
TOURNAMENT_K = 4          # nombre de candidats par tournoi
MUTATION_RATE = 0.2       # probabilité qu'un enfant soit muté
MAX_GENERATIONS = 5000    # arrêt (échec) si aucune solution avant


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


# mutation : échange deux cases modifiables d'une même ligne (la ligne reste valide)
# la ligne est tirée parmi celles qui ont au moins 2 cases modifiables
def mutate(board, fixed):
    rows = [[i for i in row if not fixed[i]] for row in ROWS]
    rows = [free for free in rows if len(free) >= 2]
    if not rows:
        return board
    a, b = random.sample(random.choice(rows), 2)
    child = board[:]
    child[a], child[b] = child[b], child[a]
    return child


# boucle des générations : s'arrête sur une solution (0 conflit) ou après MAX_GENERATIONS (échec)
# retourne (meilleure grille, nombre de générations, conflits du meilleur à chaque génération, 0 redémarrage)
def genetic_algorithm(puzzle):
    fixed = get_fixed(puzzle)
    population = [fill_rows(puzzle) for _ in range(POP_SIZE)]
    costs = []

    for generation in range(1, MAX_GENERATIONS + 1):
        next_generation = []
        for _ in range(POP_SIZE):
            parent1 = tournament_selection(population, conflicts, TOURNAMENT_K)
            parent2 = tournament_selection(population, conflicts, TOURNAMENT_K)
            child = crossover(parent1, parent2)
            if random.random() < MUTATION_RATE:
                child = mutate(child, fixed)
            next_generation.append(child)
        population = next_generation

        best = min(population, key=conflicts)
        costs.append(conflicts(best))
        if costs[-1] == 0:
            return best, generation, costs, 0

    return best, MAX_GENERATIONS, costs, 0
