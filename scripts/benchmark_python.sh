#!/bin/bash
# Runs the N-Queens benchmarks of the python libraries (Python-MIP, PuLP,
# gurobipy) from the python-mip repository (extern/python-mip submodule),
# and the JuMP one (jump/n-queens.jl), writing the result files under
# results/python-mip/ where scripts/tables.py picks them up.
# Adapted from the queens part of extern/python-mip/benchmarks/bench.sh.
#
# Usage: scripts/benchmark_python.sh [output_dir]
set -u
cd "$(dirname "$0")/.."
ROOT=$PWD
BENCH=$ROOT/extern/python-mip/benchmarks
OUT=${1:-$ROOT/results/python-mip}

if [ ! -f "$BENCH/queens.py" ]; then
    echo "python-mip submodule missing: run 'git submodule update --init'" >&2
    exit 1
fi

# warm-up run used for the published results (no-op if already applied)
if git -C "$BENCH/.." apply "$ROOT/patches/python-mip-queens-warmup.patch" 2> /dev/null; then
    echo "applied patches/python-mip-queens-warmup.patch"
fi

mkdir -p "$OUT"
cd "$BENCH"

run() { # run <interpreter> <script> <produced csv> <output csv> [script args...]
    local interp=$1 script=$2 produced=$3 out=$4
    shift 4
    if ! command -v "$interp" > /dev/null; then
        echo "-- $interp not found, skipping $out"
        return
    fi
    echo "== $interp $script $* -> $out"
    rm -f "$produced"
    if "$interp" "$script" "$@" && [ -f "$produced" ]; then
        mv "$produced" "$OUT/$out"
    else
        echo "-- failed (missing library or solver license?), skipping $out"
    fi
}

run python3 queens.py queens-mip-cbc.csv queens-mip-cbc-cpython.csv cbc
run pypy3 queens.py queens-mip-cbc.csv queens-mip-cbc-pypy.csv cbc
run python3 queens.py queens-mip-gurobi.csv queens-mip-grb-cpython.csv gurobi
run pypy3 queens.py queens-mip-gurobi.csv queens-mip-grb-pypy.csv gurobi
run python3 queens-gurobi.py queens-gurobi-cpython.csv queens-gurobi-cpython.csv
run python3 queens-pulp.py queens-pulp.csv queens-pulp-cpython.csv
run pypy3 queens-pulp.py queens-pulp.csv queens-pulp-pypy.csv

if command -v julia > /dev/null; then
    echo "== julia jump/n-queens.jl -> queens-jump.csv"
    julia "$ROOT/jump/n-queens.jl" "$OUT/queens-jump.csv" ||
        echo "-- failed (JuMP and HiGHS julia packages installed?), skipping queens-jump.csv"
else
    echo "-- julia not found, skipping queens-jump.csv"
fi
