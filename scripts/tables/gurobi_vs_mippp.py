from helper import *

c_api = read_col("results/gurobi/gurobi_c.csv", "model_time_ms")


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


def to_c_percent(N, value):
    return "{:.1f} %".format(float(value) / float(c_api[N]) * 100)


def to_c_scale(N, value):
    return "{:.1f} x".format(float(value) / float(c_api[N]))


table_data = [
    (
        "Gurobi C API",
        [("", c_api, to_ms)],
    ),
    (
        "MIP++",
        [
            (
                "",
                read_col("results/mippp/Gurobi_distinct.csv", "model_time_ms"),
                to_c_percent,
            )
        ],
    ),
    (
        "gurobipy",
        [("", read_col("results/gurobi/gurobipy.csv", "model_time_ms"), to_c_scale)],
    ),
    (
        "JuMP",
        [
            ("warm", read_col("results/jump/Gurobi.csv", "model_time_ms"), to_c_scale),
            (
                "cold",
                read_col("results/jump/Gurobi.csv", "cold_model_time_ms"),
                to_c_scale,
            ),
        ],
    ),
    (
        "Python-MIP",
        [
            (
                "CPython",
                read_col("results/python-mip/python_Gurobi.csv", "model_time_ms"),
                to_c_scale,
            ),
            (
                "PyPy",
                read_col("results/python-mip/pypy3_Gurobi.csv", "model_time_ms"),
                to_c_scale,
            ),
        ],
    ),
]

print_markdown_table(table_data)
