from helper import *
import os
from statistics import mean


def cmd(args):
    return ["./build/" + args[0], args[1], str(args[2])]


def repetitions(args) -> int:
    reps = int(5000 / args[2])
    reps = min(reps, 50)
    return max(reps, 5)


def to_row(results: list):
    return {
        "N": int(results[0]["N"]),
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "api_time_ms": mean(r["api_time_ms"] for r in results),
        "model_time_ms": mean(r["model_time_ms"] for r in results),
    }


results_dir = "results/mippp"
os.makedirs(results_dir, exist_ok=True)
os.environ["MIPPP_NO_VERSION_WARNING"] = "1"

for exec_name in ["mippp", "mippp_bulk", "mippp_distinct", "mippp_bulk_distinct"]:
    for solver in [
        "Cbc",
        "COPT",
        "CPLEX",
        "GLPK",
        "Gurobi",
        "Highs",
        "MOSEK",
        "SCIP",
        "Xpress",
    ]:
        csv_path = f"{results_dir}/{solver}{exec_name[5:]}.csv"
        try:
            args_list = [(exec_name, solver, N) for N in range(100, 1001, 100)]
            run(cmd, args_list, repetitions, to_row, csv_path)
        except Exception as e:
            print(f"Skipped {exec_name} {solver}: {resume_exception(e)}")
            continue
        print(f"Done {exec_name} {solver}!")
