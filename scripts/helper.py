import csv
import json
import subprocess
from collections.abc import Callable


def call_executable(cmd):
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return json.loads(process.stderr.strip())
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr.strip() + '\n' + str(e))


def run(
    cmd_f: Callable,
    args_list: list,
    repetitions: Callable,
    to_row: Callable,
    csv_path: str,
):
    rows = []
    for args in args_list:
        reps = repetitions(args)
        runs = []
        for i in range(reps):
            cmd = cmd_f(args)
            print(
                "\r" + " " * 80 + "\r> " + " ".join(cmd) + f"\t({i+1}/{reps})", end="\r"
            )
            runs.append(call_executable(cmd))
        rows.append(to_row(runs))
    print("\r" + " " * 80, end="\r")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def resume_exception(e: Exception):
    lines = str(e).split("\n")
    error_lines = [line for line in lines if line.lower().find("error") != -1]
    return error_lines[0] if len(error_lines) > 0 else lines[0]
