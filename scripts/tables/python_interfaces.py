from helper import *


def to_s(N, value):
    v = float(value)
    return "{:.2f} s".format(v / 1000)


table_data = [
    (
        "highspy",
        [("HiGHS", read_col("results/highs/highspy.csv", "model_time_ms"), to_s)],
    ),
    (
        "PuLP",
        [
            (
                "Cbc · CPython",
                read_col("results/pulp/python.csv", "model_time_ms"),
                to_s,
            ),
            ("Cbc · PyPy", read_col("results/pulp/pypy3.csv", "model_time_ms"), to_s),
        ],
    ),
    (
        "Python-MIP",
        [
            (
                "Cbc · CPython",
                read_col("results/python-mip/python_Cbc.csv", "model_time_ms"),
                to_s,
            ),
            (
                "Cbc · PyPy",
                read_col("results/python-mip/pypy3_Cbc.csv", "model_time_ms"),
                to_s,
            ),
        ],
    ),
]

print_markdown_table(table_data)
