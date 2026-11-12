"""
problem.py
The 0/1 Knapsack (project funding) problem: instance generator + fitness.
Every algorithm (GA, PSO, ACO, DP) will import from this file.
"""
import random

# The three problem sizes used in the experiments
SIZES = {"small": 20, "medium": 100, "large": 500}


def generate_instance(n, seed=42):
    """Create a random problem with n projects.
    Using the same seed always gives the same instance (reproducible)."""
    rng = random.Random(seed)
    values = [rng.randint(1, 100) for _ in range(n)]   # benefit of each project
    weights = [rng.randint(1, 50) for _ in range(n)]   # cost of each project
    capacity = int(0.4 * sum(weights))                 # budget = 40% of total cost
    return values, weights, capacity


def total_value(choices, values):
    """Sum of the values of the picked items (choices[i] == 1)."""
    total = 0
    for i in range(len(choices)):
        if choices[i] == 1:
            total += values[i]
    return total


def total_weight(choices, weights):
    """Sum of the weights (costs) of the picked items."""
    total = 0
    for i in range(len(choices)):
        if choices[i] == 1:
            total += weights[i]
    return total


def is_feasible(choices, weights, capacity):
    """True if the picked items fit inside the budget."""
    return total_weight(choices, weights) <= capacity


def fitness(choices, values, weights, capacity):
    """Score of a solution: its total value, or 0 if it breaks the budget."""
    if not is_feasible(choices, weights, capacity):
        return 0
    return total_value(choices, values)


if __name__ == "__main__":
    # Test with the small example from problem_definition.txt
    values = [10, 40, 30, 50]
    weights = [5, 4, 6, 3]
    capacity = 10

    print(fitness([0, 1, 0, 1], values, weights, capacity))  # expect 90
    print(fitness([1, 1, 1, 0], values, weights, capacity))  # expect 0 (over budget)
    print(fitness([0, 0, 0, 0], values, weights, capacity))  # expect 0

    # Test the generator
    v, w, cap = generate_instance(SIZES["small"])
    print("capacity:", cap, "| first 5 values:", v[:5])
