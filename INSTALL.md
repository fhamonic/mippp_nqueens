# Installing the benchmark requirements

This document explains how to install everything needed to reproduce the
N-Queens modeling benchmarks on a clean **Ubuntu** machine. The instructions are
grouped by benchmark family — you only need the pieces for the interfaces you
actually want to run.

| Benchmark | What it needs |
|---|---|
| MIP++ (`build/mippp*`) | GCC ≥ 14, Conan ≥ 2.12, and each solver's shared library at runtime |
| OR-Tools (`build/or_tools`) | nothing extra — Conan builds it from source with Cbc/SCIP/HiGHS statically linked |
| Gurobi C API (`build/gurobi_c*`) | the Gurobi SDK + a license |
| Python interfaces | CPython + `highspy pulp mip gurobipy` |
| PyPy interfaces | PyPy + `pulp mip` |
| JuMP | Julia + `JuMP`, `Cbc`, `HiGHS` (optionally `GLPK`, `Gurobi`) |

Throughout, the machine is assumed to be Ubuntu 22.04 or newer with `sudo` rights.

---

## 1. C++ toolchain (GCC ≥ 14)

The C++ benchmarks are compiled at `-std=c++23` (or `c++26`) with GCC ≥ 14. If
your distribution does not ship it (Ubuntu versions prior to 24.04), add the toolchain PPA:

```bash
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install gcc-14 g++-14
```

Note the resulting paths (`which gcc-14 g++-14`) — the Conan profiles reference
them explicitly (see §3).

---

## 2. Conan (≥ 2.12)

Conan drives the C++ build and provisions CMake itself, so CMake does **not**
need to be installed separately.

```bash
sudo apt install python3-pip
pipx install "conan>=2.12"        # or: pip install --user "conan>=2.12"
conan --version                   # verify >= 2.12
```

---

## 3. Conan profiles

Two profiles ship with the repo: [profiles/gcc14_c++23](profiles/gcc14_c++23)
(used for the published numbers) and [profiles/gcc15_c++26](profiles/gcc15_c++26).

**Both hardcode the `CC`/`CXX` paths of the machine they were written on.** Edit
the `[buildenv]` block to point at your compiler before using them:

```ini
[buildenv]
CC=/usr/bin/gcc-14
CXX=/usr/bin/g++-14
```

You can either use the profile in place (`-pr=profiles/gcc14_c++23`, as below) or
copy it into `~/.conan2/profiles/` to make it a named default.

---

## 4. Building the C++ benchmarks

```bash
# 1. export the header-only MIP++ package into your Conan cache. MIP++ is not
#    vendored in this repository (it is gitignored), so clone it first.
git clone https://github.com/fhamonic/mippp
conan create mippp -pr=profiles/gcc14_c++23 -b=missing -c tools.build:skip_test=true

# 2. build the benchmarks — the first run also builds or-tools from source
conan build . -of=build -pr=profiles/gcc14_c++23 -b=missing
```

The executables land in `build/` (`build/mippp`, `build/mippp_distinct`,
`build/mippp_bulk`, `build/mippp_bulk_distinct`, `build/or_tools`, and
`build/gurobi_c*` when the Gurobi SDK is found — see §6).

> **or-tools build note:** or-tools 9.15 vendors a FlatZinc test that fails
> against the abseil version its recipe pins. If the build stops on
> `fzn-parser_test`, apply the source patch documented in
> [README.md](README.md#building) and re-run the `conan build` command.

---

## 5. Solvers for MIP++ at runtime (Cbc, HiGHS, …)

The `mippp*` executables do **not** link the solvers — they `dlopen` a solver's
shared library at runtime. For each backend MIP++ resolves the library in this
order (first match wins):

1. the `MIPPP_<KEY>_LIBRARY` environment variable pointing at the exact `.so`
   (e.g. `MIPPP_HIGHS_LIBRARY=/opt/highs/lib/libhighs.so`);
2. otherwise the loader's directories (`LD_LIBRARY_PATH`, `/etc/ld.so.conf*`,
   system library dirs) searched for the default soname below.

| Backend | `KEY` | soname(s) searched |
|---|---|---|
| Cbc | `CBC` | `libCbcSolver.so`, `libCbc.so` |
| HiGHS | `HIGHS` | `libhighs.so` |
| GLPK | `GLPK` | `libglpk.so` |
| SCIP | `SCIP` | `libscip.so` |
| Gurobi | `GUROBI` | `libgurobi120.so` |

### Cbc (free, from apt)

```bash
sudo apt install coinor-libcbc-dev coinor-libclp-dev
```

This installs `libCbcSolver.so` / `libClp.so` into a standard system directory,
so MIP++ finds them with no extra configuration.

### GLPK (free, optional, from apt)

```bash
sudo apt install libglpk-dev
```

### HiGHS (free)

On Ubuntu 25.04 or later, HiGHS is packaged:

```bash
sudo apt install highs libhighs1
```

Ubuntu 24.04 and earlier do not ship a usable `libhighs.so` in their default
repositories, so build it from source:

```bash
git clone https://github.com/ERGO-Code/HiGHS.git
cmake -S HiGHS -B HiGHS/build -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/opt/highs
cmake --build HiGHS/build -j --target install
```

