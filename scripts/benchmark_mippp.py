from helper import *
import os


def cmd(args):
    return ["./build/" + args[0], args[1], str(args[2])]


results_dir = "results/mippp"
os.makedirs(results_dir, exist_ok=True)
os.environ["MIPPP_NO_VERSION_WARNING"] = "1"

for exec_name in ["mippp", "mippp_bulk", "mippp_distinct", "mippp_bulk_distinct"]:
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
        csv_path = f"{results_dir}/{solver}{exec_name[5:]}.csv"
        try:
            args_list = [(exec_name, solver, N) for N in range(100, 1001, 100)]
            rows = run(cmd, args_list, csv_path)
            print(f"Done {exec_name} {solver}! {summary(rows)}")
        except Exception as e:
            print(f"Skipped {exec_name} {solver}: {resume_exception(e)}")
