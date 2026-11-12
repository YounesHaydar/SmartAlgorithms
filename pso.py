"""
pso.py
Binary Particle Swarm Optimization for the 0/1 Knapsack (project funding) problem.

Solution representation : each particle has a position (list of n bits) and a velocity (list of n real numbers)
Fitness                 : total value (positions are repaired so they never exceed the budget)
Movement                : velocity is pulled toward the particle's own best and the swarm's best;
                          sigmoid(velocity) is the probability that a bit becomes 1
Stopping criterion      : fixed number of iterations
"""
import math
import random
from problem import generate_instance, fitness, SIZES
from ga import repair          # same repair step as the GA (keeps the comparison fair)


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def solve_pso(values, weights, capacity,
              swarm_size=100, iterations=200,
              w=0.7, c1=1.5, c2=1.5, vmax=4.0, seed=0):
    rng = random.Random(seed)
    n = len(values)

    # start: random positions (repaired), small random velocities
    positions = []
    for _ in range(swarm_size):
        p = [rng.randint(0, 1) for _ in range(n)]
        positions.append(repair(p, weights, capacity, rng))
    velocities = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(swarm_size)]

    # each particle remembers its own best position
    pbest = [p[:] for p in positions]
    pbest_score = [fitness(p, values, weights, capacity) for p in positions]

    # the swarm remembers the overall best
    g = max(range(swarm_size), key=lambda i: pbest_score[i])
    gbest, gbest_score = pbest[g][:], pbest_score[g]

    history = []
    for _ in range(iterations):
        for i in range(swarm_size):
            for d in range(n):
                r1, r2 = rng.random(), rng.random()
                velocities[i][d] = (w * velocities[i][d]
                                    + c1 * r1 * (pbest[i][d] - positions[i][d])
                                    + c2 * r2 * (gbest[d] - positions[i][d]))
                # keep the velocity from growing too large
                velocities[i][d] = max(-vmax, min(vmax, velocities[i][d]))
                # sigmoid turns velocity into a probability of the bit being 1
                positions[i][d] = 1 if rng.random() < sigmoid(velocities[i][d]) else 0

            positions[i] = repair(positions[i], weights, capacity, rng)
            score = fitness(positions[i], values, weights, capacity)

            if score > pbest_score[i]:
                pbest[i], pbest_score[i] = positions[i][:], score
                if score > gbest_score:
                    gbest, gbest_score = positions[i][:], score

        history.append(gbest_score)

    return gbest, gbest_score, history


if __name__ == "__main__":
    from dp import solve_dp
    for name, n in SIZES.items():
        v, wts, cap = generate_instance(n)
        optimum, _ = solve_dp(v, wts, cap)
        _, score, history = solve_pso(v, wts, cap, seed=1)
        print(f"{name:7s} PSO={score:6d}  DP optimum={optimum:6d}  "
              f"gap={100 * (optimum - score) / optimum:.2f}%")
