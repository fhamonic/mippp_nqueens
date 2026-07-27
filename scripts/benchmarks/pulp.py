from helper import *
import os


def cmd(args):
    return [args[0], "src/pulp_.py", str(args[1])]


results_dir = "results/pulp"
os.makedirs(results_dir, exist_ok=True)

for python in ["python", "pypy3"]:
    csv_path = f"{results_dir}/{python}.csv"
    try:
        args_list = [(python, N) for N in range(100, 1001, 100)]
        rows = run(cmd, args_list, csv_path)
        print(f"Done {python}! {summary(rows)}")
    except Exception as e:
        print(f"Skipped {python}: {resume_exception(e)}")
