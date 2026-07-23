def read_col(file, col):
    with open(file, "r") as f:
        lines = list(f.read().split("\n"))
        col_id = lines[0].split(",").index(col)
        return {line.split(",")[0]: line.split(",")[col_id] for line in lines[1:-1]}


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
            else f"<div align=\"center\">{group}<br>{sc[0]}</div>"
        )
        for group, sc in cols
    ]
    print("| " + " | ".join(header) + " |")
    print("|" + ":---:|" + "---:|" * len(cols))
    for N in table_data[0][1][0][1].keys():
        print(f"| {N} | " + " | ".join([sc[2](N, sc[1][N]) for _, sc in cols]) + " |")
