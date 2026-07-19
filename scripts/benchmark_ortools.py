import csv
import json
import os
import subprocess
from statistics import mean


def call_executable(cmd):
    r = str()
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        r = process.stderr.strip()
        return json.loads(r)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr.strip())
    except json.decoder.JSONDecodeError as e:
        raise Exception(r)


results_dir = "results/or_tools"
os.makedirs(results_dir, exist_ok=True)


MIN_REPS = 5
MAX_REPS = 20
REP_BUDGET = 5000


def repetitions(N: int) -> int:
    return max(MIN_REPS, min(MAX_REPS, round(REP_BUDGET / N)))


if __name__ == "__main__":
    solvers = ["Cbc", "SCIP", "GLPK", "Gurobi", "Highs"]
    values = list(range(100, 1001, 100))
    columns = ["N", "num_variables", "num_constraints", "api_time_us", "model_time_us"]

    for solver in solvers:
        csv_path = f"{results_dir}/{solver}_or_tools.csv"
        if os.path.exists(csv_path):
            continue
        try:
            rows = []
            for N in values:
                reps = repetitions(N)
                runs = [
                    call_executable(["./build/or_tools", solver, str(N)])
                    for _ in range(reps + 1)
                ]
                runs = runs[1:]  # drop warm-up
                rows.append(
                    {
                        "N": N,
                        "num_variables": int(runs[0]["num_variables"]),
                        "num_constraints": int(runs[0]["num_constraints"]),
                        "api_time_us": mean(r["api_time_us"] for r in runs),
                        "model_time_us": mean(r["model_time_us"] for r in runs),
                    }
                )
        except Exception as e:
            lines = str(e).split("\n")
            error_lines = [line for line in lines if line.lower().find("error") != -1]
            print(
                f"Skipped {solver}: {error_lines[0] if len(error_lines) > 0 else lines[0]}..."
            )
            continue
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
