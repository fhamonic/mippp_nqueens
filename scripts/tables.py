import os

results_dir = "results"

python_mip_benchmarks = [
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-pulp-cpython.csv",
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-gurobi-cpython.csv",
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-mip-cbc-pypy.csv",
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-mip-grb-pypy.csv",
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-mip-cbc-cpython.csv",
    "/home/plaiseek/Softwares/python-mip/benchmarks/queens-mip-grb-cpython.csv",
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
            file[54:-4]: {N: 1000 * t for N, t in read_result(file).items()}
            for file in python_mip_benchmarks
        }
    )
    results["jump-grb"] = read_result("/home/plaiseek/Softwares/python-mip/benchmarks/JuMP/result.csv")

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

    print(
        """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|rr|rr|r|r}
    \multirow{2}{*}{N} & \\multicolumn{2}{c}{C} & \\multicolumn{2}{c}{MIP++} & GyrobiPy & \\multicolumn{2}{c}{Python-MIP} & \multirow{2}{*}{JuMP}\\tabularnewline
    & naive & bulk & naive & bulk & CPython & CPython & Pypy &\\tabularnewline
    \\hline
"""
    )
    for N in Ns:
        print(f"{N} & ", end="")
        # print(" & ".join(map(lambda x: f"{results[x][N]:.2f}", cols)), end="")
        ref = results[cols[0]][N]
        print(f"{ref:.2f} ms & ", end="")
        print(" & ".join(map(lambda x: f"{results[x][N]/ref:.1f} x", cols[1:])), end="")
        print("\\tabularnewline")
    print(
        """
  \\end{tabular}
\\end{table*}"""
    )

    cols = [
        "Cbc_mippp",
        "Cbc_mippp_bulk",
        "mip-cbc-cpython",
        "mip-cbc-pypy",
        "pulp-cpython",
    ]

    print(
        """\\begin{table*}[!ht]
  \\centering
  \\begin{tabular}{c|rr|rr|r}
    \multirow{2}{*}{N} & \\multicolumn{2}{c}{MIP++} & \\multicolumn{2}{c}{Python-MIP} & \multirow{2}{*}{PuLP}\\tabularnewline
    & naive & bulk & CPython & Pypy &\\tabularnewline
    \\hline
"""
    )
    for N in Ns:
        print(f"{N} & ", end="")
        # print(" & ".join(map(lambda x: f"{results[x][N]:.2f}", cols)), end="")
        ref = results[cols[0]][N]
        print(f"{ref:.2f} ms & ", end="")
        print(" & ".join(map(lambda x: f"{results[x][N]/ref:.1f} x", cols[1:])), end="")
        print("\\tabularnewline")
    print(
        """
  \\end{tabular}
\\end{table*}"""
    )
