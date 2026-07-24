from helper import *
import os
from statistics import mean


def cmd(N):
    return ["python",  "", str(N)]


def repetitions(N) -> int:
    reps = int(1000000 / N**2)
    reps = min(reps, 10)
    return max(reps, 1)


def to_row(results: list):
    return {
        "N": results[0]["N"],
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "model_time_ms": mean(r["model_time_ms"] for r in results),
    }


results_dir = "results/gurobi"
os.makedirs(results_dir, exist_ok=True)

csv_path = f"{results_dir}/gurobipy.csv"
try:
    args_list = range(100, 1001, 100)
    run(cmd, args_list, repetitions, to_row, csv_path)
except Exception as e:
    print(f"Skipped: {resume_exception(e)}")
    exit(1)
print(f"Done!")
