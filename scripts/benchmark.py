import subprocess
import itertools


def call_executable(executable_path, arg1, arg2):
    try:
        process = subprocess.run(
            [executable_path, arg1, arg2],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return process.stderr.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr.strip())


if __name__ == "__main__":
    executable = "./build/nqueens"
    solvers = ["Cbc", "CPLEX", "Gurobi", "Highs", "MOSEK", "SCIP"]
    values = [str(v) for v in range(100, 1001, 100)]

    print(f"N", end="")
    for solver in solvers:
        print(f" | {solver}", end="")
    print()
    for value in values:
        print(f"{value}", end="")
        for solver in solvers:
            result = call_executable(executable, solver, value).split(",")
            print(f" | {result[3]}", end="")
        print()
