The following table contains the time *in Milliseconds* requires by mippp to fill a N-Queens MILP model for each of the popular solvers supported.
These results are to be compared with the [Python-MIP benchmarks](https://python-mip.readthedocs.io/en/latest/bench.html#) of python interfaces.

| N | MIP++<br>Cbc | MIP++<br>HiGHS | OR-tools<br>Cbc | OR-tools<br>HiGHS | JuMP<br>Cbc | JuMP<br>HiGHS |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.9 ms | 1.2 ms | 3.8 x | 3.0 x | 13.7 x | 57.0 x |
| 200 | 3.3 ms | 5.1 ms | 4.1 x | 2.7 x | 30.4 x | 5.3 x |
| 300 | 7.0 ms | 11.5 ms | 4.5 x | 2.7 x | 10.6 x | 9.6 x |
| 400 | 12.3 ms | 21.1 ms | 4.4 x | 2.6 x | 15.2 x | 8.3 x |
| 500 | 18.6 ms | 35.0 ms | 4.9 x | 2.6 x | 13.9 x | 7.7 x |
| 600 | 28.2 ms | 49.8 ms | 4.6 x | 2.6 x | 12.4 x | 7.3 x |
| 700 | 37.7 ms | 67.3 ms | 4.7 x | 2.6 x | 14.8 x | 6.7 x |
| 800 | 47.9 ms | 100.2 ms | 4.7 x | 2.3 x | 12.7 x | 6.9 x |
| 900 | 60.1 ms | 124.8 ms | 5.1 x | 2.5 x | 13.4 x | 6.1 x |
| 1000 | 73.7 ms | 145.5 ms | 5.2 x | 2.6 x | 13.5 x | 6.6 x |

## MIP++ vs OR-Tools

The following table compares the time *in Milliseconds* required to fill the same N-Queens MILP model (N² binary variables, 6N-6 constraints) through MIP++ and through the OR-Tools `MPSolver` C++ API (`or-tools/9.15`), for the solvers supported by both.

| N | MIP++<br>Cbc | MIP++<br>HiGHS | MIP++<br>SCIP | OR-tools<br>Cbc | OR-tools<br>HiGHS | OR-tools<br>SCIP |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.9 ms | 1.2 ms | 8.3 ms | 3.8 x | 3.0 x | 0.4 x |
| 200 | 3.3 ms | 5.1 ms | 27.8 ms | 4.1 x | 2.7 x | 0.5 x |
| 300 | 7.0 ms | 11.5 ms | 61.0 ms | 4.5 x | 2.7 x | 0.5 x |
| 400 | 12.3 ms | 21.1 ms | 96.1 ms | 4.4 x | 2.6 x | 0.6 x |
| 500 | 18.6 ms | 35.0 ms | 149.1 ms | 4.9 x | 2.6 x | 0.6 x |
| 600 | 28.2 ms | 49.8 ms | 222.7 ms | 4.6 x | 2.6 x | 0.6 x |
| 700 | 37.7 ms | 67.3 ms | 310.6 ms | 4.7 x | 2.6 x | 0.6 x |
| 800 | 47.9 ms | 100.2 ms | 424.8 ms | 4.7 x | 2.3 x | 0.5 x |
| 900 | 60.1 ms | 124.8 ms | 538.9 ms | 5.1 x | 2.5 x | 0.6 x |
| 1000 | 73.7 ms | 145.5 ms | 690.2 ms | 5.2 x | 2.6 x | 0.6 x |

Note that `MPSolver` stores the model in its own backend-independent data structures and only extracts it to the underlying solver when `Solve()` is called, which is why its fill times are nearly identical for all backends and exclude the actual solver load. The MIP++ (and Gurobi C API) timings instead include building the model in the solver's native in-memory representation. The OR-Tools `Gurobi` backend is also supported by `src/or_tools.cpp` but requires a valid Gurobi license at runtime.

## Reproducing the benchmarks

The numbers above were obtained on an AMD Ryzen 7 7800X3D (Ubuntu 22.04, GCC 15.1), with every benchmark compiled with the same compiler and flags (`-std=c++26`, `Release`).

### Requirements

- Linux, GCC >= 14 and [Conan](https://conan.io) >= 2.12 (the build uses the `CMakeConfigDeps` generator; CMake itself is provisioned by Conan).
- The [MIP++](https://github.com/fhamonic/mippp) Conan package (header-only, see below).
- OR-Tools is fetched and built from source automatically by Conan (`or-tools/9.15` with statically linked Cbc, SCIP and HiGHS backends), so the OR-Tools benchmarks need no license and no pre-installed solver.
- The `mippp`/`mippp_bulk` executables load the solvers' shared libraries at *runtime* (`dlopen`): install the ones you want to benchmark (Cbc, SCIP and HiGHS are free; Gurobi, CPLEX, MOSEK and COPT also require a license) and make them visible through `LD_LIBRARY_PATH`.
- The `gurobi_c`/`gurobi_c_bulk` executables (Gurobi C API) link against the Gurobi SDK and are only built when it is found: point the `GUROBI_DIR` (and, for another Gurobi version, `GUROBI_LIB`) CMake cache variables in `CMakeLists.txt` to your installation. Without it these two benchmarks are skipped and everything else still builds.

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

Known issue: `or-tools/9.15` pins `CXX_STANDARD 17` on a few auxiliary targets, which fails against the abseil version pinned by its recipe (it requires C++20). If the or-tools build fails on `fzn-parser_test`, patch the cached sources and re-run `make`:

```sh
sed -i 's/CXX_STANDARD 17/CXX_STANDARD 20/' \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/flatzinc.cmake" \
    "$(conan cache path --folder=source or-tools/9.15)/src/cmake/glop.cmake"
make
```

### Running

```sh
python3 scripts/benchmark_mippp.py
python3 scripts/benchmark_ortools.py
python3 scripts/benchmark_gurobi.py

python3 scripts/benchmark_python.py
python3 scripts/benchmark_jump.py
```

### Python and JuMP benchmarks

The Python-MIP, PuLP and gurobipy numbers are produced by the benchmark scripts of the [python-mip repository](https://github.com/coin-or/python-mip) (the same ones behind the published [Python-MIP benchmark](https://python-mip.readthedocs.io/en/latest/bench.html)), included here as the git submodule `extern/python-mip`, pinned at the commit that was used and completed by the one-line warm-up patch `patches/python-mip-queens-warmup.patch`. The JuMP numbers are produced by `jump/n-queens.jl`. The result files used for the tables in this README are committed under `results/python-mip/`; to regenerate them:

```sh
git submodule update --init
pip install mip pulp gurobipy timeout_decorator   # mip==1.15.0 was used here
scripts/benchmark_python.sh
```

The runner applies the warm-up patch to the submodule if needed and skips every benchmark whose interpreter, library or solver license is unavailable:

- the `*-pypy.csv` variants require `pypy3` with the `mip`, `pulp` and `timeout_decorator` packages installed;
- the gurobipy and Python-MIP/Gurobi benchmarks require a licensed Gurobi installation;
- the JuMP benchmark requires `julia` with the `JuMP` and `HiGHS` packages. As for the python benchmarks, a warm-up run is performed first so that the reported times exclude Julia's JIT compilation. Like OR-Tools' `MPSolver`, JuMP (in its default *cached* mode) builds the model in its own backend-independent representation, so its fill times exclude the actual solver load.

| N | JuMP<br>Cbc | JuMP<br>HiGHS | Python-MIP<br>Cbc (CPython) | Python-MIP<br>Cbc (Pypy) | PuLP<br>Cbc (CPython) | PuLP<br>Cbc (Pypy) |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 13.0 ms | 66.6 ms | 12.3 x | 12.1 x | 10.6 x | 5.4 x |
| 200 | 99.8 ms | 26.7 ms | 8.1 x | 0.9 x | 9.2 x | 1.7 x |
| 300 | 74.1 ms | 111.0 ms | 36.9 x | 2.7 x | 40.0 x | 4.9 x |
| 400 | 187.0 ms | 174.4 ms | 36.2 x | 2.1 x | 39.3 x | 3.6 x |
| 500 | 257.9 ms | 270.7 ms | 50.7 x | 2.3 x | 54.5 x | 4.4 x |
| 600 | 348.6 ms | 365.0 ms | 64.1 x | 2.6 x | 70.1 x | 5.1 x |
| 700 | 558.7 ms | 450.9 ms | 64.8 x | 2.3 x | 70.3 x | 4.5 x |
| 800 | 606.3 ms | 689.3 ms | 88.1 x | 3.1 x | 96.9 x | 5.7 x |
| 900 | 802.8 ms | 759.6 ms | 94.9 x | 3.3 x | 104.7 x | 5.8 x |
| 1000 | 994.5 ms | 956.7 ms | 107.1 x | 3.3 x | 116.0 x | 6.1 x |
