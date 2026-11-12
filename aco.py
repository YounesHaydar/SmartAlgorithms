"""
aco.py
Ant Colony Optimization for the 0/1 Knapsack (project funding) problem.

Solution representation : each ant builds a list of n bits by choosing projects one at a time
Fitness                 : total value (ants only add projects that still fit, so solutions are always valid)
Choice rule             : an unpicked project is chosen with probability proportional to
                          pheromone^alpha * (value/weight)^beta
Pheromone update        : evaporation, then the best ant of the iteration reinforces its projects
Stopping criterion      : fixed number of iterations
"""
import math
import random
from problem import generate_instance, fitness, SIZES


def build_solution(attractiveness, weights, capacity, rng):
    """One ant builds one solution.

    Picking projects one by one, each with probability proportional to its
    attractiveness, is the same as giving every project a random 'key' that
    favours attractive ones, sorting by key, and adding projects in that order
    while they fit. We use the second form because it is much faster.
    """
    n = len(weights)
    keys = [math.log(rng.random()) / attractiveness[i] for i in range(n)]
    order = sorted(range(n), key=lambda i: keys[i], reverse=True)

    choices = [0] * n
    used = 0
    for i in order:
        if used + weights[i] <= capacity:
            choices[i] = 1
            used += weights[i]
    return choices


def solve_aco(values, weights, capacity,
              n_ants=100, iterations=200,
              alpha=1.0, beta=2.0, rho=0.1,
              tau_min=0.05, tau_max=1.0, seed=0):
    rng = random.Random(seed)
    n = len(values)

    ratio = [values[i] / weights[i] for i in range(n)]       # heuristic: value per cost
    max_ratio = max(ratio)
    eta = [r / max_ratio for r in ratio]                     # scaled to (0, 1]
    tau = [tau_max] * n                                      # pheromone on each project

    best_choices, best_score = None, -1
    history = []

    for _ in range(iterations):
        attractiveness = [(tau[i] ** alpha) * (eta[i] ** beta) for i in range(n)]

        # every ant builds a solution; keep the best of this iteration
        iter_best, iter_score = None, -1
        for _ in range(n_ants):
            choices = build_solution(attractiveness, weights, capacity, rng)
            score = fitness(choices, values, weights, capacity)
            if score > iter_score:
                iter_best, iter_score = choices, score

        if iter_score > best_score:
            best_choices, best_score = iter_best[:], iter_score

        # pheromone update: evaporate everywhere, reinforce the iteration-best solution
        quality = iter_score / best_score                    # at most 1
        for i in range(n):
            tau[i] *= (1 - rho)
            if iter_best[i] == 1:
                tau[i] += rho * quality
            tau[i] = max(tau_min, min(tau_max, tau[i]))

        history.append(best_score)

    return best_choices, best_score, history


if __name__ == "__main__":
    from dp import solve_dp
    for name, n in SIZES.items():
        v, w, cap = generate_instance(n)
        optimum, _ = solve_dp(v, w, cap)
        _, score, history = solve_aco(v, w, cap, seed=1)
        print(f"{name:7s} ACO={score:6d}  DP optimum={optimum:6d}  "
              f"gap={100 * (optimum - score) / optimum:.2f}%")
