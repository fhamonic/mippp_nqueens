from helper import *

# ["Cbc", "COPT", "CPLEX", "GLPK", "Gurobi", "Highs", "MOSEK", "SCIP", "Xpress"]
SOLVER = "Cbc"


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


table_data = [
    (
        "MIP++ · " + SOLVER,
        [
            (
                "one-at-a-time",
                read_col(f"results/mippp/{SOLVER}.csv", "model_time_ms"),
                to_ms,
            ),
            (
                "+ distinct",
                read_col(f"results/mippp/{SOLVER}_distinct.csv", "model_time_ms"),
                to_ms,
            ),
            (
                "bulk",
                read_col(f"results/mippp/{SOLVER}_bulk.csv", "model_time_ms"),
                to_ms,
            ),
            (
                "bulk + distinct",
                read_col(f"results/mippp/{SOLVER}_bulk_distinct.csv", "model_time_ms"),
                to_ms,
            ),
        ],
    ),
]

print_markdown_table(table_data)
