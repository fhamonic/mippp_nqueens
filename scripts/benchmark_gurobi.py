from helper import *
import os
from statistics import mean


def cmd(args):
    return ["./build/" + args[0], str(args[1])]


def repetitions(args) -> int:
    reps = int(5000 / args[1])
    reps = min(reps, 20)
    return max(reps, 5)


def to_row(results: list):
    return {
        "N": results[0]["N"],
        "num_variables": int(results[0]["num_variables"]),
        "num_constraints": int(results[0]["num_constraints"]),
        "model_time_us": mean(r["model_time_us"] for r in results),
    }


results_dir = "results/gurobi"
os.makedirs(results_dir, exist_ok=True)


for exec_name in ["gurobi_c", "gurobi_c_bulk"]:
    csv_path = f"{results_dir}/{exec_name}.csv"
    if os.path.exists(csv_path):
        exit(1)
    try:
        args_list = [(exec_name, N) for N in range(100, 1001, 100)]
        run(cmd, args_list, repetitions, to_row, csv_path)
    except Exception as e:
        print(f"Skipped: {resume_exception(e)}")
        exit(1)
    print(f"{exec_name} Done!")
