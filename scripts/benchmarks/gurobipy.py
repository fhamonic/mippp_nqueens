from helper import *
import os


def cmd(N):
    return ["python", "src/gurobi.py", str(N)]


results_dir = "results/gurobi"
os.makedirs(results_dir, exist_ok=True)

csv_path = f"{results_dir}/gurobipy.csv"
try:
    args_list = list(range(100, 1001, 100))
    rows = run(cmd, args_list, csv_path)
    print(f"Done! {summary(rows)}")
except Exception as e:
    print(f"Skipped: {resume_exception(e)}")
