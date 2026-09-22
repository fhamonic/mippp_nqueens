from helper import *

# Every backend a MIP++ build was found for at runtime, in the one-at-a-time
# variant with no hint (`mippp`), so that the column measures the backend
# rather than the `distinct_variables` hint.
SOLVERS = ["Cbc", "MOSEK", "COPT", "Highs", "CPLEX", "Gurobi", "GLPK", "Xpress", "SCIP"]
LABELS = {"Highs": "HiGHS"}


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


table_data = [
    (
        LABELS.get(solver, solver),
        [("", read_col(f"results/mippp/{solver}.csv", "model_time_ms"), to_ms)],
    )
    for solver in SOLVERS
]

print_markdown_table(table_data)
