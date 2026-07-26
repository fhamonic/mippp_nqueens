from helper import *
import os


def cmd(args):
    return [f"./build/or_tools_{args[0]}", args[1], str(args[2])]


results_dir = "results/or-tools"
os.makedirs(results_dir, exist_ok=True)

for interface in ["mpsolver", "mathopt"]:
    for solver in ["Cbc", "SCIP", "GLPK", "Gurobi", "Highs"]:
        csv_path = f"{results_dir}/{solver}_{interface}.csv"
        try:
            args_list = [(interface, solver, N) for N in range(100, 1001, 100)]
            rows = run(cmd, args_list, csv_path)
            print(f"Done {interface} {solver}! {summary(rows)}")
        except Exception as e:
            print(f"Skipped {interface} {solver}: {resume_exception(e)}")
