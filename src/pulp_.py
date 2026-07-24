"""N-Queens model construction benchmark using PuLP."""

import json
import sys
import time

# Time the solver API loading
t_api_start = time.perf_counter()
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

t_api_end = time.perf_counter()
api_time_ms = (t_api_end - t_api_start) * 1_000


def build_nqueens(n):
    t0 = time.perf_counter()

    queens = LpProblem("queens", LpMinimize)

    x = [
        [LpVariable("x({},{})".format(i, j), 0, 1, "Binary") for j in range(n)]
        for i in range(n)
    ]

    # one per row
    for i in range(n):
        queens += lpSum(x[i][j] for j in range(n)) == 1, "row({})".format(i)

    # one per column
    for j in range(n):
        queens += lpSum(x[i][j] for i in range(n)) == 1, "col({})".format(j)

    # diagonal \
    for p, k in enumerate(range(2 - n, n - 2 + 1)):
        queens += (
            lpSum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1,
            "diag1({})".format(p),
        )

    # diagonal /
    for p, k in enumerate(range(3, n + n)):
        queens += (
            lpSum(x[i][j] for i in range(n) for j in range(n) if i + j == k) <= 1,
            "diag2({})".format(p),
        )

    t1 = time.perf_counter()

    num_variables = queens.numVariables()
    num_constraints = queens.numConstraints()
    model_time_ms = (t1 - t0) * 1_000

    return num_variables, num_constraints, model_time_ms


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <N>")
        exit(1)

    n = int(sys.argv[1])

    num_variables, num_constraints, model_time_ms = build_nqueens(n)

    result = {
        "solver_name": "PuLP",
        "N": n,
        "num_variables": num_variables,
        "num_constraints": num_constraints,
        "api_time_ms": api_time_ms,
        "model_time_ms": model_time_ms,
    }
    json.dump(result, sys.stderr, indent=4)
    sys.stderr.write("\n")


if __name__ == "__main__":
    main()
