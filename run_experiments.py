"""
run_experiments.py
Runs every algorithm on every problem size, many times, and saves the results.

Usage:
    python run_experiments.py           # full experiment (30 runs each)
    python run_experiments.py --quick   # fast check (3 runs each)

Outputs (in the results/ folder):
    runs.csv        one row per run: score, gap to optimum, time, iteration where the best was found
    memory.csv      peak memory of one extra run per algorithm and size
    histories.json  best-score-per-iteration for every run (used for the convergence plots)
"""
import csv
import json
import os
import sys
import time
import tracemalloc

from problem import generate_instance, SIZES
from dp import solve_dp
from ga import solve_ga
from pso import solve_pso
from aco import solve_aco

# ---------------- settings ----------------
N_RUNS = 3 if "--quick" in sys.argv else 30
INSTANCE_SEED = 42            # the problem data is the same in every run
RESULTS_DIR = "results"

# every algorithm: same instance in, (best solution, best score, history) out
ALGORITHMS = {
    "GA":  lambda v, w, c, seed: solve_ga(v, w, c, seed=seed),
    "PSO": lambda v, w, c, seed: solve_pso(v, w, c, seed=seed),
    "ACO": lambda v, w, c, seed: solve_aco(v, w, c, seed=seed),
}
# -------------------------------------------


def first_iteration_at_best(history):
    """Convergence speed: the first iteration where the final best score was reached."""
    final = history[-1]
    for i, score in enumerate(history):
        if score == final:
            return i + 1
    return len(history)


def peak_memory_kb(function):
    """Run a function once and return its peak memory use in KB."""
    tracemalloc.start()
    function()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    run_rows, memory_rows, histories = [], [], {}

    for size_name, n in SIZES.items():
        values, weights, capacity = generate_instance(n, INSTANCE_SEED)

        # exact optimum from Dynamic Programming (also timed: it is a baseline)
        start = time.perf_counter()
        optimum, _ = solve_dp(values, weights, capacity)
        dp_time = time.perf_counter() - start
        run_rows.append(["DP", size_name, n, 0, 0, optimum, optimum, 0.0, round(dp_time, 4), ""])
        memory_rows.append(["DP", size_name, round(peak_memory_kb(
            lambda: solve_dp(values, weights, capacity)), 1)])
        print(f"[{size_name}] DP optimum = {optimum}  ({dp_time:.3f}s)")

        for algo_name, algo in ALGORITHMS.items():
            histories[f"{algo_name}|{size_name}"] = []
            for run in range(N_RUNS):
                start = time.perf_counter()
                _, score, history = algo(values, weights, capacity, run)
                elapsed = time.perf_counter() - start
                gap = 100 * (optimum - score) / optimum
                run_rows.append([algo_name, size_name, n, run, run, score, optimum,
                                 round(gap, 4), round(elapsed, 4),
                                 first_iteration_at_best(history)])
                histories[f"{algo_name}|{size_name}"].append(history)

            # one extra run just to measure memory (tracemalloc slows code, so not used for timing)
            memory_rows.append([algo_name, size_name, round(peak_memory_kb(
                lambda: algo(values, weights, capacity, 0)), 1)])

            scores = [r[5] for r in run_rows if r[0] == algo_name and r[1] == size_name]
            print(f"[{size_name}] {algo_name}: best={max(scores)}  "
                  f"mean={sum(scores) / len(scores):.1f}  ({N_RUNS} runs)")

    with open(os.path.join(RESULTS_DIR, "runs.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "size", "n", "run", "seed", "score", "optimum",
                         "gap_percent", "time_s", "iteration_of_best"])
        writer.writerows(run_rows)

    with open(os.path.join(RESULTS_DIR, "memory.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "size", "peak_memory_kb"])
        writer.writerows(memory_rows)

    with open(os.path.join(RESULTS_DIR, "histories.json"), "w") as f:
        json.dump(histories, f)

    print("Saved results to the results/ folder.")


if __name__ == "__main__":
    main()
