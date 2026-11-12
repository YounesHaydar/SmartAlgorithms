# Comparing GA, PSO and ACO on a Project-Funding (0/1 Knapsack) Problem

University project (HW_F25). We compare three metaheuristics, a Genetic Algorithm (GA),
Particle Swarm Optimization (PSO) and Ant Colony Optimization (ACO), on a resource allocation
problem, using Dynamic Programming (DP) as an exact baseline.

## The problem

A department has a fixed budget and `n` candidate projects. Each project `i` has a benefit
`value[i]` and a cost `weight[i]`. We choose which projects to fund to **maximize total value**
without the total cost exceeding the budget (`capacity`). This is the 0/1 Knapsack problem.

- **Solution representation:** a list of `n` bits, where `x[i] = 1` means project `i` is funded.
- **Objective (fitness):** the total value of the funded projects, or 0 if the budget is exceeded.
- **Instances:** generated randomly with a fixed seed (values 1 to 100, weights 1 to 50, capacity = 40% of total weight).
- **Sizes:** small (n = 20), medium (n = 100), large (n = 500).

## Project structure

```
problem.py           problem definition: instance generator and fitness function
dp.py                Dynamic Programming: exact optimum (baseline)
ga.py                Genetic Algorithm
pso.py               Binary Particle Swarm Optimization
aco.py               Ant Colony Optimization
run_experiments.py   runs every algorithm on every size, many times, and saves raw results
analyze.py           turns the raw results into tables and plots
requirements.txt     Python dependencies
results/             generated outputs (created when you run the scripts)
```

## How to run

Requires **Python 3.10 or newer** (developed and tested on Python 3.12).

```bash
# 1. (recommended) create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows (cmd)
# source venv/bin/activate       # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. run the experiments (30 runs per algorithm and size)
python run_experiments.py
#    for a fast check with 3 runs per case:
python run_experiments.py --quick

# 4. generate the tables and plots
python analyze.py
```

Each algorithm file can also be run on its own (for example `python ga.py`); it prints its
result and the gap to the DP optimum for the three sizes.

## Outputs (in `results/`)

| File | Contents |
|---|---|
| `runs.csv` | one row per run: score, gap to optimum, time, iteration where the best was found |
| `memory.csv` | peak memory of one run per algorithm and size |
| `histories.json` | best score after every iteration, for every run |
| `summary_table.csv` | mean, std, best, worst score, mean time, mean gap, mean convergence iteration (DP included) |
| `memory_table.csv` | peak memory per algorithm and size (DP included) |
| `convergence_<size>.png` | Iteration → Best Fitness curves, with the DP optimum as a dashed line |
| `boxplot_<size>.png` | spread of final scores across runs (stability) |
| `runtime_vs_size.png` | how runtime grows with problem size |

## Metrics

| Criterion | How it is measured |
|---|---|
| Solution quality | final score, and **gap (%)** to the DP optimum: `100 × (optimum − score) / optimum` |
| Execution time | wall-clock seconds per run (`time.perf_counter`) |
| Resource use | peak memory in KB (`tracemalloc`), measured in a separate run so it does not distort timing |
| **Convergence speed** | see below |
| Stability | standard deviation, best and worst score, and boxplots over 30 runs |

### Convergence speed

Convergence speed tells us how quickly an algorithm reaches its final answer. We measure it in two ways:

1. **Convergence curves** (`convergence_<size>.png`). Every algorithm records its best score so far
   after each iteration (the `history` it returns). The plot shows this history averaged over all runs,
   with the DP optimum as a dashed reference line. A curve that rises early and flattens is fast. A curve
   that keeps rising until the end is still improving.
2. **Convergence iteration** (`mean_iteration_of_best` in `summary_table.csv`). For each run, this is the
   **first iteration at which the run's final best score was reached**, averaged over runs. A **lower
   number means faster convergence**.

How to read the convergence iteration:

- It measures *when the final result was first found*, not how good that result is. Always read it next to
  the score and gap. An algorithm can stop improving early at a poor score (early stagnation).
- A value close to the total number of iterations (200) means the algorithm was still improving when it
  stopped, so more iterations might help.
- DP has no iterations, so its convergence entry is empty.
- All three algorithms use the same iteration count (200), so the values are directly comparable.

## Algorithms and hyperparameters

All three heuristics use the same evaluation budget (about 20,000 fitness evaluations) so the comparison is fair.
Every algorithm takes the same input `(values, weights, capacity)` and returns the best solution, its score,
and the per-iteration history. The stopping criterion for all three is a **fixed number of iterations (200)**.

| Algorithm | Mechanism | Hyperparameters (defaults used) |
|---|---|---|
| **GA** | tournament selection, one-point crossover, bit-flip mutation, elitism, repair of over-budget solutions | population 100, generations 200, crossover rate 0.9, mutation rate 1/n, tournament size 3, elite 2 |
| **PSO** | binary PSO: velocity pulled toward personal and global best, sigmoid turns velocity into the probability of a bit being 1, repair | swarm 100, iterations 200, inertia w 0.7, c1 1.5, c2 1.5, velocity limit 4.0 |
| **ACO** | ants build solutions guided by pheromone and the value/weight ratio, evaporation plus reinforcement of the iteration's best solution | ants 100, iterations 200, alpha 1.0, beta 2.0, evaporation rho 0.1, pheromone bounds 0.05 to 1.0 |
| **DP** (baseline) | exact table over budgets, `O(n × capacity)` | none |

**Constraint handling.** Random or recombined solutions can exceed the budget. GA and PSO use a `repair` step
(`ga.py`) that removes random funded projects until the solution fits. ACO ants only add projects that still
fit, so they need no repair.

## Reproducibility

- The problem instance is generated with a fixed seed (`INSTANCE_SEED = 42` in `run_experiments.py`), so
  every algorithm is tested on identical data.
- Run `k` of each algorithm uses seed `k`, so re-running gives the same results.
- Raw per-run data is saved in `results/`, so `analyze.py` can be re-run without repeating the experiments.

## Team contributions

<!-- Fill in with each member's real contribution. The brief requires this section. -->

| Member | Contribution |
|---|---|
| [Name] | [e.g. problem definition and DP baseline] |
| [Name] | [e.g. Genetic Algorithm] |
| [Name] | [e.g. PSO] |
| [Name] | [e.g. ACO] |
| [Name] | [e.g. experiments and plots] |
| [Name] | [e.g. report and README] |
