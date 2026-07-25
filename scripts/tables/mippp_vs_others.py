from helper import *


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


def scale_to(ref_col):
    def f(N, value):
        ref = float(ref_col[N])
        return "—" if ref == 0 else "{:.1f} x".format(float(value) / ref)

    return f


mippp_cbc = read_col("results/mippp/Cbc_distinct.csv", "model_time_ms")
mippp_highs = read_col("results/mippp/Highs_distinct.csv", "model_time_ms")

table_data = [
    (
        "MIP++",
        [
            ("Cbc", mippp_cbc, to_ms),
            ("HiGHS", mippp_highs, to_ms),
        ],
    ),
    (
        "OR-tools",
        [
            (
                "Cbc",
                read_col("results/or_tools/Cbc.csv", "model_time_ms"),
                scale_to(mippp_cbc),
            ),
            (
                "HiGHS",
                read_col("results/or_tools/Highs.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
        ],
    ),
    (
        "JuMP",
        [
            (
                "Cbc",
                read_col("results/jump/Cbc.csv", "model_time_ms"),
                scale_to(mippp_cbc),
            ),
            (
                "HiGHS",
                read_col("results/jump/Highs.csv", "model_time_ms"),
                scale_to(mippp_highs),
            ),
        ],
    ),
]

print_markdown_table(table_data)
