"""
analyze.py
Turns the files in results/ into the tables and plots the report needs.
Dynamic Programming (DP) is shown as the exact reference:
  - a dashed line at the DP optimum on the convergence and boxplot charts
  - a DP row in the summary table
  - DP's runtime and memory next to the three heuristics

Usage:
    python analyze.py

Outputs (in results/):
    summary_table.csv        quality, stability, time, gap, convergence iteration per algorithm x size (DP included)
    memory_table.csv         peak memory per algorithm x size (DP included)
    convergence_<size>.png   Iteration -> Best Fitness, with the DP optimum as a dashed line
    boxplot_<size>.png       spread of final scores across runs, with the DP optimum line
    runtime_vs_size.png      how runtime scales with problem size (DP included)
"""
import csv
import json
import os
import statistics as stats

import matplotlib.pyplot as plt

from problem import SIZES

RESULTS_DIR = "results"
ALGORITHMS = ["GA", "PSO", "ACO"]        # the heuristics (many runs each)
ALL_ALGORITHMS = ["DP"] + ALGORITHMS     # DP first, as the reference


def read_csv(name):
    with open(os.path.join(RESULTS_DIR, name)) as f:
        return list(csv.DictReader(f))


def load_histories():
    with open(os.path.join(RESULTS_DIR, "histories.json")) as f:
        return json.load(f)


def get_optimum(rows, size_name):
    """The exact optimum from DP for this size."""
    for r in rows:
        if r["algorithm"] == "DP" and r["size"] == size_name:
            return float(r["score"])


def build_summary_table(rows):
    """One row per (algorithm, size). DP has a single run, so its std is 0."""
    table = []
    for size_name in SIZES:
        for algo in ALL_ALGORITHMS:
            sel = [r for r in rows if r["algorithm"] == algo and r["size"] == size_name]
            scores = [float(r["score"]) for r in sel]
            times = [float(r["time_s"]) for r in sel]
            gaps = [float(r["gap_percent"]) for r in sel]
            # convergence speed: iteration where the final best score was first reached (DP has none)
            iters = [float(r["iteration_of_best"]) for r in sel if r["iteration_of_best"] != ""]
            table.append({
                "size": size_name,
                "algorithm": algo,
                "runs": len(scores),
                "mean_score": round(stats.mean(scores), 1),
                "std_score": round(stats.pstdev(scores), 1),
                "best_score": max(scores),
                "worst_score": min(scores),
                "mean_time_s": round(stats.mean(times), 4),
                "mean_gap_percent": round(stats.mean(gaps), 2),
                "mean_iteration_of_best": round(stats.mean(iters), 1) if iters else "",
            })

    with open(os.path.join(RESULTS_DIR, "summary_table.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0].keys()))
        writer.writeheader()
        writer.writerows(table)
    return table


def build_memory_table():
    """Peak memory (KB) per algorithm and size, DP included."""
    rows = read_csv("memory.csv")
    with open(os.path.join(RESULTS_DIR, "memory_table.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "algorithm", "peak_memory_kb"])
        for size_name in SIZES:
            for algo in ALL_ALGORITHMS:
                for r in rows:
                    if r["algorithm"] == algo and r["size"] == size_name:
                        writer.writerow([size_name, algo, r["peak_memory_kb"]])
    return rows


def plot_convergence(histories, rows):
    """Iteration -> best fitness so far, averaged over runs, with the DP optimum as a reference."""
    for size_name in SIZES:
        plt.figure()
        for algo in ALGORITHMS:
            runs = histories[f"{algo}|{size_name}"]
            length = min(len(h) for h in runs)
            averaged = [stats.mean(h[i] for h in runs) for i in range(length)]
            plt.plot(range(1, length + 1), averaged, label=algo)
        plt.axhline(get_optimum(rows, size_name), color="black", linestyle="--", label="DP optimum")
        plt.title(f"Convergence - {size_name} instance")
        plt.xlabel("Iteration / Generation")
        plt.ylabel("Best fitness so far (averaged over runs)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f"convergence_{size_name}.png"))
        plt.close()


def plot_boxplots(rows):
    """Spread of final scores per algorithm (stability), with the DP optimum as a reference."""
    for size_name in SIZES:
        data = [[float(r["score"]) for r in rows if r["algorithm"] == algo and r["size"] == size_name]
                for algo in ALGORITHMS]
        plt.figure()
        plt.boxplot(data, tick_labels=ALGORITHMS)
        plt.axhline(get_optimum(rows, size_name), color="black", linestyle="--", label="DP optimum")
        plt.title(f"Final score spread - {size_name} instance")
        plt.ylabel("Score")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f"boxplot_{size_name}.png"))
        plt.close()


def plot_runtime_vs_size(rows):
    plt.figure()
    for algo in ALL_ALGORITHMS:
        means = [stats.mean(float(r["time_s"]) for r in rows
                             if r["algorithm"] == algo and r["size"] == size_name)
                 for size_name in SIZES]
        plt.plot(list(SIZES.values()), means, marker="o", label=algo)
    plt.title("Mean runtime vs problem size")
    plt.xlabel("Number of projects (n)")
    plt.ylabel("Mean runtime (s)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "runtime_vs_size.png"))
    plt.close()


def main():
    rows = read_csv("runs.csv")          # includes the DP rows
    histories = load_histories()

    table = build_summary_table(rows)
    print("size    algorithm  runs  mean   std   best   worst  mean_time  mean_gap%  conv_iter")
    for row in table:
        print(f"{row['size']:7s} {row['algorithm']:9s} {row['runs']:4d} "
              f"{row['mean_score']:7.1f} {row['std_score']:5.1f} {row['best_score']:6.0f} "
              f"{row['worst_score']:6.0f} {row['mean_time_s']:9.4f} {row['mean_gap_percent']:9.2f} "
              f"{str(row['mean_iteration_of_best']):>9s}")

    memory = build_memory_table()
    print("\nPeak memory (KB):")
    for size_name in SIZES:
        parts = [f"{r['algorithm']}={float(r['peak_memory_kb']):.0f}"
                 for algo in ALL_ALGORITHMS for r in memory
                 if r["algorithm"] == algo and r["size"] == size_name]
        print(f"  {size_name:7s} " + "  ".join(parts))

    plot_convergence(histories, rows)
    plot_boxplots(rows)
    plot_runtime_vs_size(rows)
    print("\nSaved summary_table.csv, memory_table.csv and all PNG plots to the results/ folder.")


if __name__ == "__main__":
    main()
