from helper import *
import os
from statistics import mean


def cmd(args):
    return ["julia", "src/jump.jl", args[0], str(args[1])]


def repetitions(args) -> int:
    reps = int(5000 / args[1])
    reps = min(reps, 20)
    return max(reps, 5)


def to_row(results: list):
    return {
        "N": int(results[0]["N"]),
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "api_time_us": mean(r["api_time_us"] for r in results),
        "cold_model_time_us": mean(r["cold_model_time_us"] for r in results),
        "model_time_us": mean(r["model_time_us"] for r in results),
    }


results_dir = "results/jump"
os.makedirs(results_dir, exist_ok=True)
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
    csv_path = f"{results_dir}/{solver}.csv"
    if os.path.exists(csv_path):
        continue
    try:
        args_list = [(solver, N) for N in range(100, 1001, 100)]
        run(cmd, args_list, repetitions, to_row, csv_path)
    except Exception as e:
        print(f"Skipped {solver}: {resume_exception(e)}")
        continue
    print(f"{solver} Done!")
