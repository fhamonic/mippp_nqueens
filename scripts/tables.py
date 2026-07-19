import os

results_dir = "results"

# produced by scripts/benchmark_python.sh
python_mip_results_dir = os.path.join(results_dir, "python-mip")
python_mip_benchmarks = [
    os.path.join(python_mip_results_dir, f)
    for f in [
        "queens-pulp-cpython.csv",
        "queens-pulp-pypy.csv",
        "queens-gurobi-cpython.csv",
        "queens-mip-cbc-pypy.csv",
        "queens-mip-grb-pypy.csv",
        "queens-mip-cbc-cpython.csv",
        "queens-mip-grb-cpython.csv",
    ]
]


def read_result(file):
    with open(file, "r") as f:
        lines = list(f.read().split("\n")[:-1])
        return {int(line.split(",")[0]): float(line.split(",")[-1]) for line in lines}


if __name__ == "__main__":
    files = filter(
        lambda f: os.path.isfile(os.path.join(results_dir, f)),
        os.listdir(results_dir),
    )
    results = {
        file[:-4]: read_result(os.path.join(results_dir, file)) for file in files
    }
    Ns = list(list(results.values())[0].keys())
    results.update(
        {
            # strips the "queens-" prefix and the ".csv" extension
            os.path.basename(file)[7:-4]: {
                N: 1000 * t for N, t in read_result(file).items()
            }
            for file in python_mip_benchmarks
            if os.path.isfile(file)
        }
    )
    jump_file = os.path.join(python_mip_results_dir, "queens-jump.csv")
    if os.path.isfile(jump_file):
        results["jump-grb"] = read_result(jump_file)

    cols = [
        "Gurobi_c",
        "Gurobi_c_bulk",
        "Gurobi_mippp",
        "Gurobi_mippp_bulk",
        "gurobi-cpython",
        "mip-grb-cpython",
        "mip-grb-pypy",
        "jump-grb",
    ]

    # skipped when the python-mip/JuMP result files are not on this machine
    if all(c in results for c in cols):
        print(
            """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|rr|rr|r|rr|r}
    \multirow{2}{*}{N} & \\multicolumn{2}{c}{C} & \\multicolumn{2}{c}{MIP++} & GyrobiPy & \\multicolumn{2}{c}{Python-MIP} & \\multirow{2}{*}{JuMP}\\tabularnewline
    & naive & bulk & naive & bulk & CPython & CPython & Pypy &\\tabularnewline
    \\hline"""
        )
        for N in Ns:
            print(f"{N} & ", end="")
            # print(" & ".join(map(lambda x: f"{results[x][N]:.2f}", cols)), end="")
            ref = results[cols[0]][N]
            print(f"{ref:.2f} ms & ", end="")
            print(
                " & ".join(map(lambda x: f"{results[x][N]/ref:.1f} x", cols[1:])),
                end="",
            )
            print("\\tabularnewline")
        print(
            """  \\end{tabular}
\\end{table*}"""
        )

    ortools_backends = [
        b for b in ["Cbc", "SCIP", "Gurobi", "Highs"] if f"{b}_or_tools" in results
    ]
    if ortools_backends:
        print(
            """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|"""
            + "|".join(["rrr"] * len(ortools_backends))
            + """}
    \\multirow{2}{*}{N} & """
            + " & ".join(
                f"\\multicolumn{{3}}{{c}}{{{b}}}" for b in ortools_backends
            )
            + """\\tabularnewline
    & """
            + " & ".join(["MIP++ & bulk & OR-Tools"] * len(ortools_backends))
            + """\\tabularnewline
    \\hline"""
        )
        for N in Ns:
            print(f"{N}", end="")
            for b in ortools_backends:
                ref = results[f"{b}_mippp"][N]
                print(f" & {ref:.2f} ms", end="")
                print(f" & {results[f'{b}_mippp_bulk'][N]/ref:.1f} x", end="")
                print(f" & {results[f'{b}_or_tools'][N]/ref:.1f} x", end="")
            print("\\tabularnewline")
        print(
            """  \\end{tabular}
\\end{table*}"""
        )

    cols = [
        "Cbc_mippp",
        "Cbc_mippp_bulk",
        "mip-cbc-cpython",
        "mip-cbc-pypy",
        "pulp-cpython",
        "pulp-pypy",
    ]

    # skipped when the python-mip result files are not on this machine
    if all(c in results for c in cols):
        print(
            """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|rr|rr|rr}
    \multirow{2}{*}{N} & \\multicolumn{2}{c}{MIP++} & \\multicolumn{2}{c}{Python-MIP} & \\multicolumn{2}{c}{PuLP}\\tabularnewline
    & naive & bulk & CPython & Pypy & CPython & Pypy\\tabularnewline
    \\hline"""
        )
        for N in Ns:
            print(f"{N} & ", end="")
            # print(" & ".join(map(lambda x: f"{results[x][N]:.2f}", cols)), end="")
            ref = results[cols[0]][N]
            print(f"{ref:.2f} ms & ", end="")
            print(
                " & ".join(map(lambda x: f"{results[x][N]/ref:.1f} x", cols[1:])),
                end="",
            )
            print("\\tabularnewline")
        print(
            """  \\end{tabular}
\\end{table*}"""
        )
