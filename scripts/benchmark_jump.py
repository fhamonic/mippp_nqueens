from helper import *
import os


def cmd(args):
    return ["julia", f"src/jump_{args[0]}.jl", args[1], str(args[2])]


results_dir = "results/jump"
os.makedirs(results_dir, exist_ok=True)


for interface in ["cached", "direct"]:
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
        csv_path = f"{results_dir}/{solver}_{interface}.csv"
        try:
            args_list = [(interface, solver, N) for N in range(100, 1001, 100)]
            rows = run(
                cmd,
                args_list,
                csv_path,
                time_keys=("api_time_ms", "cold_model_time_ms", "model_time_ms"),
            )
            print(f"Done {interface} {solver}! {summary(rows)}")
        except Exception as e:
            print(f"Skipped {interface} {solver}: {resume_exception(e)}")
