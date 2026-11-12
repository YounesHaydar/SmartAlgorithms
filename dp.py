"""
dp.py
Dynamic Programming for 0/1 Knapsack: gives the TRUE optimum.
We use it as the baseline to measure how good the other algorithms are.
"""
from problem import generate_instance, fitness, SIZES


def solve_dp(values, weights, capacity):
    n = len(values)
    # best[w] = best value achievable with budget w using the items seen so far
    best = [0] * (capacity + 1)
    # keep[i][w] = True if item i was taken to reach best[w]
    keep = [[False] * (capacity + 1) for _ in range(n)]

    for i in range(n):
        # go from high budget to low so each item is used at most once
        for w in range(capacity, weights[i] - 1, -1):
            candidate = best[w - weights[i]] + values[i]
            if candidate > best[w]:
                best[w] = candidate
                keep[i][w] = True

    # walk backwards to recover WHICH items were chosen
    choices = [0] * n
    w = capacity
    for i in range(n - 1, -1, -1):
        if keep[i][w]:
            choices[i] = 1
            w -= weights[i]

    return best[capacity], choices


if __name__ == "__main__":
    # small example from problem_definition.txt
    print(solve_dp([10, 40, 30, 50], [5, 4, 6, 3], 10))   # expect (90, [0, 1, 0, 1])

    # check on a generated instance: DP value must equal fitness of its own solution
    for name, n in SIZES.items():
        v, w, cap = generate_instance(n)
        best_value, choices = solve_dp(v, w, cap)
        print(name, best_value, fitness(choices, v, w, cap))