Then expose it to MIP++ (add to `~/.bashrc` to make it permanent):

```bash
export MIPPP_HIGHS_LIBRARY=/opt/highs/lib/libhighs.so
# or, instead: export LD_LIBRARY_PATH=/opt/highs/lib:$LD_LIBRARY_PATH
```

> **Shortcut:** the `highspy` pip wheel (§7) already bundles a `libhighs`; you
> can point `MIPPP_HIGHS_LIBRARY` at the `.so` inside the installed package
> instead of building from source.

Solvers whose library is not found are simply skipped by the benchmark runners
(they print a `Skipped …` line and move on), so you only need the ones you care
about. The proprietary backends MIP++ can also load — CPLEX, MOSEK, COPT,
Xpress — follow the same `MIPPP_<KEY>_LIBRARY` pattern and each needs its own
license; they are not required to reproduce the free-solver tables.

---

## 6. Gurobi (academic license)

Gurobi is used three ways: the standalone C API benchmark (`build/gurobi_c*`),
the MIP++ / OR-Tools / JuMP / Python Gurobi backends, and `gurobipy`. All of
them share one SDK install + license.

### 6.1 Get an academic license

1. Register a free account at <https://portal.gurobi.com/iam/register/> using
   your **institutional (university) email address**.
2. On the portal, request a **Named-User Academic** license. The portal shows a
   `grbgetkey` command containing your license key.

### 6.2 Install the SDK

```bash
cd /opt
sudo wget https://packages.gurobi.com/12.0/gurobi12.0.1_linux64.tar.gz
sudo tar xzf gurobi12.0.1_linux64.tar.gz      # -> /opt/gurobi1201/
```

### 6.3 Activate the license

Run the command from the portal **while connected to your institution's network
or VPN** (academic activation validates the academic domain):

```bash
/opt/gurobi1201/linux64/bin/grbgetkey <your-key>   # writes ~/gurobi.lic
```

### 6.4 Environment

Add to `~/.bashrc`:

```bash
export GUROBI_HOME=/opt/gurobi1201/linux64
export PATH="$GUROBI_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$GUROBI_HOME/lib:$LD_LIBRARY_PATH"
```

With `GUROBI_HOME` set, re-running `conan build .` (§4) additionally produces
`build/gurobi_c` and `build/gurobi_c_bulk`, and MIP++ can `dlopen`
`libgurobi120.so` from `$GUROBI_HOME/lib` (matching the version linked here,
12.0.x). `gurobipy` and the Gurobi Python-MIP backend use the same license file.

---

## 7. Python interfaces (CPython)

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install highspy pulp mip gurobipy
```

- `highspy`, `pulp` and `mip` bundle a free Cbc/HiGHS, so they run out of the box.
- `gurobipy` and the Gurobi backend of Python-MIP need the licensed Gurobi from §6.

The benchmark scripts invoke the interpreter as `python`, so make sure `python`
resolves to the CPython where these packages are installed (activating the venv
above does this).

---

## 8. PyPy interfaces

The PuLP and Python-MIP benchmarks are also run under PyPy, invoked as `pypy3`.

```bash
sudo apt install pypy3                 # or download from https://pypy.org/download.html
pypy3 -m ensurepip
pypy3 -m pip install pulp mip          # the two pure-Python builders
```

`pypy3` must be on your `PATH`; the runners skip the PyPy columns gracefully if
it is missing. (gurobipy and highspy are C-extension heavy and are not run under
PyPy here.)

---

## 9. Julia + JuMP

Install Julia (the [`juliaup`](https://github.com/JuliaLang/juliaup) manager is
the simplest route):

```bash
curl -fsSL https://install.julialang.org | sh
# restart your shell, then:
julia --version
```

Add JuMP and the solver backends:

```julia
julia> import Pkg
julia> Pkg.add(["JuMP", "Cbc", "HiGHS"])          # required for the tabulated columns
julia> Pkg.add(["GLPK", "Gurobi"])                # optional extra backends
```

Notes:
- The `Cbc` and `HiGHS` Julia packages ship their own solver binaries: no system library is required for JuMP.
- The `Gurobi` Julia package needs `GUROBI_HOME` before running `Pkg.add("Gurobi")` (or `Pkg.build("Gurobi")` afterwards).
- `julia` must be on your `PATH`; [scripts/benchmark_jump.py](scripts/benchmark_jump.py) invokes it directly.

---

## 10. Running the benchmarks

Once the pieces you need are installed:

```bash
make all                              # runs every benchmark script
# or individually, e.g.:
python3 scripts/benchmark_mippp.py    # -> results/mippp/<solver>[_bulk][_distinct].csv
python3 scripts/benchmark_ortools.py
python3 scripts/benchmark_jump.py
python3 scripts/benchmark_pulp.py
```

Each runner writes CSV files under `results/`, skipping any solver or interpreter
it cannot find. The table scripts under [scripts/tables/](scripts/tables/) then
render the Markdown tables from those CSVs (standard library only — no extra
Python packages). See [README.md](README.md) for the full result discussion.
