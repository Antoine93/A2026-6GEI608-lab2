# Programme récupéré de AIMA python dans la référence
# BESOIN D'ADAPTATION POUR FONCTIONNER AVEC NOTRE PROBLÈME DE SUDOKU

import random
from collections import Counter

def genetic_search(problem, ngen=1000, pmut=0.1, n=20):
    """Call genetic_algorithm on the appropriate parts of a problem.
    This requires the problem to have states that can mate and mutate,
    plus a value method that scores states."""

    s = problem.initial_state
    states = [problem.result(s, a) for a in problem.actions(s)]
    random.shuffle(states)
    return genetic_algorithm(states[:n], problem.value, ngen, pmut)


def genetic_algorithm(population, fitness_fn, gene_pool=[0, 1], f_thres=None, ngen=1000, pmut=0.1):
    """[Figure 4.8]"""
    for i in range(ngen):
        population = [mutate(recombine(*select(2, population, fitness_fn)), gene_pool, pmut)
                      for i in range(len(population))]

        fittest_individual = fitness_threshold(fitness_fn, f_thres, population)
        if fittest_individual:
            return fittest_individual

    return max(population, key=fitness_fn)


def fitness_threshold(fitness_fn, f_thres, population):
    """Return the fittest individual if its fitness reaches f_thres, otherwise None
    (also None when no threshold f_thres is given)."""
    if not f_thres:
        return None

    fittest_individual = max(population, key=fitness_fn)
    if fitness_fn(fittest_individual) >= f_thres:
        return fittest_individual

    return None


def init_population(pop_number, gene_pool, state_length):
    """Initializes population for genetic algorithm
    pop_number  :  Number of individuals in population
    gene_pool   :  List of possible values for individuals
    state_length:  The length of each individual"""
    g = len(gene_pool)
    population = []
    for i in range(pop_number):
        new_individual = [gene_pool[random.randrange(0, g)] for j in range(state_length)]
        population.append(new_individual)

    return population

# Valide tel quel
def weighted_sampler(population, weights):
    """Return a random function that chooses from population with probability
    proportional to the corresponding weight."""
    weights = list(weights)
    if not population:
        raise ValueError("population cannot be empty")

    total = sum(weights)
    if total <= 0:
        return random.choice(population)

    target = random.uniform(0, total)
    cumulative = 0
    for item, weight in zip(population, weights):
        cumulative += weight
        if cumulative >= target:
            return item

    return population[-1]

# Valide tel quel
def select(r, population, fitness_fn):
    """Select r individuals from the population, sampling each with probability
    proportional to its fitness."""
    fitnesses = [fitness_fn(individual) for individual in population]
    sampler = weighted_sampler(population, fitnesses)
    return [sampler() for i in range(r)]


def recombine(x, y):
    """Single-point crossover: combine a random-length prefix of x with the
    corresponding suffix of y."""
    n = len(x)
    c = random.randrange(0, n)
    return x[:c] + y[c:]


def recombine_uniform(x, y):
    """Uniform crossover: build a child string by taking roughly half of its genes
    from x and the rest from y, at random positions."""
    n = len(x)
    result = [0] * n
    indexes = random.sample(range(n), n)
    for i in range(n):
        ix = indexes[i]
        result[ix] = x[ix] if i < n / 2 else y[ix]

    return ''.join(str(r) for r in result)


def mutate(x, gene_pool, pmut):
    """With probability pmut, replace one randomly chosen gene of x with a random
    gene from gene_pool; otherwise return x unchanged."""
    if random.uniform(0, 1) >= pmut:
        return x

    n = len(x)
    g = len(gene_pool)
    c = random.randrange(0, n)
    r = random.randrange(0, g)

    new_gene = gene_pool[r]
    return x[:c] + [new_gene] + x[c + 1:]
