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


# The OR-Tools columns are the `_setcoef` variants: same model built with
# MakeRowConstraint + SetCoefficient / AddLinearConstraint + set_coefficient
# rather than with an expression object, which is the faster of the two forms
# both APIs offer. See `or-tools_modes.py` for the two side by side.

mippp_cbc = read_col("results/mippp/Cbc_distinct.csv", "model_time_ms")
mippp_highs = read_col("results/mippp/Highs_distinct.csv", "model_time_ms")
mippp_scip = read_col("results/mippp/SCIP_distinct.csv", "model_time_ms")
mippp_xpress = read_col("results/mippp/Xpress_distinct.csv", "model_time_ms")

table_data = [
    (
        "MIP++",
        [
            ("Cbc", mippp_cbc, to_ms),
            ("HiGHS", mippp_highs, to_ms),
            ("SCIP", mippp_scip, to_ms),
            ("Xpress", mippp_xpress, to_ms),
        ],
    ),
    (
        "MPSolver",
        [
            (
                "Cbc",
                read_col("results/or-tools/Cbc_mpsolver_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_cbc),
            ),
            (
                "HiGHS",
                read_col("results/or-tools/Highs_mpsolver_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_highs),
            ),
            (
                "SCIP",
                read_col("results/or-tools/SCIP_mpsolver_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_scip),
            ),
            (
                "Xpress",
                read_col("results/or-tools/Xpress_mpsolver_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_xpress),
            ),
        ],
    ),
    (
        "MathOpt",
        [
            (
                "HiGHS",
                read_col("results/or-tools/Highs_mathopt_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_highs),
            ),
            (
                "SCIP",
                read_col("results/or-tools/SCIP_mathopt_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_scip),
            ),
            (
                "Xpress",
                read_col("results/or-tools/Xpress_mathopt_setcoef.csv", "model_time_ms"),
                percentage_to(mippp_xpress),
            ),
        ],
    ),
]

print_markdown_table(table_data)
