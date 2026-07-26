from helper import *

# Every backend a MIP++ build was found for at runtime. One-at-a-time
# (`mippp`), the one variant available for all of them: the GLPK backend aborts
# in `mippp_distinct`.
SOLVERS = ["Cbc", "MOSEK", "Highs", "CPLEX", "Gurobi", "GLPK", "SCIP"]
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
