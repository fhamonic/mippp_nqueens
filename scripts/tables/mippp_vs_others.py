from helper import *

# HiGHS is the only backend all four interfaces provide: MathOpt has no Cbc, and
# JuMP's direct mode needs an incrementally modifiable backend, which the Cbc
# wrapper is not. Cbc and SCIP are covered in the OR-Tools table.


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


def scale_to(ref_col):
    def f(N, value):
        ref = float(ref_col[N])
        return "—" if ref == 0 else "{:.1f} x".format(float(value) / ref)

    return f


mippp_highs = read_col("results/mippp/Highs_distinct.csv", "model_time_ms")

table_data = [
    (
        "MIP++",
        [("", mippp_highs, to_ms)],
    ),
    (
        "OR-tools",
        [
            (
                "MPSolver",
                read_col("results/or-tools/Highs_mpsolver_setcoef.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
            (
                "MathOpt",
                read_col("results/or-tools/Highs_mathopt_setcoef.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
        ],
    ),
    (
        "JuMP",
        [
            (
                "cached",
                read_col("results/jump/Highs_cached.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
            (
                "direct",
                read_col("results/jump/Highs_direct.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
        ],
    ),
]

print_markdown_table(table_data)
