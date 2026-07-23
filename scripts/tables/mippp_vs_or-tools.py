from helper import *


def to_float(N, value):
    return "{:.1f} ms".format(float(value) / 1_000)


def to_first_scale(N, value):
    ref_value = table_data[0][1][0][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))


def to_highs_scale(N, value):
    ref_value = table_data[0][1][1][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))


def to_scip_scale(N, value):
    ref_value = table_data[0][1][2][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))


table_data = [
    (
        "MIP++",
        [
            (
                "Cbc",
                read_col("results/mippp/Cbc_mippp_bulk.csv", "model_time_us"),
                to_float,
            ),
            (
                "HiGHS",
                read_col("results/mippp/Highs_mippp_bulk.csv", "model_time_us"),
                to_float,
            ),
            (
                "SCIP",
                read_col("results/mippp/SCIP_mippp_bulk.csv", "model_time_us"),
                to_float,
            ),
        ],
    ),
    (
        "OR-tools",
        [
            (
                "Cbc",
                read_col("results/or_tools/Cbc.csv", "model_time_us"),
                to_first_scale,
            ),
            (
                "HiGHS",
                read_col("results/or_tools/Highs.csv", "model_time_us"),
                to_highs_scale,
            ),
            (
                "SCIP",
                read_col("results/or_tools/SCIP.csv", "model_time_us"),
                to_scip_scale,
            ),
        ],
    ),
]

print_markdown_table(table_data)
