# Fichier d'implémentation de l'algorithme génétique (structure inspirée de aima-python, Figure 4.8)
# ancienne version AIMA non adaptée : genetic_aima.py
import random

from .commun import get_fixed, fill_rows, conflicts

# paramètres de l'algorithme (valeurs à choisir à l'étape 2d)
POP_SIZE = None        # nombre d'individus par génération
TOURNAMENT_K = None    # nombre de candidats par tournoi


# sélection par tournoi : tire k individus au hasard et retourne celui qui a le moins de conflits
def tournament_selection(population, k):
    candidates = random.sample(population, k)
    return min(candidates, key=conflicts)


# temporaire : main_sudoku.py importe cette fonction
def genetic_algorithm(puzzle):
    raise NotImplementedError("algorithme génétique en cours d'écriture")

def tournament_selection(population, fitness_fn, k):
