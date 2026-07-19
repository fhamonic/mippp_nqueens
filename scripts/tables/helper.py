def read_col(file, col):
    with open(file, "r") as f:
        lines = list(f.read().split("\n"))
        col_id = lines[0].split(",").index(col)
        return {line.split(",")[0]: line.split(",")[col_id] for line in lines[1:-1]}


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
                read_col("results/mippp/Highs_mippp_bulk.csv", "model_time_us"),
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
    (
        "Python-MIP",
        [
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
                "Cbc (Pypy)",
                read_col("results/pulp/pypy.csv", "model_time_s"),
                to_us_cbc_scale,
            ),
        ],
    ),
]


def print_latex_table(table_data):
    print(
        """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|"""
        + "|".join(["r" * len(c[1]) for c in table_data])
        + """}
    \multirow{2}{*}{N} & """
        + " & ".join(
            [
                (
                    "\multirow{2}{*}{" + c[0] + "}"
                    if len(c[1]) == 1 and c[1][0][0] == ""
                    else "\\multicolumn{" + str(len(c[1])) + "}{c}{" + c[0] + "}"
                )
                for c in table_data
            ]
        )
        + """\\tabularnewline
    & """
        + " & ".join([sc[0] for c in table_data for sc in c[1]])
        + """\\tabularnewline
    \\hline"""
    )
    for N in table_data[0][1][0][1].keys():
        print(
            f"    {N} & "
            + " & ".join([sc[2](N, sc[1][N]) for c in table_data for sc in c[1]]),
            end="\\tabularnewline\n",
        )
    print("""  \\end{tabular}
\\end{table*}""")


def print_markdown_table(table_data):
    cols = [(c[0], sc) for c in table_data for sc in c[1]]
    header = ["N"] + [
        (
            group
            if (len([x for x in cols if x[0] == group]) == 1 and sc[0] == "")
            else f"{group}<br>{sc[0]}"
        )
        for group, sc in cols
    ]
    print("| " + " | ".join(header) + " |")
    print("|" + ":---:|" + "---:|" * len(cols))
    for N in table_data[0][1][0][1].keys():
        print(f"| {N} | " + " | ".join([sc[2](N, sc[1][N]) for _, sc in cols]) + " |")
