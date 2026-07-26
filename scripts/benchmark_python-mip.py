from helper import *
import os


def cmd(args):
    return [args[0], "src/python-mip.py", args[1], str(args[2])]


results_dir = "results/python-mip"
os.makedirs(results_dir, exist_ok=True)

for python in ["python", "pypy3"]:
    for solver in ["Cbc", "Gurobi"]:
        csv_path = f"{results_dir}/{python}_{solver}.csv"
        try:
            args_list = [(python, solver, N) for N in range(100, 1001, 100)]
            rows = run(cmd, args_list, csv_path)
            print(f"Done {python} {solver}! {summary(rows)}")
        except Exception as e:
            print(f"Skipped {python} {solver}: {resume_exception(e)}")
