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
        "JuMP",
        [
            (
                "Cbc",
                read_col("results/jump/Cbc_jump.csv", "model_time_us"),
                to_float,
            ),
            (
                "HiGHS",
                read_col("results/jump/Highs_jump.csv", "model_time_us"),
                to_float,
            ),
        ],
    ),
    (
        "Python-MIP",
        [
            (
                "Cbc (CPython)",
                read_col("results/python-mip/cbc_cpython.csv", "model_time_s"),
                to_us_cbc_scale,
            ),
            (
                "Cbc (Pypy)",
                read_col("results/python-mip/cbc_pypy.csv", "model_time_s"),
                to_us_cbc_scale,
            ),
        ],
    ),
    (
        "PuLP",
        [
            (
                "Cbc (CPython)",
                read_col("results/pulp/cpython.csv", "model_time_s"),
                to_us_cbc_scale,
            ),
            (
                "Cbc (Pypy)",
                read_col("results/pulp/pypy.csv", "model_time_s"),
                to_us_cbc_scale,
            ),
        ],
    ),
]

print_markdown_table(table_data)
