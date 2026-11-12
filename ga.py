"""
ga.py
Genetic Algorithm for the 0/1 Knapsack (project funding) problem.

Solution representation : list of n bits (1 = project funded)
Fitness                 : total value (solutions are repaired so they never exceed the budget)
Selection               : tournament
Crossover               : one-point
Mutation                : bit flip
Elitism                 : the best few individuals are copied unchanged
Stopping criterion      : fixed number of generations
"""
import random
from problem import generate_instance, fitness, total_weight, SIZES


def repair(choices, weights, capacity, rng):
    """If a solution is over budget, drop random picked items until it fits."""
    w = total_weight(choices, weights)
    picked = [i for i in range(len(choices)) if choices[i] == 1]
    rng.shuffle(picked)
    for i in picked:
        if w <= capacity:
            break
        choices[i] = 0
        w -= weights[i]
    return choices


def create_individual(n, weights, capacity, rng):
    choices = [rng.randint(0, 1) for _ in range(n)]
    return repair(choices, weights, capacity, rng)


def tournament_select(population, scores, k, rng):
    """Pick k random individuals and return (a copy of) the best of them."""
    contenders = rng.sample(range(len(population)), k)
    winner = max(contenders, key=lambda i: scores[i])
    return population[winner][:]


def crossover(parent1, parent2, rate, rng):
    """One-point crossover: child takes the start of one parent and the end of the other."""
    if rng.random() < rate:
        point = rng.randint(1, len(parent1) - 1)
        return (parent1[:point] + parent2[point:],
                parent2[:point] + parent1[point:])
    return parent1[:], parent2[:]


def mutate(choices, rate, rng):
    """Flip each bit with a small probability."""
    for i in range(len(choices)):
        if rng.random() < rate:
            choices[i] = 1 - choices[i]
    return choices


def solve_ga(values, weights, capacity,
             pop_size=100, generations=200,
             crossover_rate=0.9, mutation_rate=None,
             tournament_size=3, elite=2, seed=0):
    rng = random.Random(seed)
    n = len(values)
    if mutation_rate is None:
        mutation_rate = 1.0 / n          # on average one bit flips per child

    population = [create_individual(n, weights, capacity, rng) for _ in range(pop_size)]
    best_choices, best_score = None, -1
    history = []                         # best score after each generation

    for _ in range(generations):
        scores = [fitness(ind, values, weights, capacity) for ind in population]

        # remember the best solution found so far
        gen_best = max(range(pop_size), key=lambda i: scores[i])
        if scores[gen_best] > best_score:
            best_score = scores[gen_best]
            best_choices = population[gen_best][:]
        history.append(best_score)

        # elitism: keep the top individuals as they are
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        new_population = [population[i][:] for i in ranked[:elite]]

        # fill the rest of the new generation with children
        while len(new_population) < pop_size:
            p1 = tournament_select(population, scores, tournament_size, rng)
            p2 = tournament_select(population, scores, tournament_size, rng)
            c1, c2 = crossover(p1, p2, crossover_rate, rng)
            for child in (c1, c2):
                child = mutate(child, mutation_rate, rng)
                child = repair(child, weights, capacity, rng)
                if len(new_population) < pop_size:
                    new_population.append(child)

        population = new_population

    return best_choices, best_score, history


if __name__ == "__main__":
    from dp import solve_dp
    for name, n in SIZES.items():
        v, w, cap = generate_instance(n)
        optimum, _ = solve_dp(v, w, cap)
        _, score, history = solve_ga(v, w, cap, seed=1)
        print(f"{name:7s} GA={score:6d}  DP optimum={optimum:6d}  "
              f"gap={100 * (optimum - score) / optimum:.2f}%")
