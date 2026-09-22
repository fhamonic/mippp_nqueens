from helper import *

# What each axis is worth per backend, at the largest model of the sweep.
N = "1000"
SOLVERS = ["Cbc", "MOSEK", "COPT", "Highs", "CPLEX", "Gurobi", "GLPK", "Xpress", "SCIP"]
LABELS = {"Highs": "HiGHS"}
VARIANTS = ["_distinct", "_bulk", "_bulk_distinct"]


def read_variant(solver, variant):
    try:
        return read_col(f"results/mippp/{solver}{variant}.csv", "model_time_ms")[N]
    except FileNotFoundError:
        return None  # no such build: the runner skipped it


rows = []
for solver in SOLVERS:
    base = float(read_variant(solver, ""))
    cells = [LABELS.get(solver, solver), "{:.1f} ms".format(base)]
    for variant in VARIANTS:
        value = read_variant(solver, variant)
        cells.append("—" if value is None else "{:.0f} %".format(100 * float(value) / base))
    rows.append(cells)

print_markdown_grid(
    ["backend", "one-at-a-time", "+ distinct", "bulk", "bulk + distinct"], rows
)
