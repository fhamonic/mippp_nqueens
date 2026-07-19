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


results_dir = "results"
os.makedirs(results_dir, exist_ok=True)


MIN_REPS = 5
MAX_REPS = 20
REP_BUDGET = 5000


def repetitions(N: int) -> int:
    return max(MIN_REPS, min(MAX_REPS, round(REP_BUDGET / N)))


if __name__ == "__main__":
    values = list(range(100, 1001, 100))
    columns = ["N", "num_variables", "num_constraints", "model_time_us"]

    for exec_name in ["gurobi_c", "gurobi_c_bulk"]:
        csv_path = f"{results_dir}/{exec_name}.csv"
        try:
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()

                for N in values:
                    reps = repetitions(N)
                    runs = [
                        call_executable(["./build/" + exec_name, str(N)])
                        for _ in range(reps + 1)
                    ]
                    runs = runs[1:]  # drop warm-up

                    writer.writerow(
                        {
                            "N": N,
                            "num_variables": int(runs[0]["num_variables"]),
                            "num_constraints": int(runs[0]["num_constraints"]),
                            "model_time_us": mean(r["model_time_us"] for r in runs),
                        }
                    )
        except Exception as e:
            print(f"Skipped {exec_name}")
            os.remove(csv_path)
            continue
