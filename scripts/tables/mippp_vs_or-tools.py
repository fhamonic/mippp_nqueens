from helper import *


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


def scale_to(ref_col):
    def f(N, value):
        ref = float(ref_col[N])
        return "—" if ref == 0 else "{:.1f} x".format(float(value) / ref)

    return f


def percentage_to(ref_col):
    def f(N, value):
        ref = float(ref_col[N])
        return "—" if ref == 0 else "{:.0f} %".format(float(value) / ref * 100)

    return f


mippp_cbc = read_col("results/mippp/Cbc_distinct.csv", "model_time_ms")
mippp_highs = read_col("results/mippp/Highs_distinct.csv", "model_time_ms")
mippp_scip = read_col("results/mippp/SCIP_distinct.csv", "model_time_ms")

table_data = [
    (
        "MIP++",
        [
            ("Cbc", mippp_cbc, to_ms),
            ("HiGHS", mippp_highs, to_ms),
            ("SCIP", mippp_scip, to_ms),
        ],
    ),
    (
        "OR-tools (MPSolver)",
        [
            (
                "Cbc",
                read_col("results/or-tools/Cbc_mpsolver.csv", "model_time_ms"),
                percentage_to(mippp_cbc),
            ),
            (
                "HiGHS",
                read_col("results/or-tools/Highs_mpsolver.csv", "model_time_ms"),
                percentage_to(mippp_highs),
            ),
            (
                "SCIP",
                read_col("results/or-tools/SCIP_mpsolver.csv", "model_time_ms"),
                percentage_to(mippp_scip),
            ),
        ],
    ),
    (
        "OR-tools (MathOpt)",
        [
            (
                "HiGHS",
                read_col("results/or-tools/Highs_mathopt.csv", "model_time_ms"),
                percentage_to(mippp_highs),
            ),
            (
                "SCIP",
                read_col("results/or-tools/SCIP_mathopt.csv", "model_time_ms"),
                percentage_to(mippp_scip),
            ),
        ],
    ),
]

print_markdown_table(table_data)
