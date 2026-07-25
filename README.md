# N-Queens modeling benchmarks

This repository measures how long it takes to *fill* a N-Queens MILP model
(N² binary variables, 6N-6 constraints) through several modeling interfaces.
**Only model construction is timed, never the resolution.**

The interfaces compared are:

- [MIP++](https://github.com/fhamonic/mippp) — the header-only C++ modeling library benchmarked here;
- the OR-Tools `MPSolver` C++ API (`or-tools/9.15`);
- the Gurobi C API;
- [JuMP](https://jump.dev/) (Julia);
- the Python interfaces [gurobipy](https://pypi.org/project/gurobipy/), [highspy](https://pypi.org/project/highspy/), [PuLP](https://pypi.org/project/PuLP/) and [Python-MIP](https://www.python-mip.com/), each run on CPython and, where relevant, on PyPy.

Every benchmark is self-contained in this repository (`src/`): there is no
longer any external submodule or dependency on the Python-MIP repository.

The headline result: **MIP++ builds the model within a few percent of the
time taken by the raw Gurobi C API** (see [MIP++ vs the Gurobi C API](#mip-vs-the-gurobi-c-api)),
while being several times faster than the other C++/Julia interfaces and two to
three *orders of magnitude* faster than the Python ones.

## MIP++ vs the other C++/Julia interfaces

Time *in milliseconds* required by MIP++ to fill the model, and how much longer
the OR-Tools `MPSolver` C++ API and JuMP take on the same machine for the two
backends common to all three (Cbc and HiGHS):

| N | <div align="center">MIP++<br>Cbc</div> | <div align="center">MIP++<br>HiGHS</div> | <div align="center">OR-tools<br>Cbc</div> | <div align="center">OR-tools<br>HiGHS</div> | <div align="center">JuMP<br>Cbc</div> | <div align="center">JuMP<br>HiGHS</div> |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.8 ms | 1.4 ms | 4.3 x | 2.5 x | 15.7 x | 49.3 x |
| 200 | 3.0 ms | 5.5 ms | 4.6 x | 2.5 x | 32.9 x | 4.9 x |
| 300 | 6.4 ms | 13.4 ms | 5.0 x | 2.4 x | 11.0 x | 8.7 x |
| 400 | 10.8 ms | 21.8 ms | 5.0 x | 2.5 x | 16.9 x | 8.0 x |
| 500 | 17.2 ms | 34.2 ms | 5.2 x | 2.7 x | 14.7 x | 9.6 x |
| 600 | 24.3 ms | 54.3 ms | 5.4 x | 2.4 x | 14.2 x | 6.4 x |
| 700 | 33.4 ms | 68.8 ms | 5.3 x | 2.6 x | 16.6 x | 6.5 x |
| 800 | 42.8 ms | 93.8 ms | 5.4 x | 2.4 x | 14.1 x | 7.4 x |
| 900 | 54.3 ms | 116.2 ms | 5.7 x | 2.7 x | 15.6 x | 7.4 x |
| 1000 | 66.0 ms | 139.4 ms | 5.8 x | 2.8 x | 14.0 x | 6.3 x |

Cbc is the one backend common to every interface, and HiGHS is shared by MIP++,
OR-Tools and JuMP, which is why the tables use them. The benchmark runners also
produce CSV files for every other solver they find at runtime (GLPK, SCIP,
CPLEX, MOSEK, COPT, Gurobi and Xpress for MIP++); they are simply not tabulated
here.

## How the model is built: single vs bulk, and the `distinct_variables` hint

Four MIP++ executables are built from the same model, differing only in *how*
the constraints are handed to the library:

| executable | constraints added | `distinct_variables` hint | CSV suffix |
|---|---|---|---|
| `mippp` | one at a time (`add_constraint`) | no | *(none)* |
| `mippp_distinct` | one at a time (`add_constraint`) | yes | `_distinct` |
| `mippp_bulk` | in bulk (`add_constraints(range, λ)`) | no | `_bulk` |
| `mippp_bulk_distinct` | in bulk (`add_constraints(range, λ)`) | yes | `_bulk_distinct` |

The `distinct_variables` tag tells MIP++ that the terms of each linear
expression reference pairwise-distinct variables, letting it skip the
coefficient-merging (deduplication) step it would otherwise perform. In the
N-Queens model every constraint genuinely has distinct variables, so the hint is
an idiomatic use rather than a shortcut, and it is what makes MIP++ competitive
with the raw solver C APIs.

Timing all four variants for the Cbc backend (the one common to every
interface) shows what each axis is worth:

| N | <div align="center">MIP++ · Cbc<br>one-at-a-time</div> | <div align="center">MIP++ · Cbc<br>+ distinct</div> | <div align="center">MIP++ · Cbc<br>bulk</div> | <div align="center">MIP++ · Cbc<br>bulk + distinct</div> |
|:---:|---:|---:|---:|---:|
| 100 | 0.9 ms | 0.8 ms | 1.0 ms | 0.9 ms |
| 200 | 3.3 ms | 3.0 ms | 3.4 ms | 3.0 ms |
| 300 | 7.1 ms | 6.4 ms | 7.2 ms | 6.3 ms |
| 400 | 12.4 ms | 10.8 ms | 12.5 ms | 11.2 ms |
| 500 | 18.7 ms | 17.2 ms | 19.3 ms | 17.2 ms |
| 600 | 28.0 ms | 24.3 ms | 28.7 ms | 25.1 ms |
| 700 | 37.8 ms | 33.4 ms | 38.4 ms | 33.0 ms |
| 800 | 48.8 ms | 42.8 ms | 50.7 ms | 44.5 ms |
| 900 | 61.0 ms | 54.3 ms | 63.5 ms | 55.2 ms |
| 1000 | 72.3 ms | 66.0 ms | 74.2 ms | 66.6 ms |

The `distinct_variables` hint is the one that pays off — about 10% for Cbc and a
few percent for the other backends, but always in MIP++'s favor. One-at-a-time
vs bulk barely moves the needle for Cbc, and the sign of the (small) difference
is backend-dependent: bulk helps HiGHS a little but is marginally *slower* for
Gurobi. **All the MIP++
numbers elsewhere in this README come from `mippp_distinct`** — one constraint
at a time, mirroring how the OR-Tools, JuMP and Python models are written, plus
the hint.

The same one-at-a-time / bulk split exists for the Gurobi C API: `gurobi_c`
calls `GRBaddconstr` per constraint while `gurobi_c_bulk` builds the whole
matrix in a single `GRBaddconstrs` call.

## MIP++ vs OR-Tools

Time *in milliseconds* required to fill the same model through MIP++ and through
the OR-Tools `MPSolver` C++ API, for the three backends supported by both:

| N | <div align="center">MIP++<br>Cbc</div> | <div align="center">MIP++<br>HiGHS</div> | <div align="center">MIP++<br>SCIP</div> | <div align="center">OR-tools<br>Cbc</div> | <div align="center">OR-tools<br>HiGHS</div> | <div align="center">OR-tools<br>SCIP</div> |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.8 ms | 1.4 ms | 8.1 ms | 4.3 x | 2.5 x | 0.4 x |
| 200 | 3.0 ms | 5.5 ms | 26.8 ms | 4.6 x | 2.5 x | 0.5 x |
| 300 | 6.4 ms | 13.4 ms | 57.7 ms | 5.0 x | 2.4 x | 0.6 x |
| 400 | 10.8 ms | 21.8 ms | 92.6 ms | 5.0 x | 2.5 x | 0.6 x |
| 500 | 17.2 ms | 34.2 ms | 140.9 ms | 5.2 x | 2.7 x | 0.7 x |
| 600 | 24.3 ms | 54.3 ms | 209.6 ms | 5.4 x | 2.4 x | 0.6 x |
| 700 | 33.4 ms | 68.8 ms | 295.7 ms | 5.3 x | 2.6 x | 0.6 x |
| 800 | 42.8 ms | 93.8 ms | 394.6 ms | 5.4 x | 2.4 x | 0.6 x |
| 900 | 54.3 ms | 116.2 ms | 513.9 ms | 5.7 x | 2.7 x | 0.6 x |
| 1000 | 66.0 ms | 139.4 ms | 643.6 ms | 5.8 x | 2.8 x | 0.6 x |

MIP++ fills the model 5–6× faster than `MPSolver` for Cbc and ~2.5× faster for
HiGHS. **SCIP is the exception**: `MPSolver` stores the model in its own
backend-independent data structures and only extracts it into the underlying
solver when `Solve()` is called, so its fill time excludes the SCIP load
entirely and is nearly identical across all three backends. MIP++ (like the
Gurobi C API below) instead builds directly in the solver's native in-memory
representation, and SCIP's incremental build API is slow — hence MIP++ appears
"slower" for SCIP even though it is doing strictly more work up front. The
OR-Tools `Gurobi` backend is also supported by `src/or_tools.cpp` but requires a
valid Gurobi license at runtime.

## MIP++ vs the Gurobi C API

The most direct measure of MIP++'s overhead: the pure Gurobi C API in absolute
milliseconds, MIP++ as a *percentage* of it, and the other Gurobi-capable
interfaces as multiples of it.

| N | Gurobi C API | MIP++ | gurobipy | <div align="center">JuMP<br>warm</div> | <div align="center">JuMP<br>cold</div> | <div align="center">Python-MIP<br>CPython</div> | <div align="center">Python-MIP<br>PyPy</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 3.2 ms | 96.2 % | 33.3 x | 2.9 x | 151.3 x | 45.4 x | 37.5 x |
| 200 | 8.7 ms | 98.5 % | 86.2 x | 4.2 x | 60.2 x | 98.9 x | 19.8 x |
| 300 | 17.7 ms | 96.8 % | 146.3 x | 3.8 x | 35.3 x | 156.3 x | 15.5 x |
| 400 | 30.4 ms | 96.9 % | 207.3 x | 6.0 x | 22.4 x | 218.1 x | 14.7 x |
| 500 | 46.4 ms | 99.6 % | 273.1 x | 5.7 x | 15.9 x | 281.1 x | 15.2 x |
| 600 | 66.4 ms | 99.9 % | 329.7 x | 5.2 x | 13.5 x | 337.2 x | 16.2 x |
| 700 | 91.7 ms | 100.3 % | 380.2 x | 5.0 x | 11.8 x | 390.3 x | 17.1 x |
| 800 | 120.1 ms | 100.5 % | 435.1 x | 5.8 x | 10.1 x | 450.7 x | 18.6 x |
| 900 | 154.6 ms | 99.9 % | 484.5 x | 4.8 x | 9.3 x | 496.6 x | 19.2 x |
| 1000 | 188.4 ms | 101.3 % | 549.8 x | 5.6 x | 8.5 x | 557.4 x | 21.0 x |

MIP++ tracks the raw C API to within a few percent across the whole sweep
(≈96–101%, and marginally *faster* than it for the smaller models) — the
modeling layer is essentially free. gurobipy and CPython Python-MIP, by
contrast, take several *hundred* times longer to build the identical model.
JuMP's `cold` column includes Julia's JIT compilation (paid once per process);
its `warm` column is a rebuild in the same process.

## Python modeling interfaces

The Python benchmarks are self-contained (`src/gurobi.py`, `src/highs.py`,
`src/pulp_.py`, `src/python-mip.py`) and time a single build per model. Fill
time *in milliseconds* (values reach tens of seconds at N=1000):

| N | <div align="center">highspy<br>HiGHS</div> | <div align="center">PuLP<br>Cbc · CPython</div> | <div align="center">PuLP<br>Cbc · PyPy</div> | <div align="center">Python-MIP<br>Cbc · CPython</div> | <div align="center">Python-MIP<br>Cbc · PyPy</div> |
|:---:|---:|---:|---:|---:|---:|
| 100 | 0.20 s | 0.15 s | 0.06 s | 0.16 s | 0.16 s |
| 200 | 0.79 s | 0.90 s | 0.18 s | 0.87 s | 0.20 s |
| 300 | 1.76 s | 2.99 s | 0.40 s | 2.83 s | 0.30 s |
| 400 | 3.19 s | 7.18 s | 0.74 s | 6.67 s | 0.45 s |
| 500 | 4.93 s | 14.13 s | 1.23 s | 13.27 s | 0.67 s |
| 600 | 7.06 s | 24.40 s | 1.88 s | 22.43 s | 0.97 s |
| 700 | 9.52 s | 39.24 s | 2.75 s | 36.02 s | 1.40 s |
| 800 | 12.32 s | 58.16 s | 3.74 s | 53.75 s | 2.00 s |
| 900 | 16.84 s | 83.89 s | 4.97 s | 76.41 s | 2.67 s |
| 1000 | 19.81 s | 115.01 s | 6.36 s | 104.94 s | 3.55 s |

For the pure-Python builders (PuLP, Python-MIP) the interpreter dominates: PyPy's
JIT makes them ~18× (PuLP) and ~30× (Python-MIP) faster than CPython at N=1000.
For reference, MIP++ builds these same models in single- to low-hundreds of
milliseconds (tables above) — hundreds to thousands of times faster than any
CPython interface.

`gurobipy` (Gurobi, CPython) and the CPython Gurobi Python-MIP results appear in
the [Gurobi table](#mip-vs-the-gurobi-c-api) above.

## Reproducing the benchmarks

The numbers above were obtained on an AMD Ryzen 7 7800X3D (Ubuntu 22.04), with
every C++ benchmark compiled with the same compiler and flags (GCC 14,
`Release`, `-std=c++23`, `-flto`), as configured by `profiles/gcc14_c++23`.

### Requirements

- Linux, GCC >= 14 and [Conan](https://conan.io) >= 2.12 (the build uses the `CMakeConfigDeps` generator; CMake itself is provisioned by Conan).
- The [MIP++](https://github.com/fhamonic/mippp) Conan package (header-only, exported below).
- OR-Tools is fetched and built from source automatically by Conan (`or-tools/9.15`, with statically-linked Cbc, SCIP and HiGHS backends), so the OR-Tools benchmarks need no license and no pre-installed solver.
- The `mippp*` executables load the solvers' shared libraries at *runtime* (`dlopen`): install the ones you want to benchmark (Cbc, GLPK, SCIP and HiGHS are free; Gurobi, CPLEX, MOSEK, COPT and Xpress also require a license) and make them visible through `LD_LIBRARY_PATH`.
- The `gurobi_c`/`gurobi_c_bulk` executables link against the Gurobi SDK and are only built when it is found: set `GUROBI_HOME`, typically `export GUROBI_HOME=".../gurobi1201/linux64"`.
- **Python interfaces**: `pip install highspy pulp mip gurobipy`. highspy, PuLP and Python-MIP bundle a free Cbc/HiGHS; gurobipy and the Gurobi backend of Python-MIP need a licensed Gurobi. For the PyPy columns, install `pulp` and `mip` under `pypy3` as well.
- **JuMP**: a Julia installation with `JuMP`, `Cbc` and `HiGHS` (and optionally `Gurobi`) added.

Two Conan profiles are provided, `profiles/gcc14_c++23` (used for the numbers
above) and `profiles/gcc15_c++26`. **Both hardcode the `CC`/`CXX` paths of the
machine they were written on**; edit them to point at your own GCC before
building.

### Building

```sh
git clone https://github.com/fhamonic/mippp_nqueens
cd mippp_nqueens

# 1. export the header-only MIP++ package into your Conan cache
git clone https://github.com/fhamonic/mippp
conan create mippp -pr=profiles/gcc14_c++23 -b=missing -c tools.build:skip_test=true

# 2. build the benchmarks (the first run also builds or-tools and its whole
#    dependency tree from source, which takes tens of minutes)
conan build . -of=build -pr=profiles/gcc14_c++23 -b=missing
```

The executables are produced directly in `build/` (`build/mippp`,
`build/mippp_distinct`, `build/mippp_bulk`, `build/mippp_bulk_distinct`,
`build/or_tools`, and `build/gurobi_c*` when the Gurobi SDK is found).

Known issue: `or-tools/9.15` pins `CXX_STANDARD 17` on a few auxiliary targets,
which fails against the abseil version its recipe pins (that requires C++20). If
the or-tools build fails on `fzn-parser_test`, patch the sources in the Conan
cache and re-run the `conan build` command above:

```sh
sed -i 's/CXX_STANDARD 17/CXX_STANDARD 20/' \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/flatzinc.cmake" \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/glop.cmake"
```

### Running

Run everything with `make all`, or run any of the individual scripts (all from
the repository root):

```sh
python3 scripts/benchmark_mippp.py        # -> results/mippp/<solver>[_bulk][_distinct].csv
python3 scripts/benchmark_ortools.py      # -> results/or_tools/<solver>.csv
python3 scripts/benchmark_gurobi.py       # -> results/gurobi/gurobi_c[_bulk].csv
python3 scripts/benchmark_gurobipy.py     # -> results/gurobi/gurobipy.csv
python3 scripts/benchmark_highspy.py      # -> results/highs/highspy.csv
python3 scripts/benchmark_jump.py         # -> results/jump/<solver>.csv
python3 scripts/benchmark_pulp.py         # -> results/pulp/<python>.csv
python3 scripts/benchmark_python-mip.py   # -> results/python-mip/<python>_<solver>.csv
```

Each runner sweeps `N` from 100 to 1000 and repeats every point several times
(fewer repetitions for the larger models) before averaging; the PuLP and
Python-MIP runners additionally drop a warm-up build. Solvers whose
shared library, package or license is missing at runtime are reported as skipped
and produce no CSV. Every runner overwrites its CSVs on each run.

The runners spawn the CPython interpreter as `python` (and the PyPy one as
`pypy3`), so make sure a `python` on your `PATH` resolves to the CPython where
the packages are installed — on a stock Ubuntu that ships only `python3`,
activate a virtualenv or install `python-is-python3`. See
[INSTALL.md](INSTALL.md) for the full dependency setup.

`results/` is listed in `.gitignore`, so none of the CSV files are committed.

### Regenerating the tables

The markdown tables above are produced from the CSV files by the scripts under
`scripts/tables/`:

```sh
python3 scripts/tables/mippp_vs_others.py     # MIP++ vs OR-Tools vs JuMP
python3 scripts/tables/mippp_vs_or-tools.py   # MIP++ vs OR-Tools (Cbc, HiGHS, SCIP)
python3 scripts/tables/gurobi_vs_mippp.py     # Gurobi C API vs MIP++ vs the rest
python3 scripts/tables/python_interfaces.py   # highspy / PuLP / Python-MIP
python3 scripts/tables/mippp_variants.py      # the four MIP++ build variants (Cbc)
```

Each script reads every CSV it needs at import time, so the corresponding
benchmarks must have been run first.
