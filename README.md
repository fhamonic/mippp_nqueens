# N-Queens modeling benchmarks

This repository measures the time it takes to *fill* a N-Queens MILP model
(N² binary variables, 6N-6 constraints) through several modeling interfaces:
[MIP++](https://github.com/fhamonic/mippp), the OR-Tools `MPSolver` C++ API,
the Gurobi C API, JuMP, Python-MIP and PuLP.
Only model construction is timed, never the resolution.
These results are to be compared with the [Python-MIP benchmarks](https://python-mip.readthedocs.io/en/latest/bench.html#) of python interfaces.

The following table contains the time *in Milliseconds* required by MIP++ to
fill the model, and how much longer the other C++/Julia interfaces take on the
same machine.

| N | MIP++<br>Cbc | MIP++<br>HiGHS | OR-tools<br>Cbc | OR-tools<br>HiGHS | JuMP<br>Cbc | JuMP<br>HiGHS |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 1.0 ms | 1.2 ms | 3.7 x | 3.0 x | 11.8 x | 59.7 x |
| 200 | 3.4 ms | 5.0 ms | 4.1 x | 2.7 x | 29.4 x | 5.4 x |
| 300 | 7.1 ms | 11.8 ms | 4.5 x | 2.7 x | 10.3 x | 10.3 x |
| 400 | 12.4 ms | 21.1 ms | 4.4 x | 2.6 x | 15.0 x | 8.3 x |
| 500 | 19.6 ms | 36.8 ms | 4.6 x | 2.5 x | 13.4 x | 7.2 x |
| 600 | 27.6 ms | 50.1 ms | 4.8 x | 2.6 x | 12.7 x | 7.1 x |
| 700 | 39.3 ms | 67.5 ms | 4.6 x | 2.6 x | 14.4 x | 6.8 x |
| 800 | 49.0 ms | 100.5 ms | 4.7 x | 2.3 x | 12.4 x | 6.9 x |
| 900 | 62.2 ms | 127.3 ms | 5.1 x | 2.5 x | 12.8 x | 6.1 x |
| 1000 | 73.3 ms | 147.7 ms | 5.2 x | 2.6 x | 14.0 x | 6.4 x |

Cbc is the one backend common to all the interfaces compared here, and HiGHS is
shared by MIP++, OR-Tools and JuMP, which is why the tables use them. The
benchmark runners also produce CSV files for every other solver they find at
runtime (GLPK, SCIP, CPLEX, MOSEK, COPT, Gurobi and Xpress for MIP++), they are
simply not tabulated.

## Model construction: one constraint at a time vs. bulk

Two executables are built from the same model:

- `mippp` (`src/mippp.cpp`) adds the constraints one at a time with
  `model.add_constraint(...)`, mirroring how the OR-Tools, JuMP, Python-MIP and
  PuLP models are written. **All the MIP++ numbers in this README come from this
  executable**, so that the comparison stays apples-to-apples.
- `mippp_bulk` (`src/mippp_bulk.cpp`) uses the bulk `model.add_constraints(range, lambda)`
  overload instead, and writes its own `results/mippp/<solver>_mippp_bulk.csv`
  files.

The same split exists for the Gurobi C API: `gurobi_c` (`src/gurobi_c.cpp`)
calls `GRBaddconstr` per constraint while `gurobi_c_bulk`
(`src/gurobi_c_bulk.cpp`) builds the whole matrix in one `GRBaddconstrs` call.

## MIP++ vs OR-Tools

The following table compares the time *in Milliseconds* required to fill the
same N-Queens MILP model through MIP++ and through the OR-Tools `MPSolver` C++
API (`or-tools/9.15`), for the solvers supported by both.

| N | MIP++<br>Cbc | MIP++<br>HiGHS | MIP++<br>SCIP | OR-tools<br>Cbc | OR-tools<br>HiGHS | OR-tools<br>SCIP |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 1.0 ms | 1.2 ms | 8.3 ms | 3.7 x | 3.0 x | 0.4 x |
| 200 | 3.4 ms | 5.0 ms | 27.1 ms | 4.1 x | 2.7 x | 0.5 x |
| 300 | 7.1 ms | 11.8 ms | 60.8 ms | 4.5 x | 2.7 x | 0.5 x |
| 400 | 12.4 ms | 21.1 ms | 96.1 ms | 4.4 x | 2.6 x | 0.6 x |
| 500 | 19.6 ms | 36.8 ms | 144.4 ms | 4.6 x | 2.5 x | 0.6 x |
| 600 | 27.6 ms | 50.1 ms | 223.5 ms | 4.8 x | 2.6 x | 0.6 x |
| 700 | 39.3 ms | 67.5 ms | 303.3 ms | 4.6 x | 2.6 x | 0.6 x |
| 800 | 49.0 ms | 100.5 ms | 417.0 ms | 4.7 x | 2.3 x | 0.6 x |
| 900 | 62.2 ms | 127.3 ms | 531.3 ms | 5.1 x | 2.5 x | 0.6 x |
| 1000 | 73.3 ms | 147.7 ms | 653.7 ms | 5.2 x | 2.6 x | 0.6 x |

Note that `MPSolver` stores the model in its own backend-independent data structures and only extracts it to the underlying solver when `Solve()` is called, which is why its fill times are nearly identical for all backends and exclude the actual solver load. The MIP++ (and Gurobi C API) timings instead include building the model in the solver's native in-memory representation. The OR-Tools `Gurobi` backend is also supported by `src/or_tools.cpp` but requires a valid Gurobi license at runtime.

## Reproducing the benchmarks

The numbers above were obtained on an AMD Ryzen 7 7800X3D (Ubuntu 22.04, GCC 14.1), with every C++ benchmark compiled with the same compiler and flags (`-std=c++23`, `Release`, `-flto`).

### Requirements

- Linux, GCC >= 14 and [Conan](https://conan.io) >= 2.12 (the build uses the `CMakeConfigDeps` generator; CMake itself is provisioned by Conan).
- The [MIP++](https://github.com/fhamonic/mippp) Conan package (header-only, see below).
- OR-Tools is fetched and built from source automatically by Conan (`or-tools/9.15` with statically linked Cbc, SCIP and HiGHS backends), so the OR-Tools benchmarks need no license and no pre-installed solver.
- The `mippp`/`mippp_bulk` executables load the solvers' shared libraries at *runtime* (`dlopen`): install the ones you want to benchmark (Cbc, SCIP and HiGHS are free; Gurobi, CPLEX, MOSEK and COPT also require a license) and make them visible through `LD_LIBRARY_PATH`.
- The `gurobi_c`/`gurobi_c_bulk` executables (Gurobi C API) link against the Gurobi SDK and are only built when it is found: set the `GUROBI_HOME` environement variable to your installation, typically with `export GUROBI_HOME=".../gurobi1201/linux64"`.

Two Conan profiles are provided, `profiles/gcc14_c++23` (used for the numbers
above) and `profiles/gcc15_c++26`. **Both hardcode the `CC`/`CXX` paths of the
machine they were written on**, edit them to point at your own GCC before
building.

### Building

```sh
git clone https://github.com/fhamonic/mippp_nqueens
cd mippp_nqueens

# 1. export the header-only MIP++ package into your Conan cache
git clone https://github.com/fhamonic/mippp
conan create mippp -pr=profiles/gcc14_c++23 -b=missing -c tools.build:skip_test=true

# 2. build the benchmarks (the first run also builds or-tools and its dependency tree from source, which takes tens of minutes)
conan build . -of=build -pr=profiles/gcc14_c++23 -b=missing
```

The executables are produced directly in `build/` (`build/mippp`,
`build/mippp_bulk`, `build/or_tools`, and `build/gurobi_c*` when the Gurobi SDK
is found).

Known issue: `or-tools/9.15` pins `CXX_STANDARD 17` on a few auxiliary targets, which fails against the abseil version pinned by its recipe (it requires C++20). If the or-tools build fails on `fzn-parser_test`, patch the sources in the Conan cache and re-run the `conan build` command above, it will pick the patched sources up:

```sh
sed -i 's/CXX_STANDARD 17/CXX_STANDARD 20/' \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/flatzinc.cmake" \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/glop.cmake"
```

### Running

All the scripts below are meant to be run from the root of the repository.

```sh
python3 scripts/benchmark_mippp.py     # -> results/mippp/<solver>_mippp[_bulk].csv
python3 scripts/benchmark_ortools.py   # -> results/or_tools/<solver>_or_tools.csv
python3 scripts/benchmark_gurobi.py    # -> results/gurobi_c[_bulk].csv
```

Each runner sweeps `N` from 100 to 1000, repeats every point between 5 and 20
times (fewer repetitions for the larger models), drops the first run as a
warm-up and averages the rest. Solvers whose shared library or license is
missing at runtime are reported as skipped and produce no CSV.

`benchmark_mippp.py`, `benchmark_ortools.py` and `benchmark_jump.py` leave any
CSV that already exists untouched, delete the file to refresh it.
`benchmark_gurobi.py` always re-runs and overwrites.

`results/` is listed in `.gitignore`, so none of the CSV files are committed:
running the benchmarks yourself is the only way to populate it.

### Regenerating the tables

The markdown tables of this README are produced from the CSV files by:

```sh
python3 scripts/tables/mippp_vs_others.py
python3 scripts/tables/mippp_vs_or-tools.py
python3 scripts/tables/jump_vs_python.py
```

Each script reads every CSV it needs at import time, so all the corresponding
benchmarks must have been run first.

### Python and JuMP benchmarks

| N | JuMP<br>Cbc (warm) | JuMP<br>Cbc (cold) | Python-MIP<br>Cbc (CPython) | Python-MIP<br>Cbc (Pypy) | PuLP<br>Cbc (CPython) | PuLP<br>Cbc (Pypy) |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 11.5 ms | 219.7 x | 14.0 x | 13.8 x | 12.0 x | 6.2 x |
| 200 | 98.7 ms | 25.8 x | 8.2 x | 0.9 x | 9.3 x | 1.8 x |
| 300 | 73.8 ms | 36.3 x | 37.1 x | 2.7 x | 40.2 x | 4.9 x |
| 400 | 185.8 ms | 14.8 x | 36.4 x | 2.1 x | 39.5 x | 3.6 x |
| 500 | 262.4 ms | 10.7 x | 49.8 x | 2.2 x | 53.5 x | 4.3 x |
| 600 | 349.7 ms | 8.5 x | 63.9 x | 2.6 x | 69.8 x | 5.1 x |
| 700 | 565.7 ms | 5.4 x | 64.0 x | 2.3 x | 69.4 x | 4.4 x |
| 800 | 607.3 ms | 5.4 x | 87.9 x | 3.1 x | 96.8 x | 5.7 x |
| 900 | 793.8 ms | 4.4 x | 95.9 x | 3.3 x | 105.9 x | 5.8 x |
| 1000 | 1029.0 ms | 3.5 x | 103.5 x | 3.2 x | 112.1 x | 5.9 x |

#### JuMP

The JuMP model is `src/jump.jl`, driven by `scripts/benchmark_jump.py`:

```julia
julia> import Pkg
julia> Pkg.add("JuMP")
julia> Pkg.add("Cbc")
julia> Pkg.add("HiGHS")
```

```sh
python3 scripts/benchmark_jump.py   # -> results/jump/<solver>_jump.csv
```

`src/jump.jl` builds the model twice per process and reports both timings:
`cold_model_time_us`, which includes Julia's JIT compilation, and
`model_time_us`, the warm rebuild. The tables use the warm one, which is two
orders of magnitude smaller. Like OR-Tools' `MPSolver`, JuMP (in its default
*cached* mode) builds the model in its own backend-independent representation,
so its fill times exclude the actual solver load.

#### Python

The Python-MIP, PuLP and gurobipy numbers are produced by the benchmark scripts of the [python-mip repository](https://github.com/coin-or/python-mip) (the same ones behind the published [Python-MIP benchmark](https://python-mip.readthedocs.io/en/latest/bench.html)), included unmodified as a git submodule checked out in `python-mip/`, pinned at the commit that was used. Unlike the C++ and Julia benchmarks, these scripts time a single build of each model, without any warm-up run.

```sh
git submodule update --init
pip install mip pulp gurobipy timeout_decorator   # mip==1.15.0 was used here
./scripts/benchmark_python.sh
```

The runner writes `results/python-mip/`, `results/pulp/` and `results/gurobipy.csv`, skipping any benchmark whose CSV already exists:

- the `*_pypy.csv` variants require `pypy3` with the `mip`, `pulp` and `timeout_decorator` packages installed;
- the gurobipy and Python-MIP/Gurobi benchmarks require a licensed Gurobi installation.
