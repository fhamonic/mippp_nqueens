"""N-Queens model construction benchmark using gurobipy."""

import json
import sys
import time

# Time the solver API loading
t_api_start = time.perf_counter()
from gurobipy import Model, quicksum, GRB

t_api_end = time.perf_counter()
api_time_ms = (t_api_end - t_api_start) * 1_000


def build_nqueens(n):
    t0 = time.perf_counter()

    queens = Model("queens")
    queens.setParam("OutputFlag", 0)

    x = [
        [
            queens.addVar(name="x({},{})".format(i, j), vtype=GRB.BINARY, obj=-1)
            for j in range(n)
        ]
        for i in range(n)
    ]

    # one per row
    for i in range(n):
        queens.addConstr(
            quicksum(x[i][j] for j in range(n)) == 1,
            name="row({})".format(i),
        )

    # one per column
    for j in range(n):
        queens.addConstr(
            quicksum(x[i][j] for i in range(n)) == 1,
            name="col({})".format(j),
        )

    # diagonal \
    for p, k in enumerate(range(2 - n, n - 2 + 1)):
        queens.addConstr(
            quicksum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1,
            name="diag1({})".format(p),
        )

    # diagonal /
    for p, k in enumerate(range(3, n + n)):
        queens.addConstr(
            quicksum(x[i][j] for i in range(n) for j in range(n) if i + j == k) <= 1,
            name="diag2({})".format(p),
        )

    t1 = time.perf_counter()

    queens.update()
    num_variables = queens.NumVars
    num_constraints = queens.NumConstrs
    model_time_ms = (t1 - t0) * 1_000

    return num_variables, num_constraints, model_time_ms


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    num_variables, num_constraints, model_time_ms = build_nqueens(n)

    result = {
        "solver_name": "Gurobi",
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
