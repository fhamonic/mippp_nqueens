from helper import *


def to_float(N, value):
    return "{:.1f} ms".format(float(value) / 1_000)


def to_first_scale(N, value):
    ref_value = table_data[0][1][0][1][N]
    return "{:.1f} x".format(float(value) / float(ref_value))

def to_us_first_scale(N, value):
    ref_value = table_data[0][1][0][1][N]
    return "{:.1f} x".format(float(value) * 1e6 / float(ref_value))


def to_first_percent(N, value):
    ref_value = table_data[0][1][0][1][N]
    return "{:.1f} %".format(float(value) / float(ref_value) * 100)


table_data = [
    (
        "pure C API",
        [
            (
                "",
                read_col("results/gurobi/gurobi_c.csv", "model_time_us"),
                to_float,
            )
        ],
    ),
    (
        "MIP++",
        [
            (
                "",
                read_col("results/mippp/Gurobi_mippp.csv", "model_time_us"),
                to_first_percent,
            )
        ],
    ),
    (
        "JuMP",
        [
            (
                "(cold)",
                read_col("results/jump/Gurobi.csv", "cold_model_time_us"),
                to_first_scale,
            ),
            (
                "(warm)",
                read_col("results/jump/Gurobi.csv", "model_time_us"),
                to_first_scale,
            )
        ],
    ),
    (
        "Python-MIP",
        [
            (
                "CPython",
                read_col("results/python-mip/gurobi_cpython.csv", "model_time_s"),
                to_us_first_scale,
            ),
            (
                "Pypy",
                read_col("results/python-mip/gurobi_pypy.csv", "model_time_s"),
                to_us_first_scale,
            )
        ],
    ),
    (
        "GurobiPy",
        [
            (
                "",
                read_col("results/gurobi/gurobipy.csv", "model_time_s"),
                to_us_first_scale,
            )
        ],
    ),
]

print_markdown_table(table_data)
