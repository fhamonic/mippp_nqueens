#!/usr/bin/env python3
"""Assert that the figures quoted in the README prose match the CSVs.

`render_readme.py` keeps the *tables* in step with `results/`; the sentences
around them are hand-written and silently go stale after a re-run. This script
closes that gap: every figure below is recomputed from the committed CSVs,
formatted the way the README states it, and required to appear verbatim in the
prose. A re-run that moves a number fails here instead of shipping.

    python3 scripts/check_figures.py     # also: make check

Each check pairs the expected text with a short literal from the same sentence,
so a figure only counts where it is actually claimed. Rewording a sentence trips
the check, which is intended: a reworded claim needs re-reading anyway.
"""

import csv
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def col(path, key="model_time_ms"):
    with open(ROOT / "results" / path) as f:
        return {int(r["N"]): float(r[key]) for r in csv.DictReader(f)}


def mippp(name):
    return col(f"mippp/{name}.csv")


def ortools(solver, interface):
    return col(f"or-tools/{solver}_{interface}.csv")


def jump(solver, mode):
    return col(f"jump/{solver}_{mode}.csv")


def build_checks():
    """Return [(label, text that must appear, literal from the same sentence)]."""
    c_api, c_api_bulk = col("gurobi/gurobi_c.csv"), col("gurobi/gurobi_c_bulk.csv")
    Ns = sorted(c_api)
    highs, cbc, gurobi = (
        mippp("Highs_distinct"),
        mippp("Cbc_distinct"),
        mippp("Gurobi_distinct"),
    )
    checks = []

    def add(label, text, context):
        checks.append((label, text, context))

    def span(fn, digits=1):
        values = [fn(N) for N in Ns]
        return f"%.{digits}f" % min(values), f"%.{digits}f" % max(values)

    # -- MIP++ against the raw Gurobi C API
    lo, hi = span(lambda N: gurobi[N] / c_api[N] * 100, 0)
    add("MIP++ / C API", f"{lo}–{hi} % of the Gurobi C API", "Gurobi C API")
    add("MIP++ / C API (sweep)", f"({lo}–{hi} %)", "raw C API across the whole sweep")
    lo, hi = span(lambda N: gurobi[N] / c_api[N] * 100 - 100, 0)
    add("MIP++ overhead", f"within {lo}–{hi} %", "raw C API across the whole sweep")
    lo, hi = span(lambda N: c_api_bulk[N] / c_api[N] * 100, 0)
    add("C API bulk", f"({lo}–{hi} %)", "is worth nothing")

    # -- overview ratios, on the HiGHS backend they all share
    lo, hi = span(lambda N: ortools("Highs", "mpsolver_setcoef")[N] / highs[N])
    add("MPSolver / MIP++", f"{lo}–{hi}× `MPSolver`", "JuMP cached")
    lo, hi = span(lambda N: ortools("Highs", "mathopt_setcoef")[N] / highs[N])
    add("MathOpt / MIP++", f"{lo}–{hi}× MathOpt", "JuMP cached")
    lo, hi = span(lambda N: jump("Highs", "cached")[N] / highs[N])
    add("JuMP cached / MIP++", f"{lo}–{hi}× JuMP cached", "JuMP cached")
    lo, hi = span(lambda N: jump("Highs", "direct")[N] / highs[N], 0)
    add("JuMP direct / MIP++", f"{lo}–{hi}× JuMP direct", "JuMP cached")

    # -- the Python field at N = 1000
    for label, series, ref, unit in [
        ("gurobipy", col("gurobi/gurobipy.csv"), gurobi, "gurobipy"),
        ("Python-MIP", col("python-mip/python_Cbc.csv"), cbc, "Python-MIP"),
        ("PuLP", col("pulp/python.csv"), cbc, "PuLP"),
        ("highspy", col("highs/highspy.csv"), highs, "highspy"),
    ]:
        add(f"{label} / MIP++", f"{series[1000] / ref[1000]:.0f}×", f"× {unit}")

    # -- the two deferral tells
    add("JuMP cached HiGHS", f"({jump('Highs', 'cached')[1000]:.0f} ms", "whichever backend")
    add("JuMP cached Gurobi", f"{jump('Gurobi', 'cached')[1000]:.0f} ms for Gurobi",
        "whichever backend")

    # -- OR-Tools
    lo, hi = span(lambda N: ortools("Cbc", "mpsolver_setcoef")[N] / cbc[N])
    add("MIP++ vs MPSolver (Cbc)", f"{lo}–{hi}× faster than `MPSolver` for Cbc", "for Cbc")
    lo, hi = span(lambda N: ortools("Highs", "mpsolver_setcoef")[N] / highs[N])
    add("MIP++ vs MPSolver (HiGHS)", f"{lo}–{hi}× faster", "for HiGHS")
    lo, hi = span(lambda N: ortools("Xpress", "mpsolver_setcoef")[N] / mippp("Xpress_distinct")[N])
    add("MIP++ vs MPSolver (Xpress)", f"{lo}–{hi}× faster for Xpress", "for Xpress")
    add("MathOpt worst case",
        f"up to {ortools('Highs', 'mathopt_setcoef')[1000] / highs[1000]:.1f}× MIP++",
        "MathOpt is slower still")
    lo, hi = span(
        lambda N: min(
            ortools(s, "mpsolver")[N] / ortools(s, "mpsolver_setcoef")[N]
            for s in ("Cbc", "Highs", "SCIP", "Xpress")
        )
    )
    _, hi = span(
        lambda N: max(
            ortools(s, "mpsolver")[N] / ortools(s, "mpsolver_setcoef")[N]
            for s in ("Cbc", "Highs", "SCIP", "Xpress")
        )
    )
    add("expression penalty", f"`MPSolver` {lo}–{hi}×", "expression object costs")

    # -- JuMP
    add("direct/cached HiGHS",
        f"{jump('Highs', 'direct')[1000] / jump('Highs', 'cached')[1000]:.1f}× for",
        "Cutting out the caching layer")
    add("direct/cached Gurobi",
        f"{jump('Gurobi', 'direct')[1000] / jump('Gurobi', 'cached')[1000]:.1f}× for Gurobi",
        "Cutting out the caching layer")
    add("MPSolver vs MIP++ at N=1000",
        f"({ortools('Highs', 'mpsolver_setcoef')[1000] / highs[1000]:.1f}× on HiGHS",
        "costs far less there")
    add("MIP++ HiGHS at N=1000", f"({highs[1000]:.1f} ms", "Against MIP++ on HiGHS")
    add("JuMP direct vs MIP++",
        f"{jump('Highs', 'direct')[1000] / highs[1000]:.0f}× for JuMP direct", "that is")
    add("JuMP cached vs MIP++",
        f"{jump('Highs', 'cached')[1000] / highs[1000]:.1f}× for JuMP cached", "that is")

    # -- backends
    add("SCIP vs Cbc", f"({mippp('SCIP')[1000] / mippp('Cbc')[1000]:.1f}× Cbc",
        "far behind the rest")
    for solver in ("GLPK", "Xpress", "CPLEX"):
        series = mippp(solver)
        drift = (series[1000] / 1e6) / (series[200] / 4e4)
        add(f"{solver} per-nonzero drift", f"{solver} (×{drift:.1f}", "per nonzero")

    # -- build variants at N = 1000, as the summary table rounds them
    backends = ("Cbc", "MOSEK", "COPT", "Highs", "CPLEX", "Gurobi", "GLPK", "Xpress", "SCIP")
    label = {"Highs": "HiGHS"}
    hint = {b: round(100 - mippp(f"{b}_distinct")[1000] / mippp(b)[1000] * 100) for b in backends}
    bulk = {b: round(100 - mippp(f"{b}_bulk")[1000] / mippp(b)[1000] * 100) for b in backends}
    add("hint span", f"worth {min(hint.values())}–{max(hint.values())} %", "never hurts")
    for b in ("MOSEK", "COPT", "SCIP"):
        add(f"hint {b}", f"{label.get(b, b)} ({hint[b]} %)", "never hurts")
    for b in ("CPLEX", "COPT", "Xpress"):
        add(f"bulk {b}", f"{bulk[b]} % for {label.get(b, b)}", "Bulk cuts both ways")
    add("bulk MOSEK", f"MOSEK (+{-bulk['MOSEK']} %)", "Bulk cuts both ways")

    # -- sampling quality
    errors = [
        float(r["error_pct"])
        for path in sorted(glob.glob(str(ROOT / "results" / "*" / "*.csv")))
        for r in csv.DictReader(open(path))
    ]
    over = [e for e in errors if e > 1.5]
    add("points above target", f"{len(over)} of the {len(errors)} points",
        "miss the 1.5 % target")
    add("points just above", f"{sum(1 for e in over if e <= 2.5)} of them by",
        "less than a point")
    add("points well above", f"{sum(1 for e in over if e > 2.5)} by more", "less than a point")
    add("worst point", f"{max(over):.1f} %)", "single worst point")
    xpress = [
        float(r["error_pct"])
        for path in sorted(glob.glob(str(ROOT / "results" / "mippp" / "Xpress*.csv")))
        for r in csv.DictReader(open(path))
    ]
    add("worst Xpress point", f"(up to {max(xpress):.1f} %)", "25-repetition cap")
    return checks


def main():
    prose = (ROOT / "README.md").read_text()
    # the generated tables are render_readme.py's business, not ours
    prose = re.sub(r"<!-- table:[\w.-]+ -->.*?<!-- /table -->", "", prose, flags=re.S)

    checks = build_checks()
    failures = [
        (label, expected, "sentence missing" if context not in prose else "figure stale")
        for label, expected, context in checks
        if expected not in prose
    ]

    if failures:
        print(f"{len(failures)} of {len(checks)} README figures do not match results/:\n")
        for label, expected, why in failures:
            print(f"  {label:32s} expected {expected!r}  ({why})")
        print("\nRe-read the sentence against the CSVs, or update this script if the")
        print("claim itself changed.")
        return 1

    print(f"All {len(checks)} README prose figures match results/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
