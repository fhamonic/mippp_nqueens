from helper import *

# `Model(optimizer)` keeps a CachingOptimizer and the bridge layer in front of
# the solver; `direct_model(optimizer())` writes straight into the solver's own
# model. Warm times, i.e. a rebuild in an already compiled process.


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


table_data = [
    (
        solver_label,
        [
            (
                mode,
                read_col(f"results/jump/{solver}_{mode}.csv", "model_time_ms"),
                to_ms,
            )
            for mode in ["cached", "direct"]
        ],
    )
    for solver, solver_label in [("Highs", "JuMP · HiGHS"), ("Gurobi", "JuMP · Gurobi")]
]

print_markdown_table(table_data)
