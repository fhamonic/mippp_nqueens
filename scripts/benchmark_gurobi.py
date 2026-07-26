from helper import *
import os


def cmd(args):
    return ["./build/" + args[0], str(args[1])]


results_dir = "results/gurobi"
os.makedirs(results_dir, exist_ok=True)


for exec_name in ["gurobi_c", "gurobi_c_bulk"]:
    csv_path = f"{results_dir}/{exec_name}.csv"
    try:
        args_list = [(exec_name, N) for N in range(100, 1001, 100)]
        rows = run(cmd, args_list, csv_path, time_keys=("model_time_ms",))
        print(f"Done {exec_name}! {summary(rows)}")
    except Exception as e:
        print(f"Skipped: {resume_exception(e)}")
