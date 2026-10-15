# Fichier d'implémentation du hill climbing (adapté de aima-python, search.py)
import random

from .commun import ROWS, get_fixed, fill_rows, conflicts

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

# garde le meilleur voisin, s'arrête quand aucun voisin n'est meilleur
def hill_climbing(puzzle):
    fixed = get_fixed(puzzle)
    current = fill_rows(puzzle)
    while True:
        neighbors = get_neighbors(current, fixed)
        if not neighbors:
            break
        neighbor = argmax_random_tie(neighbors, key=value)
        if value(neighbor) <= value(current):
            break
        current = neighbor
    return current
