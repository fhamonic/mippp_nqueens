from helper import *
import os
from statistics import mean


def cmd(args):
    return ["julia", "src/jump.jl", args[0], str(args[1])]


def repetitions(args) -> int:
    reps = int(1000000 / args[1]**2)
    reps = min(reps, 10)
    return max(reps, 1)


def to_row(results: list):
    return {
        "N": int(results[0]["N"]),
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "api_time_ms": mean(r["api_time_ms"] for r in results),
        "cold_model_time_ms": mean(r["cold_model_time_ms"] for r in results),
        "model_time_ms": mean(r["model_time_ms"] for r in results),
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
    try:
        args_list = [(solver, N) for N in range(100, 1001, 100)]
        run(cmd, args_list, repetitions, to_row, csv_path)
    except Exception as e:
        print(f"Skipped {solver}: {resume_exception(e)}")
        continue
    print(f"Done {solver}!")
