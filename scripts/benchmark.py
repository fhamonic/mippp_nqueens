import os
import subprocess


def call_executable(cmd):
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return process.stderr.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr.strip())


results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

if __name__ == "__main__":
    solvers = ["Cbc", "CPLEX", "Gurobi", "Highs", "MOSEK", "SCIP", "COPT"]
    values = [str(v) for v in range(100, 1001, 100)]

    for exec in ["mippp", "mippp_bulk"]:
        for solver in solvers:
            with open(f"{results_dir}/{solver}_{exec}.csv", "w") as f:
                for value in values:
                    result = call_executable(["./build/" + exec, solver, value]).split(
                        ","
                    )
                    f.write(f"{value},{result[2]},{result[3]},{(float(result[-2])+float(result[-1]))/1000:.1f}\n")

    for exec in ["gurobi_c", "gurobi_c_bulk"]:
        # only built when the Gurobi SDK is found, see GUROBI_DIR in CMakeLists.txt
        if not os.path.isfile(f"./build/{exec}"):
            print(f"./build/{exec} not built, skipping")
            continue
        with open(f"{results_dir}/Gurobi_{exec}.csv", "w") as f:
            for value in values:
                result = call_executable(["./build/" + exec, value]).split(",")
                f.write(f"{value},{float(result[-1])/1000:.1f}\n")

    # "Gurobi" is also supported but requires a valid license at runtime
    ortools_solvers = ["Cbc", "SCIP", "Highs"]
    for solver in ortools_solvers:
        with open(f"{results_dir}/{solver}_or_tools.csv", "w") as f:
            for value in values:
                result = call_executable(["./build/or_tools", solver, value]).split(
                    ","
                )
                f.write(f"{value},{result[2]},{result[3]},{(float(result[-2])+float(result[-1]))/1000:.1f}\n")
