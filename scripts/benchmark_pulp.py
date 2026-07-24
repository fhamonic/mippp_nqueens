from helper import *
import os
from statistics import mean


def cmd(args):
    return [args[0], "src/pulp_.py", str(args[1])]


def repetitions(args) -> int:
    reps = int(1000000 / args[1] ** 2)
    reps = min(reps, 10)
    reps = max(reps, 1)
    if args[0] == "pypy3":
        reps *= 10
    return reps + 1


def to_row(results: list):
    if len(results) > 1 and results[0]["model_time_ms"] > results[1]["model_time_ms"]:
        results = results[1:]
    return {
        "N": results[0]["N"],
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "api_time_ms": mean(r["api_time_ms"] for r in results),
        "model_time_ms": mean(r["model_time_ms"] for r in results),
    }


results_dir = "results/pulp"
os.makedirs(results_dir, exist_ok=True)

for python in ["python", "pypy3"]:
    csv_path = f"{results_dir}/pulp.csv"
    try:
        args_list = [(python, N) for N in range(100, 1001, 100)]
        run(cmd, args_list, repetitions, to_row, csv_path)
    except Exception as e:
        print(f"Skipped {python}: {resume_exception(e)}")
        exit(1)
    print(f"Done {python}!")
