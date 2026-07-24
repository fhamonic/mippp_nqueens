"""N-Queens model construction benchmark using Python-MIP."""

import json
import sys
import time

# Time the solver API loading
t_api_start = time.perf_counter()
from mip import Model, xsum, BINARY

t_api_end = time.perf_counter()
api_time_ms = (t_api_end - t_api_start) * 1_000


def build_nqueens(n, solver):
    t0 = time.perf_counter()

    queens = Model("queens", solver_name=solver)

    x = [
        [
            queens.add_var("x({},{})".format(i, j), var_type=BINARY, obj=-1.0)
            for j in range(n)
        ]
        for i in range(n)
    ]

    # one per row
    for i in range(n):
        queens.add_constr(xsum(x[i][j] for j in range(n)) == 1, "row({})".format(i))

    # one per column
    for j in range(n):
        queens.add_constr(xsum(x[i][j] for i in range(n)) == 1, "col({})".format(j))

    # diagonal \
    for p, k in enumerate(range(2 - n, n - 2 + 1)):
        queens.add_constr(
            xsum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1,
            "diag1({})".format(p),
        )

    # diagonal /
    for p, k in enumerate(range(3, n + n)):
        queens.add_constr(
            xsum(x[i][j] for i in range(n) for j in range(n) if i + j == k) <= 1,
            "diag2({})".format(p),
        )

    t1 = time.perf_counter()

    num_variables = queens.num_cols
    num_constraints = queens.num_rows
    model_time_ms = (t1 - t0) * 1_000

    return num_variables, num_constraints, model_time_ms


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <solver> <N>")
        exit(1)

    solver = sys.argv[1]
    n = int(sys.argv[2])

    num_variables, num_constraints, model_time_ms = build_nqueens(n, solver)

    result = {
        "solver_name": solver,
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
