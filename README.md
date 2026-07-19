The following table contains the time *in Milliseconds* requires by mippp to fill a N-Queens MILP model for each of the popular solvers supported.
These results are to be compared with the [Python-MIP benchmarks](https://python-mip.readthedocs.io/en/latest/bench.html#) of python interfaces.

| N    | Cbc  | CPLEX | Gurobi | Highs | MOSEK | SCIP  |
|------|------|-------|--------|-------|-------|-------|
| 100  | 1    | 1.2   | 3.6    | 1.1   | 2     | 15.7  |
| 200  | 6.7  | 4.7   | 7.8    | 4.3   | 4.4   | 26.3  |
| 300  | 8.4  | 9.9   | 14.7   | 10    | 7.7   | 57.5  |
| 400  | 15.4 | 18.9  | 24.7   | 18.6  | 14.9  | 98.3  |
| 500  | 29.9 | 29.4  | 36.2   | 31    | 21.2  | 152.2 |
| 600  | 30.8 | 44.8  | 53.7   | 45.2  | 31.7  | 222.3 |
| 700  | 43   | 63.1  | 70.8   | 64.7  | 48.7  | 305.2 |
| 800  | 72.5 | 86    | 92.7   | 92.2  | 57.9  | 404.6 |
| 900  | 92   | 106.2 | 120.8  | 116.9 | 69.4  | 523.2 |
| 1000 | 94.9 | 129.2 | 149.8  | 129.2 | 85.5  | 641.8 |

## MIP++ vs OR-Tools

The following table compares the time *in Milliseconds* required to fill the same N-Queens MILP model (N² binary variables, 6N-6 constraints) through MIP++ and through the OR-Tools `MPSolver` C++ API (`or-tools/9.15`), for the solvers supported by both.

| N    | Cbc MIP++ | Cbc OR-Tools | SCIP MIP++ | SCIP OR-Tools | Highs MIP++ | Highs OR-Tools |
|------|-----------|--------------|------------|---------------|-------------|----------------|
| 100  | 8.2       | 4.2          | 12.2       | 5.6           | 2.0         | 4.0            |
| 200  | 13.0      | 15.0         | 30.3       | 16.2          | 5.6         | 14.3           |
| 300  | 13.2      | 31.9         | 60.0       | 35.2          | 12.2        | 33.0           |
| 400  | 19.1      | 54.9         | 111.5      | 58.2          | 23.4        | 57.5           |
| 500  | 25.2      | 94.2         | 157.5      | 93.0          | 36.4        | 93.2           |
| 600  | 33.7      | 135.2        | 225.3      | 140.2         | 49.8        | 132.6          |
| 700  | 43.5      | 177.5        | 307.1      | 189.1         | 69.7        | 181.4          |
| 800  | 52.8      | 236.0        | 399.6      | 239.7         | 101.2       | 235.3          |
| 900  | 66.9      | 317.6        | 509.6      | 328.5         | 126.2       | 313.6          |
| 1000 | 78.1      | 401.6        | 638.6      | 406.4         | 148.0       | 396.0          |

Note that `MPSolver` stores the model in its own backend-independent data structures and only extracts it to the underlying solver when `Solve()` is called, which is why its fill times are nearly identical for all backends and exclude the actual solver load. The MIP++ (and Gurobi C API) timings instead include building the model in the solver's native in-memory representation. The OR-Tools `Gurobi` backend is also supported by `src/or_tools.cpp` but requires a valid Gurobi license at runtime.

## Reproducing the benchmarks

The numbers above were obtained on an AMD Ryzen 7 7800X3D (Ubuntu 22.04, GCC 15.1), with every benchmark compiled with the same compiler and flags (`-std=c++26`, `Release`).

### Requirements

- Linux, GCC >= 15 and [Conan](https://conan.io) >= 2.12 (the build uses the `CMakeConfigDeps` generator; CMake itself is provisioned by Conan).
- The [MIP++](https://github.com/fhamonic/mippp) Conan package (header-only, see below).
- OR-Tools is fetched and built from source automatically by Conan (`or-tools/9.15` with statically linked Cbc, SCIP and HiGHS backends), so the OR-Tools benchmarks need no license and no pre-installed solver.
- The `mippp`/`mippp_bulk` executables load the solvers' shared libraries at *runtime* (`dlopen`): install the ones you want to benchmark (Cbc, SCIP and HiGHS are free; Gurobi, CPLEX, MOSEK and COPT also require a license) and make them visible through `LD_LIBRARY_PATH`.
- The `gurobi_c`/`gurobi_c_bulk` executables (Gurobi C API) link against the Gurobi SDK and are only built when it is found: point the `GUROBI_DIR` (and, for another Gurobi version, `GUROBI_LIB`) CMake cache variables in `CMakeLists.txt` to your installation. Without it these two benchmarks are skipped and everything else still builds.

### Building

```sh
git clone https://github.com/fhamonic/mippp_nqueens
cd mippp_nqueens

# 1. install the Conan profile (adjust CC/CXX inside to your GCC >= 15)
cp profiles/gcc15_c++26 ~/.conan2/profiles/

# 2. export the header-only MIP++ package into your Conan cache
git clone https://github.com/fhamonic/mippp
conan create mippp -pr=gcc15_c++26 -b=missing

# 3. build the benchmarks (the first run also builds or-tools and its
#    dependency tree from source, which takes tens of minutes)
make
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
python3 scripts/benchmark.py   # writes one results/<Solver>_<api>.csv per benchmark
python3 scripts/tables.py      # prints the LaTeX comparison tables
```

Edit the `solvers` and `ortools_solvers` lists at the top of `scripts/benchmark.py` to match the solvers available on your machine. Each row of a results file is `N,num_variables,num_constraints,fill_time_ms`. The comparison tables against the Python-MIP, PuLP, gurobipy and JuMP interfaces are only printed for the `results/python-mip/queens-*.csv` files that are present (see below).

The executables can also be run individually, e.g. `./build/mippp SCIP 500`, `./build/or_tools Highs 1000` or `./build/gurobi_c 800`. They print their timings *in microseconds* on stderr (`solver,N,num_variables,num_constraints,api_time_us,fill_time_us` for `mippp*` and `or_tools`, the fill time only for `gurobi_c*`) and, for N < 20, also solve the instance and print the resulting board.

### Python and JuMP benchmarks

The Python-MIP, PuLP and gurobipy numbers are produced by the benchmark scripts of the [python-mip repository](https://github.com/coin-or/python-mip) (the same ones behind the published [Python-MIP benchmark](https://python-mip.readthedocs.io/en/latest/bench.html)), included here as the git submodule `extern/python-mip`, pinned at the commit that was used and completed by the one-line warm-up patch `patches/python-mip-queens-warmup.patch`. The JuMP numbers are produced by `jump/n-queens.jl`. The result files used for the tables in this README are committed under `results/python-mip/`; to regenerate them:

```sh
git submodule update --init
pip install mip pulp gurobipy timeout_decorator   # mip==1.15.0 was used here
scripts/benchmark_python.sh   # writes results/python-mip/queens-*.csv
```

The runner applies the warm-up patch to the submodule if needed and skips every benchmark whose interpreter, library or solver license is unavailable:

- the `*-pypy.csv` variants require `pypy3` with the `mip`, `pulp` and `timeout_decorator` packages installed;
- the gurobipy and Python-MIP/Gurobi benchmarks require a licensed Gurobi installation;
- the JuMP benchmark requires `julia` with the `JuMP` and `HiGHS` packages. As for the python benchmarks, a warm-up run is performed first so that the reported times exclude Julia's JIT compilation. Like OR-Tools' `MPSolver`, JuMP (in its default *cached* mode) builds the model in its own backend-independent representation, so its fill times exclude the actual solver load.
