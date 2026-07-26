# N-Queens modeling benchmarks

Support material for the JOSS submission of
[MIP++](https://github.com/fhamonic/mippp), a header-only C++ library for
building mixed-integer programs.

It measures how long it takes to **fill** a MILP model — never to solve it —
through eight modeling libraries spanning C++, Julia and Python, on up to seven
solver backends. The model is the classical N-Queens feasibility program: N²
binary variables and 6N−6 constraints (one per row, one per column, one per
diagonal), swept from N = 100 (10⁴ variables) to N = 1000 (10⁶ variables,
≈ 4 · 10⁶ nonzeros).

## Claims and where they are supported

| Claim | Evidence |
|---|---|
| The MIP++ modeling layer is essentially free: filling a model through it costs what calling the solver's own C API costs. | 99–104 % of the Gurobi C API across the whole sweep — [§ MIP++ vs the Gurobi C API](#mip-vs-the-gurobi-c-api) |
| MIP++ is 2.3–7.7× faster than the OR-Tools C++ APIs and 4–21× faster than JuMP, while being one of the only two that has the whole model in the solver when the timer stops. | [§ MIP++ vs OR-Tools](#mip-vs-or-tools), [§ MIP++ vs JuMP](#mip-vs-jump) |
| MIP++ is one to two orders of magnitude faster than the Python interfaces. | 12× gurobipy, ~50× Python-MIP, ~100× PuLP, ~140× highspy — [§ Python modeling interfaces](#python-modeling-interfaces) |
| This is a property of the library, not of one backend. | The same code path is measured against seven solver backends — [§ MIP++ across solver backends](#mip-across-solver-backends) |

## What is measured

> [!NOTE]
> **Only model construction is timed.** The timer starts once the solver API
> object exists and stops once the model holds all N² variables and all 6N−6
> constraints, after forcing any pending update to be flushed. No presolve, no
> optimization, no solution retrieval.

The interfaces compared are:

- **MIP++** — the library under review, one C++ source per build variant (`src/mippp*.cpp`);
- **the Gurobi C API**, per constraint (`GRBaddconstr`) and in bulk (`GRBaddconstrs`) — the reference floor;
- **OR-Tools' two C++ modeling APIs**, `MPSolver` and MathOpt (`or-tools/9.15`);
- **JuMP** (Julia), in both cached (`Model`) and direct (`direct_model`) mode;
- **the Python interfaces** gurobipy, highspy, PuLP and Python-MIP, each on CPython and, where relevant, on PyPy.

Every benchmark is self-contained in `src/`; no external repository or submodule
is needed to reproduce a column.

### Every model is written in its best-case form

In a high-level language it is easy to write a model whose *asymptotic* cost
exceeds that of the model it builds. The natural way to express the diagonal
constraints of N-Queens is to filter the whole board once per diagonal:

```python
lpSum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1
```

That walks N² cells to collect the N belonging to one diagonal, so filling a
model with Θ(N²) nonzeros costs Θ(N³). At N = 1000 this formulation costs the
PuLP model **115 s**, where indexing the cells of each diagonal directly builds
the very same model in **6.9 s** — a factor of 17, none of which happens inside
PuLP. JuMP admits the same trap when `LinearAlgebra.diag(reverse(x))` is left
inside the constraint loop instead of being hoisted out of it (see the comment
in [`src/jump_cached.jl`](src/jump_cached.jl)).

Every model here therefore touches only its own nonzeros, addressed by index,
with no scan of the board. The tables report a *floor*: the cost of the
interface layer itself, isolated as far as possible from the modeling code
sitting on top of it.

### Deferred vs. direct model construction

One structural difference explains most of the spread between interfaces, and it
is not the language. Both OR-Tools APIs and JuMP's default `Model` accumulate the
model in their own data structures and translate it for the solver later,
whereas MIP++, the Gurobi C API and JuMP's `direct_model` write into the
solver's own model as each constraint is added.

> [!IMPORTANT]
> The measurements are therefore **not comparing the same amount of work, and
> the bias is against MIP++**. Two independent tells confirm the deferral:
> JuMP's cached mode fills at the same speed whichever backend is named (888 ms
> for HiGHS, 887 ms for Gurobi at N = 1000), and `MPSolver` needs ~385 ms at
> N = 1000 for Cbc, HiGHS and SCIP alike. Wherever a deferred interface looks
> cheap, it has simply not handed the solver anything yet.

### Timing protocol

Each runner sweeps N from 100 to 1000 and reports the **median** of a number of
repetitions it picks itself: it repeats a point until the standard error of the
median drops under 1.5 %, capped at 25 repetitions and about five seconds per
point. Repetitions land where the noise is rather than where the time is — the
sub-millisecond C++ points are the jittery ones and cost nothing to repeat,
while the multi-second Python ones are consistent and stop at the floor of two.

Every repetition is a fresh process, so there is nothing to warm up and nothing
to discard — except for JuMP, where starting Julia and loading the solver
package costs seconds: there the build is repeated five times *inside* the
process and the median of those reported (the "warm" figure).

Each CSV records the `repetitions` spent on a point and the resulting
`error_pct`, so every number can be taken with the right amount of salt. A point
that hit the 25-repetition cap without reaching 1.5 % is called out on the
runner's `Done` line.

## Results

All numbers were obtained on an AMD Ryzen 7 7800X3D (Ubuntu 22.04), with every
C++ benchmark compiled by the same compiler and flags (GCC 14, `Release`,
`-std=c++23`, `-flto`), as configured by `profiles/gcc14_c++23`.

Unless stated otherwise, the MIP++ column is the `mippp_distinct` executable —
one constraint at a time, with the `distinct_variables` hint — which mirrors how
the OR-Tools, JuMP and Python models are written. [§ MIP++ build
variants](#mip-build-variants) justifies that choice.

> [!IMPORTANT]
> **Every Cbc figure below was obtained against Cbc's `devel` branch, not a
> released version.** Only `devel` caches `addRow` calls; the current release
> (2.10.13, and the `coinor-libcbc-dev` package built from it) flushes the
> matrix on every call instead, which dominates the fill time and makes Cbc look
> far slower than it is. Reproducing the Cbc columns with a released Cbc will
> therefore not give these numbers — see [§ Requirements](#requirements).

### Overview: the C++ and Julia interfaces

Time *in milliseconds* required by MIP++ to fill the model, and how much longer
each of the other C++/Julia interfaces takes on the same machine. HiGHS is the
one backend all of them share: MathOpt has no Cbc, and JuMP's direct mode needs
an incrementally modifiable backend, which the Cbc wrapper is not.

| N | MIP++ | <div align="center">OR-tools<br>MPSolver</div> | <div align="center">OR-tools<br>MathOpt</div> | <div align="center">JuMP<br>cached</div> | <div align="center">JuMP<br>direct</div> |
|:---:|---:|---:|---:|---:|---:|
| 100 | 1.5 ms | 2.4 x | 3.3 x | 4.1 x | 13.1 x |
| 200 | 5.6 ms | 2.4 x | 3.6 x | 4.8 x | 13.9 x |
| 300 | 13.5 ms | 2.3 x | 3.5 x | 4.3 x | 14.8 x |
| 400 | 22.2 ms | 2.4 x | 4.0 x | 8.0 x | 17.1 x |
| 500 | 34.1 ms | 2.6 x | 5.2 x | 6.8 x | 16.6 x |
| 600 | 54.8 ms | 2.4 x | 4.3 x | 6.1 x | 18.0 x |
| 700 | 68.2 ms | 2.5 x | 6.4 x | 6.3 x | 19.6 x |
| 800 | 95.9 ms | 2.3 x | 5.8 x | 5.8 x | 18.2 x |
| 900 | 116.3 ms | 2.6 x | 6.0 x | 6.0 x | 20.2 x |
| 1000 | 137.6 ms | 2.8 x | 7.7 x | 6.5 x | 21.1 x |

The three sections that follow break this down per interface, and the runners
also produce CSVs for every other backend they find at runtime.

### MIP++ vs the Gurobi C API

The most direct measure of MIP++'s overhead: the pure Gurobi C API in absolute
milliseconds, MIP++ as a *percentage* of it, and the other Gurobi-capable
interfaces as multiples of it.

| N | <div align="center">Gurobi C API<br>per constraint</div> | <div align="center">Gurobi C API<br>bulk</div> |  MIP++  | gurobipy | <div align="center">JuMP<br>warm</div> | <div align="center">JuMP<br>cold</div> | <div align="center">Python-MIP<br>CPython</div> | <div align="center">Python-MIP<br>PyPy</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 3.2 ms | 103.0 % | 99.3 % | 6.5 x | 3.7 x | 73.2 x | 19.7 x | 36.6 x |
| 200 | 8.3 ms | 105.8 % | 102.1 % | 9.0 x | 5.5 x | 40.2 x | 19.8 x | 17.6 x |
| 300 | 16.7 ms | 102.3 % | 102.8 % | 9.7 x | 7.3 x | 28.5 x | 19.3 x | 11.7 x |
| 400 | 29.3 ms | 102.6 % | 100.5 % | 9.7 x | 8.9 x | 19.1 x | 19.1 x | 9.4 x |
| 500 | 46.1 ms | 100.8 % | 99.3 % | 9.9 x | 8.0 x | 14.2 x | 18.7 x | 7.8 x |
| 600 | 66.0 ms | 101.4 % | 101.7 % | 10.6 x | 8.0 x | 13.5 x | 18.5 x | 7.2 x |
| 700 | 92.4 ms | 98.5 % | 102.0 % | 10.9 x | 7.7 x | 11.6 x | 18.1 x | 6.9 x |
| 800 | 120.6 ms | 99.9 % | 101.0 % | 11.5 x | 7.8 x | 10.4 x | 18.3 x | 6.9 x |
| 900 | 152.3 ms | 102.7 % | 103.7 % | 11.9 x | 7.7 x | 9.6 x | 18.7 x | 6.8 x |
| 1000 | 190.2 ms | 100.5 % | 103.1 % | 12.1 x | 7.5 x | 9.6 x | 18.4 x | 6.9 x |

MIP++ tracks the raw C API to within a few percent across the whole sweep
(≈ 99–104 %): **the modeling layer is essentially free.** Handing Gurobi the
whole matrix in a single `GRBaddconstrs` call instead of one `GRBaddconstr` per
constraint is worth nothing (98–106 %), so matching the per-constraint path is
the meaningful comparison rather than a handicap.

The JuMP columns are `direct_model`; the `cold` one includes Julia's JIT
compilation, paid once per process, and is the only figure in this README that
improves with N.

### MIP++ vs OR-Tools

OR-Tools ships two C++ modeling APIs and both are benchmarked:
`MPSolver` ([`src/or_tools_mpsolver.cpp`](src/or_tools_mpsolver.cpp)) and the
newer MathOpt ([`src/or_tools_mathopt.cpp`](src/or_tools_mathopt.cpp)). MIP++ in
absolute milliseconds, each OR-Tools API as a percentage of it:

| N | <div align="center">MIP++<br>Cbc</div> | <div align="center">MIP++<br>HiGHS</div> | <div align="center">MIP++<br>SCIP</div> | <div align="center">MPSolver<br>Cbc</div> | <div align="center">MPSolver<br>HiGHS</div> | <div align="center">MPSolver<br>SCIP</div> | <div align="center">MathOpt<br>HiGHS</div> | <div align="center">MathOpt<br>SCIP</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.8 ms | 1.5 ms | 8.9 ms | 422 % | 241 % | 40 % | 327 % | 55 % |
| 200 | 2.9 ms | 5.6 ms | 26.7 ms | 465 % | 245 % | 53 % | 361 % | 77 % |
| 300 | 6.3 ms | 13.5 ms | 60.9 ms | 507 % | 228 % | 52 % | 348 % | 74 % |
| 400 | 11.3 ms | 22.2 ms | 95.7 ms | 477 % | 241 % | 57 % | 401 % | 91 % |
| 500 | 17.3 ms | 34.1 ms | 147.2 ms | 524 % | 264 % | 62 % | 520 % | 111 % |
| 600 | 25.0 ms | 54.8 ms | 219.3 ms | 525 % | 236 % | 60 % | 432 % | 101 % |
| 700 | 33.2 ms | 68.2 ms | 310.5 ms | 537 % | 253 % | 58 % | 642 % | 131 % |
| 800 | 42.7 ms | 95.9 ms | 421.8 ms | 535 % | 234 % | 54 % | 577 % | 130 % |
| 900 | 55.0 ms | 116.3 ms | 550.6 ms | 572 % | 265 % | 58 % | 597 % | 124 % |
| 1000 | 67.0 ms | 137.6 ms | 680.4 ms | 573 % | 279 % | 58 % | 770 % | 156 % |

MIP++ fills the model 5–6× faster than `MPSolver` for Cbc and ~2.5× faster for
HiGHS; MathOpt is slower still, up to 7.7× MIP++ for HiGHS at N = 1000, and it
degrades as the model grows where `MPSolver` stays flat.

**SCIP is the exception in both columns, and it is the deferral effect of
[§ Deferred vs. direct model construction](#deferred-vs-direct-model-construction)
in its clearest form.** The OR-Tools fill time excludes the SCIP load entirely,
which is why it is nearly identical across backends; MIP++ builds directly in
SCIP's native representation, whose incremental build API is slow. MIP++ appears
"slower" for SCIP while doing strictly more work up front.

### MIP++ vs JuMP

`Model(optimizer)` puts a `CachingOptimizer` and the bridge layer between the
model and the solver; `direct_model(optimizer())` removes both, so every
`@variable` and `@constraint` goes straight into the solver's own model. Warm
build times (a rebuild inside an already-compiled process):

| N | <div align="center">JuMP · HiGHS<br>cached</div> | <div align="center">JuMP · HiGHS<br>direct</div> | <div align="center">JuMP · Gurobi<br>cached</div> | <div align="center">JuMP · Gurobi<br>direct</div> |
|:---:|---:|---:|---:|---:|
| 100 | 6.0 ms | 19.2 ms | 7.7 ms | 11.8 ms |
| 200 | 26.7 ms | 77.3 ms | 25.9 ms | 45.8 ms |
| 300 | 57.9 ms | 199.8 ms | 59.6 ms | 121.1 ms |
| 400 | 176.7 ms | 378.7 ms | 177.8 ms | 260.1 ms |
| 500 | 231.7 ms | 567.8 ms | 236.6 ms | 370.9 ms |
| 600 | 332.6 ms | 988.7 ms | 342.0 ms | 527.3 ms |
| 700 | 430.0 ms | 1339.8 ms | 441.0 ms | 707.3 ms |
| 800 | 556.4 ms | 1750.7 ms | 547.7 ms | 940.0 ms |
| 900 | 699.9 ms | 2351.1 ms | 712.9 ms | 1175.7 ms |
| 1000 | 888.3 ms | 2908.8 ms | 886.6 ms | 1424.9 ms |

Cutting out the caching layer makes filling the model *slower*, by 3.3× for
HiGHS and 1.6× for Gurobi — the price of actually depositing the model in the
solver as you go, and the same gap the C++ interfaces show between MIP++ and
`MPSolver`. The two solvers' incremental APIs differ enough to make direct mode
twice as expensive on HiGHS as on Gurobi, a difference the cached columns hide
completely.

Direct mode is the one to compare against MIP++, since it is the mode that has
the model in the solver when the timer stops. Against MIP++ on HiGHS (137.6 ms
at N = 1000), that is 21× for JuMP direct and 6.5× for JuMP cached.

### Python modeling interfaces

Self-contained builders in [`src/gurobi.py`](src/gurobi.py),
[`src/highs.py`](src/highs.py), [`src/pulp_.py`](src/pulp_.py) and
[`src/python-mip.py`](src/python-mip.py), timing a single build per model:

| N | <div align="center">gurobipy<br>Gurobi</div> | <div align="center">highspy<br>HiGHS</div> | <div align="center">PuLP<br>Cbc · CPython</div> | <div align="center">PuLP<br>Cbc · PyPy</div> | <div align="center">Python-MIP<br>Cbc · CPython</div> | <div align="center">Python-MIP<br>Cbc · PyPy</div> |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.02 s | 0.21 s | 0.06 s | 0.06 s | 0.08 s | 0.15 s |
| 200 | 0.07 s | 0.79 s | 0.22 s | 0.16 s | 0.18 s | 0.18 s |
| 300 | 0.16 s | 1.76 s | 0.50 s | 0.31 s | 0.34 s | 0.23 s |
| 400 | 0.29 s | 3.09 s | 0.92 s | 0.53 s | 0.57 s | 0.31 s |
| 500 | 0.46 s | 4.92 s | 1.50 s | 0.85 s | 0.87 s | 0.40 s |
| 600 | 0.70 s | 7.01 s | 2.34 s | 1.28 s | 1.25 s | 0.54 s |
| 700 | 1.01 s | 9.47 s | 3.20 s | 1.81 s | 1.71 s | 0.71 s |
| 800 | 1.39 s | 12.32 s | 4.38 s | 2.38 s | 2.23 s | 0.91 s |
| 900 | 1.81 s | 15.70 s | 5.69 s | 3.13 s | 2.90 s | 1.13 s |
| 1000 | 2.30 s | 19.50 s | 6.89 s | 3.77 s | 3.58 s | 1.42 s |

Against MIP++ on the same backend, the whole Python field costs one to two
orders of magnitude more: 12× for gurobipy, ~50× for CPython Python-MIP, ~100×
for CPython PuLP and ~140× for highspy. (The Gurobi Python-MIP columns are in
the [Gurobi table](#mip-vs-the-gurobi-c-api) above.)

Two secondary observations, reported for completeness rather than as claims
about MIP++: `highspy` is the slowest of the five despite being a thin binding
over a C++ solver, because a `highspy` integer variable takes two calls
(`addVar` then `changeColIntegrality`) and each `addRow` hands over freshly
built Python lists; and PyPy's JIT is worth 1.8–2.5× at N = 1000 but nothing at
N = 100, where it never warms up inside a process that builds a single model.

### MIP++ across solver backends

The same `mippp` executable, one constraint at a time, against every backend
whose shared library was found at runtime. This is the cost of the solver's own
model-building API plus MIP++'s (near-zero) overhead, so the spread is the
solvers':

| N | Cbc | MOSEK | HiGHS | CPLEX | Gurobi | GLPK | SCIP |
|:---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.9 ms | 2.2 ms | 1.5 ms | 1.4 ms | 3.3 ms | 1.6 ms | 8.4 ms |
| 200 | 3.1 ms | 4.2 ms | 5.9 ms | 5.8 ms | 9.0 ms | 6.9 ms | 27.8 ms |
| 300 | 6.8 ms | 8.3 ms | 14.4 ms | 14.3 ms | 17.5 ms | 15.6 ms | 59.9 ms |
| 400 | 12.5 ms | 12.7 ms | 23.0 ms | 24.1 ms | 30.1 ms | 28.0 ms | 94.0 ms |
| 500 | 19.4 ms | 18.8 ms | 35.7 ms | 44.1 ms | 47.5 ms | 52.3 ms | 146.8 ms |
| 600 | 28.6 ms | 29.9 ms | 57.5 ms | 60.6 ms | 71.4 ms | 78.1 ms | 220.4 ms |
| 700 | 37.6 ms | 37.6 ms | 73.8 ms | 78.2 ms | 95.8 ms | 124.7 ms | 306.0 ms |
| 800 | 49.1 ms | 48.7 ms | 103.6 ms | 108.4 ms | 128.3 ms | 161.6 ms | 410.9 ms |
| 900 | 61.5 ms | 61.9 ms | 122.6 ms | 161.3 ms | 160.5 ms | 235.9 ms | 537.8 ms |
| 1000 | 74.1 ms | 74.2 ms | 144.3 ms | 195.7 ms | 197.5 ms | 256.1 ms | 677.9 ms |

Cbc and MOSEK accept the model fastest and SCIP is an order of magnitude behind
the rest. Normalised by model size, most backends are flat across the sweep;
GLPK (×1.5 from N = 200 to N = 1000) and CPLEX (×1.3) cost progressively more
per nonzero as the model grows.

Cbc leads this table only because its `devel` branch caches `addRow` calls; on
the 2.10.13 release, which rebuilds the matrix at every call, the same code is
far slower. This is a property of the solver's build API, not of MIP++, and it
is the clearest illustration of what the column actually measures.

### MIP++ build variants

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
coefficient-merging step it would otherwise perform. In N-Queens every
constraint genuinely has distinct variables, so the hint is an idiomatic use
rather than a shortcut.

Both axes are backend-dependent. At N = 1000, as a percentage of that backend's
one-at-a-time time:

| backend | one-at-a-time | + distinct | bulk | bulk + distinct |
|:---:|---:|---:|---:|---:|
| Cbc | 74.1 ms | 90 % | 99 % | 91 % |
| MOSEK | 74.2 ms | 91 % | 113 % | 106 % |
| HiGHS | 144.3 ms | 95 % | 100 % | 95 % |
| CPLEX | 195.7 ms | 95 % | 69 % | 64 % |
| Gurobi | 197.5 ms | 99 % | 106 % | 104 % |
| GLPK | 256.1 ms | — | 104 % | — |
| SCIP | 677.9 ms | 100 % | 99 % | 99 % |

The `distinct_variables` hint never hurts: 5–10 % for Cbc, MOSEK and HiGHS, and
nothing at all for SCIP, whose own build API dominates. Bulk cuts both ways —
worth 31 % for CPLEX, worth nothing for Cbc, HiGHS and SCIP, and
*counter*-productive for MOSEK (+13 %) and Gurobi (+6 %), whose per-constraint
entry points are already the fast path. The same one-at-a-time / bulk split
exists for the Gurobi C API and buys nothing there either (see the
[Gurobi table](#mip-vs-the-gurobi-c-api)).

This is why the MIP++ figures elsewhere come from `mippp_distinct`: it is the
per-constraint variant, comparable to how every other interface is used, and the
hint is a legitimate property of this model. The backend table above uses plain
`mippp` so that GLPK can appear in it (see the limitations below).

## Limitations

- **The comparison is not work-for-work.** The deferred interfaces (`MPSolver`, MathOpt, JuMP cached) have less of the model in the solver when their timer stops. This is documented in [§ Deferred vs. direct model construction](#deferred-vs-direct-model-construction) and is the main caveat on every cross-interface ratio.
- **Single machine, single compiler.** All numbers come from one AMD Ryzen 7 7800X3D running Ubuntu 22.04 with GCC 14. Absolute times are machine-dependent; the ratios are the transferable quantity.
- **The Cbc columns need an unreleased Cbc.** They were measured against the `devel` branch, the only version that caches `addRow` calls; on release 2.10.13 every direct-building interface is substantially slower on Cbc. The Cbc figures are therefore not reproducible from a distribution package today.
- **`mippp_distinct` and `mippp_bulk_distinct` abort on GLPK** (`glp_set_mat_row: ind[1] = 0; column index out of range`): the hinted path hands GLPK 0-based column indices where its API is 1-based. GLPK therefore has no `distinct` figure and appears only via plain `mippp`.
- **Backends without a license here are reported as skipped, not measured.** COPT and Xpress are wired up in `src/mippp.cpp` and their libraries load, but neither had a usable license on this machine (COPT's check fails, the Xpress license expired), so both abort on a `mippp::license_error`.
- **OR-Tools' Gurobi paths could not be measured** and do not fail gracefully: `MPSolver` segfaults and MathOpt throws an uncaught `std::bad_function_call` when no Gurobi license is available. MathOpt has no Cbc backend at all, and Conan's or-tools recipe does not build the GLPK one.
- **Only model construction is characterised.** Nothing here says anything about solve time, memory footprint, or the quality of the models produced.

## Reproducing the benchmarks

[INSTALL.md](INSTALL.md) documents the full dependency setup, benchmark family
by benchmark family, on a clean Ubuntu machine. The short version:

### Requirements

- Linux, GCC ≥ 14 and [Conan](https://conan.io) ≥ 2.12 (CMake is provisioned by Conan).
- The [MIP++](https://github.com/fhamonic/mippp) Conan package (header-only, exported below).
- OR-Tools is fetched and built from source automatically by Conan (`or-tools/9.15`, with Cbc, SCIP and HiGHS statically linked), so its benchmarks need no license and no pre-installed solver.
- The `mippp*` executables `dlopen` the solvers' shared libraries at *runtime*: install the ones you want (Cbc, GLPK, SCIP and HiGHS are free) and make them visible through `LD_LIBRARY_PATH` or `MIPPP_<KEY>_LIBRARY`. Missing solvers are skipped, not fatal.
- **Cbc must be built from the `devel` branch to reproduce the Cbc columns** ([building from source](https://github.com/coin-or/Cbc#building-from-source)). Only `devel` caches `addRow` calls; release 2.10.13 — which is what `apt install coinor-libcbc-dev` provides — flushes the matrix at every call and yields substantially slower figures for every interface that builds directly in Cbc.
- The `gurobi_c`/`gurobi_c_bulk` executables link the Gurobi SDK and are built only when `GUROBI_HOME` is set.
- Python: `pip install highspy pulp mip gurobipy`; for the PyPy columns, `pulp` and `mip` under `pypy3` as well.
- Julia with `JuMP`, `Cbc` and `HiGHS` added (optionally `Gurobi`).

> [!WARNING]
> Two Conan profiles ship with the repository, `profiles/gcc14_c++23` (used for
> the numbers above) and `profiles/gcc15_c++26`. **Both hardcode the `CC`/`CXX`
> paths of the machine they were written on**; edit them to point at your own
> GCC before building.

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

Executables are produced directly in `build/`.

> [!WARNING]
> `or-tools/9.15` pins `CXX_STANDARD 17` on a few auxiliary targets, which fails
> against the abseil version its recipe pins (that requires C++20). If the
> or-tools build stops on `fzn-parser_test`, patch the sources in the Conan
> cache and re-run the `conan build` command above:
>
> ```sh
> sed -i 's/CXX_STANDARD 17/CXX_STANDARD 20/' \
>     "$(conan cache path --folder=source or-tools/9.15)/src/cmake/flatzinc.cmake" \
>     "$(conan cache path --folder=source or-tools/9.15)/src/cmake/glop.cmake"
> ```

### Running

`make all` runs everything; the individual runners (all from the repository
root) are:

```sh
python3 scripts/benchmark_mippp.py        # -> results/mippp/<solver>[_bulk][_distinct].csv
python3 scripts/benchmark_or-tools.py     # -> results/or-tools/<solver>_<interface>.csv
python3 scripts/benchmark_gurobi.py       # -> results/gurobi/gurobi_c[_bulk].csv
python3 scripts/benchmark_gurobipy.py     # -> results/gurobi/gurobipy.csv
python3 scripts/benchmark_highspy.py      # -> results/highs/highspy.csv
python3 scripts/benchmark_jump.py         # -> results/jump/<solver>_<interface>.csv
python3 scripts/benchmark_pulp.py         # -> results/pulp/<python>.csv
python3 scripts/benchmark_python-mip.py   # -> results/python-mip/<python>_<solver>.csv
```

Solvers, packages or licenses missing at runtime are reported as skipped and
produce no CSV; every runner overwrites its own CSVs on each run. `results/` is
gitignored, so no CSV is committed.

> [!NOTE]
> The runners spawn CPython as `python` (and PyPy as `pypy3`), so make sure
> `python` on your `PATH` resolves to the interpreter where the packages are
> installed — on a stock Ubuntu that ships only `python3`, activate a virtualenv
> or install `python-is-python3`.

### Regenerating the tables

Every table above is rendered from the CSV files by a script under
`scripts/tables/` (standard library only). Each reads the CSVs it needs at
import time, so the corresponding benchmarks must have been run first.

| Section | Script |
|---|---|
| [Overview: the C++ and Julia interfaces](#overview-the-c-and-julia-interfaces) | `mippp_vs_others.py` |
| [MIP++ vs the Gurobi C API](#mip-vs-the-gurobi-c-api) | `gurobi_vs_mippp.py` |
| [MIP++ vs OR-Tools](#mip-vs-or-tools) | `mippp_vs_or-tools.py` |
| [MIP++ vs JuMP](#mip-vs-jump) | `jump_modes.py` |
| [Python modeling interfaces](#python-modeling-interfaces) | `python_interfaces.py` |
| [MIP++ across solver backends](#mip-across-solver-backends) | `mippp_backends.py` |
| [MIP++ build variants](#mip-build-variants) | `mippp_variants_summary.py` (the N = 1000 table shown); `mippp_variants.py` renders the same four variants across the whole sweep for Cbc |

## Repository layout

| Path | Contents |
|---|---|
| [`src/`](src/) | one self-contained model builder per interface and variant |
| [`scripts/`](scripts/) | benchmark runners, one per interface family, writing CSVs to `results/` |
| [`scripts/tables/`](scripts/tables/) | CSV → Markdown table renderers |
| [`profiles/`](profiles/) | Conan profiles pinning compiler and standard |
