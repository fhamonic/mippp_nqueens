import csv
import json
import re
import subprocess
import time
from collections.abc import Callable
from math import sqrt
from statistics import median, stdev

# Sampling policy. Every repetition is a fresh process, so there is nothing to
# warm up and nothing to discard: we report the *median* of a few samples and
# keep sampling until it stops moving. Repetitions are spent where the noise
# is, which is not where the time is: the sub-millisecond C++ points are the
# jittery ones and cost nothing, while the multi-second Python ones are
# consistent and get away with the minimum.
MIN_REPETITIONS = 3  # smallest sample giving both a median and an error bar
MAX_REPETITIONS = 25
TIME_BUDGET_S = 5.0  # spent per data point, but never fewer than 2 repetitions
TARGET_ERROR_PCT = 1.5  # we stop once the median is this reproducible

MODEL_TIME_KEY = "model_time_ms"
META_KEYS = ("N", "num_variables", "num_constraints")


def call_executable(cmd):
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        result = process.stderr.strip()
        # Strip stderr noise around the json (solver banners, version warnings)
        start = result.find("{")
        result = result[start : result.find("}", start) + 1]
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr.strip() + "\n" + str(e))


def error_pct(samples: list) -> float:
    """Standard error of the median, as a percentage of that median.

    How much the reported number would move if the whole measurement were
    repeated -- which is the thing we want small, not the spread of the samples
    themselves. stdev/sqrt(n) is the standard error of the mean; a median is
    about 1.25x noisier than a mean, hence the factor.
    """
    center = median(samples)
    if len(samples) < 2 or center == 0:
        return 100.0
    return 100 * 1.25 * stdev(samples) / (center * sqrt(len(samples)))


def sample(cmd: list, progress: str = "") -> list:
    """Repeat one data point until its median is stable or the budget is out."""
    runs = []
    start = time.perf_counter()
    while len(runs) < MAX_REPETITIONS:
        label = " ".join(cmd) + progress + f"\t(rep {len(runs)+1})"
        print("\r" + " " * 80 + "\r> " + label, end="\r")
        runs.append(call_executable(cmd))
        if len(runs) < 2:
            continue  # an error bar needs two samples, whatever the budget says
        if time.perf_counter() - start >= TIME_BUDGET_S:
            break  # points this slow keep whatever error bar they ended up with
        if len(runs) < MIN_REPETITIONS:
            continue
        if error_pct([r[MODEL_TIME_KEY] for r in runs]) <= TARGET_ERROR_PCT:
            break
    return runs


def to_row(runs: list, time_keys: tuple) -> dict:
    row = {}
    for key in META_KEYS:
        values = {int(r[key]) for r in runs}
        if len(values) > 1:
            raise Exception(f"error: {key} varies across repetitions: {sorted(values)}")
        row[key] = values.pop()
    for key in time_keys:
        row[key] = round(median(r[key] for r in runs), 4)  # microsecond resolution
    row["repetitions"] = len(runs)
    row["error_pct"] = round(error_pct([r[MODEL_TIME_KEY] for r in runs]), 2)
    return row


def summary(rows: list) -> str:
    """One-line report of how much sampling effort each point needed."""
    reps = [r["repetitions"] for r in rows]
    noisy = [r["N"] for r in rows if r["error_pct"] > TARGET_ERROR_PCT]
    text = (
        f"{len(rows)} points, {min(reps)}-{max(reps)} reps, "
        f"error <= {max(r['error_pct'] for r in rows):.1f}%"
    )
    if noisy:
        text += " (above target at N=" + ", ".join(str(N) for N in noisy) + ")"
    return text


def run(
    cmd_f: Callable,
    args_list: list,
    csv_path: str,
    time_keys: tuple = ("api_time_ms", MODEL_TIME_KEY),
) -> list:
    try:
        rows = []
        for args in args_list:
            progress = f" [{len(rows)+1}/{len(args_list)}]"
            rows.append(to_row(sample(cmd_f(args), progress), time_keys))
    except Exception as e:
        print("\r" + " " * 80, end="\r")
        raise e
    print("\r" + " " * 80, end="\r")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return rows


# Log preambles the solver toolchains print before the real message; the absl
# banner ends in "written to STDERR", which otherwise wins the match below.
NOISE_MARKERS = ("log messages before", "absl::InitializeLog")
# "W0000 00:00:1785064406.140516  798264 linear_solver.cc:533] Support for..."
GLOG_PREFIX = re.compile(r"^[IWEF]\d{4} [\d:.]+ +\d+ [\w.\-]+:\d+\] ")
CAUSE_MARKERS = (
    "error",
    "exception",
    "unknown solver",
    "unavailable",
    "not found",
    "not linked",
    "failed",
    "terminate called",
)


def resume_exception(e: Exception) -> str:
    """Pick the one line of a failed run worth printing next to "Skipped"."""
    lines = [GLOG_PREFIX.sub("", line.strip()) for line in str(e).split("\n")]
    lines = [
        line for line in lines if line and not any(n in line for n in NOISE_MARKERS)
    ]
    if not lines:
        return repr(e)
    for line in lines:
        if any(marker in line.lower() for marker in CAUSE_MARKERS):
            return line
    return lines[-1]  # no stated cause: the exit status is all we have
