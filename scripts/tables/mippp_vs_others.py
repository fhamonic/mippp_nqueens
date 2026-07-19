from helper import *


def to_float(N, value):
    return "{:.1f} ms".format(float(value) / 1_000)


def to_cbc_scale(N, value):
    ref_value = table_data[0][1][0][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))


def to_us_cbc_scale(N, value):
    return to_cbc_scale(N, float(value) * 1_000_000)


def to_highs_scale(N, value):
    ref_value = table_data[0][1][1][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))


table_data = [
    (
        "MIP++",
        [
            (
                "Cbc",
                read_col("results/mippp/Cbc_mippp.csv", "model_time_us"),
                to_float,
            ),
            (
                "HiGHS",
                read_col("results/mippp/Highs_mippp.csv", "model_time_us"),
                to_float,
            ),
        ],
    ),
    (
        "OR-tools",
        [
            (
                "Cbc",
                read_col("results/or_tools/Cbc_or_tools.csv", "model_time_us"),
                to_cbc_scale,
            ),
            (
                "HiGHS",
                read_col("results/or_tools/Highs_or_tools.csv", "model_time_us"),
                to_highs_scale,
            ),
        ],
    ),
    (
        "JuMP",
        [
            (
                "Cbc",
                read_col("results/jump/Cbc_jump.csv", "model_time_us"),
                to_cbc_scale,
            ),
            (
                "HiGHS",
                read_col("results/jump/Highs_jump.csv", "model_time_us"),
                to_highs_scale,
            ),
        ],
    ),
]

print_markdown_table(table_data)
