from helper import *
import os
from statistics import mean


def cmd(args):
    return [args[0], "src/python-mip.py", args[1], str(args[2])]


def repetitions(args) -> int:
    reps = int(1000000 / args[2] ** 2)
    reps = min(reps, 10)
    reps = max(reps, 1)
    if args[0] == "pypy3":
        reps *= 10
    return reps + 1


def to_row(results: list):
    if len(results) > 1 and results[0]["model_time_ms"] > results[1]["model_time_ms"]:
        results = results[1:]
    return {
        "N": int(results[0]["N"]),
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "api_time_ms": mean(r["api_time_ms"] for r in results),
        "model_time_ms": mean(r["model_time_ms"] for r in results),
    }


results_dir = "results/python-mip"
os.makedirs(results_dir, exist_ok=True)

for python in ["python", "pypy3"]:
    for solver in ["Cbc", "Gurobi"]:
        csv_path = f"{results_dir}/{python}_{solver}.csv"
        try:
            args_list = [(python, solver, N) for N in range(100, 1001, 100)]
            run(cmd, args_list, repetitions, to_row, csv_path)
        except Exception as e:
            print(f"Skipped {python} {solver}: {resume_exception(e)}")
            continue
        print(f"Done {python} {solver}!")
