import json
import sys
import time

# Time the solver API loading (equivalent to mippp's api construction / dlopen)
t_api_start = time.perf_counter()
import highspy

t_api_end = time.perf_counter()
api_time_ms = (t_api_end - t_api_start) * 1_000


def build_nqueens(n):
    h = highspy.Highs()
    h.silent()

    t0 = time.perf_counter()

    # N² binary variables
    for i in range(n * n):
        h.addVar(0, 1)
        h.changeColIntegrality(i, highspy.HighsVarType.kInteger)

    indices = range(n)

    # One queen per row
    for row in indices:
        cols = [row * n + col for col in indices]
        vals = [1.0] * n
        h.addRow(1.0, 1.0, n, cols, vals)

    # One queen per column
    for col in indices:
        cols = [row * n + col for row in indices]
        vals = [1.0] * n
        h.addRow(1.0, 1.0, n, cols, vals)

    # Diagonal constraints (4 families, each <= 1)
    for top_col in range(n - 1):
        length = n - top_col
        cols = [row * n + (top_col + row) for row in range(length)]
        vals = [1.0] * length
        h.addRow(-highspy.kHighsInf, 1.0, length, cols, vals)

    for left_row in range(1, n - 1):
        length = n - left_row
        cols = [(left_row + col) * n + col for col in range(length)]
        vals = [1.0] * length
        h.addRow(-highspy.kHighsInf, 1.0, length, cols, vals)

    for left_row in range(1, n):
        length = left_row + 1
        cols = [(left_row - col) * n + col for col in range(length)]
        vals = [1.0] * length
        h.addRow(-highspy.kHighsInf, 1.0, length, cols, vals)

    for bottom_col in range(1, n - 1):
        length = n - bottom_col
        cols = [(n - 1 - (col - bottom_col)) * n + col for col in range(bottom_col, n)]
        vals = [1.0] * length
        h.addRow(-highspy.kHighsInf, 1.0, length, cols, vals)

    t1 = time.perf_counter()

    num_variables = h.getNumCol()
    num_constraints = h.getNumRow()
    model_time_ms = (t1 - t0) * 1_000

    return num_variables, num_constraints, model_time_ms


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <N>")
        exit(1)

    n = int(sys.argv[1])

    num_variables, num_constraints, model_time_ms = build_nqueens(n)

    result = {
        "solver_name": "HiGHS",
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
