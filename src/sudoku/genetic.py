# Fichier d'implémentation de l'algorithme génétique (structure inspirée de aima-python, Figure 4.8)
# ancienne version AIMA non adaptée : genetic_aima.py
import random

from .commun import ROWS, get_fixed, fill_rows, conflicts

# paramètres de l'algorithme (valeurs à choisir à l'étape 2d)
POP_SIZE = None        # nombre d'individus par génération
TOURNAMENT_K = None    # nombre de candidats par tournoi


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


# temporaire : main_sudoku.py importe cette fonction
def genetic_algorithm(puzzle):
    raise NotImplementedError("algorithme génétique en cours d'écriture")
