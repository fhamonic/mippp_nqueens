# N-Queens modeling benchmarks

Support material for the JOSS submission of
[MIP++](https://github.com/fhamonic/mippp), a header-only C++ library for
building mixed-integer programs.

It measures how long it takes to **fill** a MILP model — never to solve it —
through eight modeling libraries spanning C++, Julia and Python, on up to eight
solver backends. The model is the classical N-Queens feasibility program: N²
binary variables and 6N−6 constraints (one per row, one per column, one per
diagonal), swept from N = 100 (10⁴ variables) to N = 1000 (10⁶ variables,
≈ 4 · 10⁶ nonzeros).

## Claims and where they are supported

| Claim | Key figure | Section |
|---|---|---|
| The MIP++ modeling layer is thin: filling a model through it costs close to what calling the solver's own C API costs. | 102–108 % of the Gurobi C API, whole sweep | [§ MIP++ vs the Gurobi C API](#mip-vs-the-gurobi-c-api) |
| On HiGHS, the one backend every C++/Julia interface here supports, MIP++ fills the model faster than all of them — each competitor taken in its own fastest form. | 1.2–1.3× `MPSolver`, 2.6–5.6× MathOpt, 3.7–7.3× JuMP cached, 12–18× JuMP direct | [§ Overview](#overview-the-c-and-julia-interfaces), [§ vs OR-Tools](#mip-vs-or-tools), [§ vs JuMP](#mip-vs-jump) |
| MIP++ is one to two orders of magnitude faster than the Python interfaces. | at N = 1000: 11× gurobipy, 54× Python-MIP, 103× PuLP, 128× highspy | [§ Python modeling interfaces](#python-modeling-interfaces) |
| This is a property of the library, not of one backend. | the same code path against eight solver backends | [§ MIP++ across solver backends](#mip-across-solver-backends) |

Every table below is regenerated from the CSVs committed in [`results/`](results/)
by a script in [`scripts/tables/`](scripts/tables/); the mapping from section to
script to CSV is in [§ Regenerating the
tables](#regenerating-the-tables). The one caveat that applies to every
cross-interface ratio is [§ Deferred vs. direct model
construction](#deferred-vs-direct-model-construction): MIP++ has the whole model
in the solver when its timer stops, and the interfaces it is compared against
mostly do not — the bias is against MIP++.

## What is measured

> [!NOTE]
> **Only model construction is timed.** The timer starts once the solver API
> object exists and stops once the model holds all N² variables and all 6N−6
> constraints, after forcing any pending update to be flushed. No presolve, no
> optimization, no solution retrieval.

The interfaces compared are:

- **MIP++** — the library under review, one C++ source per build variant (`src/mippp*.cpp`);
- **the Gurobi C API**, per constraint (`GRBaddconstr`) and in bulk (`GRBaddconstrs`) — the reference floor;
- **OR-Tools' two C++ modeling APIs**, `MPSolver` and MathOpt (`or-tools/9.15`), each in the faster of the two ways it offers to fill a row (see [§ Both OR-Tools APIs have a faster way to fill a row](#both-or-tools-apis-have-a-faster-way-to-fill-a-row));
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
model with Θ(N²) nonzeros costs Θ(N³). Measured once at N = 1000 (not part of
the sweep, so no CSV): **115 s** for the PuLP model that way, against the
**6.9 s** the committed `results/pulp/python.csv` reports for the very same
model with each diagonal's cells indexed directly — a factor of 17, none of
which happens inside PuLP. JuMP admits the same trap when
`LinearAlgebra.diag(reverse(x))` is left inside the constraint loop instead of
being hoisted out of it (see the comment in
[`src/jump_cached.jl`](src/jump_cached.jl)).

Every model here therefore touches only its own nonzeros, addressed by index,
with no scan of the board — and where an interface offers several ways to hand
over a row, the fastest one is used: both OR-Tools APIs write coefficients
straight into the row instead of going through an expression object, worth
~1.8× for `MPSolver` and ~1.2× for MathOpt ([§ Both OR-Tools APIs have a faster
way to fill a row](#both-or-tools-apis-have-a-faster-way-to-fill-a-row)). The
tables report a *floor*: the cost of the interface layer itself, isolated as far
as possible from the modeling code sitting on top of it.

### Deferred vs. direct model construction

One structural difference explains most of the spread between interfaces, and it
is not the language. Both OR-Tools APIs and JuMP's default `Model` accumulate the
model in their own data structures and translate it for the solver later,
whereas MIP++, the Gurobi C API and JuMP's `direct_model` write into the
solver's own model as each constraint is added.

> [!IMPORTANT]
> The measurements are therefore **not comparing the same amount of work, and
> the bias is against MIP++**. Two independent tells confirm the deferral:
> JuMP's cached mode fills at the same speed whichever backend is named (867 ms
> for HiGHS, 873 ms for Gurobi at N = 1000), and `MPSolver` needs ~200–220 ms at
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
`error_pct`, so every number can be taken with the right amount of salt. In the
committed results, 37 of the 570 points miss the 1.5 % target — 26 of them by
less than a point, 11 by more. They are not spread evenly: half are JuMP, where
one repetition costs seconds so the budget stops the sampling at two, and that
is also where the single worst point sits (HiGHS direct at N = 500, 10.7 %); the
rest are mostly Xpress, whose own build API stays erratic even at the
25-repetition cap (up to 4.6 %). Ratios drawn from those two should be read with
`error_pct` next to them; nothing else in this README turns on a difference that
small.

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

<!-- table:mippp_vs_others -->
| N | MIP++ | <div align="center">OR-tools<br>MPSolver</div> | <div align="center">OR-tools<br>MathOpt</div> | <div align="center">JuMP<br>cached</div> | <div align="center">JuMP<br>direct</div> |
|:---:|---:|---:|---:|---:|---:|
| 100 | 1.6 ms | 1.3 x | 2.6 x | 3.7 x | 12.0 x |
| 200 | 5.8 ms | 1.3 x | 2.8 x | 4.6 x | 13.2 x |
| 300 | 14.4 ms | 1.3 x | 2.6 x | 4.4 x | 12.8 x |
| 400 | 23.7 ms | 1.3 x | 3.1 x | 7.3 x | 15.0 x |
| 500 | 37.4 ms | 1.3 x | 3.7 x | 6.1 x | 16.1 x |
| 600 | 59.1 ms | 1.2 x | 3.1 x | 5.5 x | 16.3 x |
| 700 | 75.0 ms | 1.3 x | 4.7 x | 5.8 x | 17.2 x |
| 800 | 104.1 ms | 1.2 x | 4.2 x | 5.3 x | 16.6 x |
| 900 | 127.0 ms | 1.3 x | 4.0 x | 5.4 x | 17.8 x |
| 1000 | 151.5 ms | 1.3 x | 5.6 x | 5.7 x | 18.3 x |
<!-- /table -->

The three sections that follow break this down per interface, and the runners
also produce CSVs for every other backend they find at runtime.

### MIP++ vs the Gurobi C API

The most direct measure of MIP++'s overhead: the pure Gurobi C API in absolute
milliseconds, MIP++ as a *percentage* of it, and the other Gurobi-capable
interfaces as multiples of it.

<!-- table:gurobi_vs_mippp -->
| N | <div align="center">Gurobi C API<br>per constraint</div> | <div align="center">Gurobi C API<br>bulk</div> | MIP++ | gurobipy | <div align="center">JuMP<br>warm</div> | <div align="center">JuMP<br>cold</div> | <div align="center">Python-MIP<br>CPython</div> | <div align="center">Python-MIP<br>PyPy</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 3.2 ms | 99.1 % | 102.3 % | 6.5 x | 3.5 x | 69.4 x | 19.4 x | 36.5 x |
| 200 | 9.0 ms | 98.1 % | 102.5 % | 8.2 x | 5.0 x | 36.2 x | 18.3 x | 16.4 x |
| 300 | 17.5 ms | 103.9 % | 104.3 % | 9.4 x | 6.4 x | 23.9 x | 18.9 x | 11.2 x |
| 400 | 29.8 ms | 101.1 % | 105.4 % | 9.7 x | 8.3 x | 18.0 x | 18.8 x | 9.2 x |
| 500 | 48.2 ms | 95.6 % | 103.5 % | 9.6 x | 7.5 x | 13.2 x | 17.8 x | 7.5 x |
| 600 | 68.1 ms | 100.6 % | 103.3 % | 10.4 x | 7.5 x | 12.8 x | 18.2 x | 7.1 x |
| 700 | 93.1 ms | 99.5 % | 106.8 % | 11.3 x | 7.4 x | 11.3 x | 18.1 x | 6.9 x |
| 800 | 122.2 ms | 100.3 % | 107.0 % | 11.7 x | 7.5 x | 10.0 x | 18.1 x | 6.9 x |
| 900 | 154.1 ms | 101.3 % | 108.4 % | 12.0 x | 7.5 x | 9.2 x | 18.4 x | 6.7 x |
| 1000 | 190.0 ms | 101.7 % | 107.3 % | 12.3 x | 7.4 x | 9.3 x | 18.5 x | 6.9 x |
<!-- /table -->

MIP++ stays within 2–8 % of the raw C API across the whole sweep (102–108 %):
**the modeling layer is thin.** Handing Gurobi the
whole matrix in a single `GRBaddconstrs` call instead of one `GRBaddconstr` per
constraint is worth nothing (96–104 %), so matching the per-constraint path is
the meaningful comparison rather than a handicap.

The JuMP columns are `direct_model`; the `cold` one includes Julia's JIT
compilation, paid once per process, which is why it improves with N — as does
the Python-MIP PyPy column, for the same reason.

### MIP++ vs OR-Tools

OR-Tools ships two C++ modeling APIs and both are benchmarked: `MPSolver`
([`src/or_tools_mpsolver_setcoef.cpp`](src/or_tools_mpsolver_setcoef.cpp)) and
the newer MathOpt
([`src/or_tools_mathopt_setcoef.cpp`](src/or_tools_mathopt_setcoef.cpp)), each
in its fastest row-filling form. MIP++ in absolute milliseconds, each OR-Tools
API as a percentage of it:

<!-- table:mippp_vs_or-tools -->
| N | <div align="center">MIP++<br>Cbc</div> | <div align="center">MIP++<br>HiGHS</div> | <div align="center">MIP++<br>SCIP</div> | <div align="center">MPSolver<br>Cbc</div> | <div align="center">MPSolver<br>HiGHS</div> | <div align="center">MPSolver<br>SCIP</div> | <div align="center">MathOpt<br>HiGHS</div> | <div align="center">MathOpt<br>SCIP</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.8 ms | 1.6 ms | 7.5 ms | 244 % | 127 % | 28 % | 260 % | 56 % |
| 200 | 2.9 ms | 5.8 ms | 24.1 ms | 269 % | 134 % | 34 % | 281 % | 69 % |
| 300 | 6.3 ms | 14.4 ms | 51.7 ms | 294 % | 127 % | 36 % | 262 % | 71 % |
| 400 | 11.0 ms | 23.7 ms | 85.1 ms | 279 % | 129 % | 37 % | 314 % | 89 % |
| 500 | 17.2 ms | 37.4 ms | 124.3 ms | 291 % | 132 % | 43 % | 371 % | 114 % |
| 600 | 24.8 ms | 59.1 ms | 181.9 ms | 293 % | 121 % | 42 % | 312 % | 103 % |
| 700 | 34.4 ms | 75.0 ms | 244.0 ms | 280 % | 127 % | 43 % | 467 % | 143 % |
| 800 | 44.6 ms | 104.1 ms | 315.8 ms | 277 % | 118 % | 42 % | 419 % | 135 % |
| 900 | 55.7 ms | 127.0 ms | 397.6 ms | 301 % | 134 % | 46 % | 404 % | 132 % |
| 1000 | 66.7 ms | 151.5 ms | 482.2 ms | 301 % | 134 % | 45 % | 560 % | 175 % |
<!-- /table -->

MIP++ fills the model 2.4–3.0× faster than `MPSolver` for Cbc and 1.2–1.3× faster
for HiGHS; MathOpt is slower still, up to 5.6× MIP++ for HiGHS at N = 1000, and it
degrades as the model grows where `MPSolver` stays flat.

**SCIP is the exception in both columns, and it is the deferral effect of
[§ Deferred vs. direct model construction](#deferred-vs-direct-model-construction)
in its clearest form.** The OR-Tools fill time excludes the SCIP load entirely,
which is why it is nearly identical across backends; MIP++ builds directly in
SCIP's native representation, whose incremental build API is slow. MIP++ appears
"slower" for SCIP while doing strictly more work up front.

#### Both OR-Tools APIs have a faster way to fill a row

The idiomatic way to fill a row is an expression object — `LinearExpr`
([src](src/or_tools_mpsolver.cpp)) or `LinearExpression`
([src](src/or_tools_mathopt.cpp)) — which accumulates the terms in a hash map
before the finished row is handed over. Both APIs also let the row be opened
first and its coefficients written straight into it: `MakeRowConstraint(lb, ub)`
+ `SetCoefficient` ([src](src/or_tools_mpsolver_setcoef.cpp)) and
`AddLinearConstraint(lb, ub)` + `set_coefficient`
([src](src/or_tools_mathopt_setcoef.cpp)). Same model, same backends; the
coefficient form in milliseconds, the expression form as a percentage of it:

<!-- table:or-tools_modes -->
| N | <div align="center">MPSolver<br>SetCoefficient<br>Cbc</div> | <div align="center">MPSolver<br>SetCoefficient<br>HiGHS</div> | <div align="center">MPSolver<br>SetCoefficient<br>SCIP</div> | <div align="center">MPSolver<br>LinearExpr<br>Cbc</div> | <div align="center">MPSolver<br>LinearExpr<br>HiGHS</div> | <div align="center">MPSolver<br>LinearExpr<br>SCIP</div> | <div align="center">MathOpt<br>set_coefficient<br>HiGHS</div> | <div align="center">MathOpt<br>set_coefficient<br>SCIP</div> | <div align="center">MathOpt<br>LinearExpression<br>HiGHS</div> | <div align="center">MathOpt<br>LinearExpression<br>SCIP</div> |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 2.0 ms | 2.0 ms | 2.1 ms | 175 % | 181 % | 178 % | 4.1 ms | 4.2 ms | 120 % | 118 % |
| 200 | 7.9 ms | 7.8 ms | 8.3 ms | 170 % | 177 % | 165 % | 16.4 ms | 16.6 ms | 122 % | 117 % |
| 300 | 18.5 ms | 18.2 ms | 18.7 ms | 173 % | 172 % | 171 % | 37.7 ms | 36.7 ms | 119 % | 122 % |
| 400 | 30.6 ms | 30.7 ms | 31.3 ms | 179 % | 176 % | 174 % | 74.5 ms | 75.9 ms | 118 % | 116 % |
| 500 | 50.1 ms | 49.5 ms | 54.0 ms | 183 % | 181 % | 171 % | 139.1 ms | 141.5 ms | 123 % | 117 % |
| 600 | 72.4 ms | 71.7 ms | 76.6 ms | 180 % | 185 % | 182 % | 184.3 ms | 187.0 ms | 126 % | 121 % |
| 700 | 96.2 ms | 95.5 ms | 104.6 ms | 187 % | 188 % | 176 % | 349.9 ms | 349.0 ms | 121 % | 121 % |
| 800 | 123.6 ms | 122.9 ms | 133.4 ms | 186 % | 186 % | 175 % | 435.9 ms | 425.7 ms | 122 % | 125 % |
| 900 | 167.9 ms | 170.3 ms | 181.9 ms | 189 % | 184 % | 175 % | 513.0 ms | 526.1 ms | 131 % | 128 % |
| 1000 | 201.1 ms | 203.5 ms | 218.0 ms | 190 % | 188 % | 178 % | 848.6 ms | 845.3 ms | 122 % | 124 % |
<!-- /table -->

Going through an expression object costs `MPSolver` 1.6–1.9× (widening with N)
and MathOpt a flat ~1.2×. The coefficient form is what every other OR-Tools
figure in this README uses, so **OR-Tools is always shown at its best** — and at
its most verbose, a loop opening a row and writing N coefficients into it where
MIP++ and the expression form both state the constraint as a sum.

### MIP++ vs JuMP

`Model(optimizer)` puts a `CachingOptimizer` and the bridge layer between the
model and the solver; `direct_model(optimizer())` removes both, so every
`@variable` and `@constraint` goes straight into the solver's own model. Warm
build times (a rebuild inside an already-compiled process):

<!-- table:jump_modes -->
| N | <div align="center">JuMP · HiGHS<br>cached</div> | <div align="center">JuMP · HiGHS<br>direct</div> | <div align="center">JuMP · Gurobi<br>cached</div> | <div align="center">JuMP · Gurobi<br>direct</div> |
|:---:|---:|---:|---:|---:|
| 100 | 5.8 ms | 18.7 ms | 7.4 ms | 11.2 ms |
| 200 | 26.6 ms | 77.3 ms | 26.1 ms | 45.2 ms |
| 300 | 63.4 ms | 183.4 ms | 58.6 ms | 112.1 ms |
| 400 | 174.1 ms | 355.7 ms | 176.0 ms | 246.7 ms |
| 500 | 229.9 ms | 602.0 ms | 227.2 ms | 360.4 ms |
| 600 | 327.0 ms | 963.8 ms | 324.1 ms | 508.7 ms |
| 700 | 433.2 ms | 1289.1 ms | 429.5 ms | 692.2 ms |
| 800 | 549.7 ms | 1723.7 ms | 544.1 ms | 921.0 ms |
| 900 | 691.4 ms | 2264.1 ms | 695.6 ms | 1157.0 ms |
| 1000 | 866.6 ms | 2777.5 ms | 872.9 ms | 1405.3 ms |
<!-- /table -->

Cutting out the caching layer makes filling the model *slower*, by 3.2× for
HiGHS and 1.6× for Gurobi — the price of actually depositing the model in the
solver as you go, which is the same effect that separates MIP++ from `MPSolver`
in the C++ tables, though it costs far less there (1.3× on HiGHS at N = 1000).
The two solvers' incremental APIs differ enough to make direct mode
twice as expensive on HiGHS as on Gurobi, a difference the cached columns hide
completely.

Direct mode is the one to compare against MIP++, since it is the mode that has
the model in the solver when the timer stops. Against MIP++ on HiGHS (151.5 ms
at N = 1000), that is 18× for JuMP direct and 5.7× for JuMP cached.

### Python modeling interfaces

Self-contained builders in [`src/gurobi.py`](src/gurobi.py),
[`src/highs.py`](src/highs.py), [`src/pulp_.py`](src/pulp_.py) and
[`src/python-mip.py`](src/python-mip.py), timing a single build per model:

<!-- table:python_interfaces -->
| N | <div align="center">gurobipy<br>Gurobi</div> | <div align="center">highspy<br>HiGHS</div> | <div align="center">PuLP<br>Cbc · CPython</div> | <div align="center">PuLP<br>Cbc · PyPy</div> | <div align="center">Python-MIP<br>Cbc · CPython</div> | <div align="center">Python-MIP<br>Cbc · PyPy</div> |
|:---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.02 s | 0.20 s | 0.06 s | 0.06 s | 0.08 s | 0.15 s |
| 200 | 0.07 s | 0.80 s | 0.22 s | 0.15 s | 0.18 s | 0.18 s |
| 300 | 0.16 s | 1.76 s | 0.48 s | 0.31 s | 0.34 s | 0.23 s |
| 400 | 0.29 s | 3.20 s | 0.93 s | 0.53 s | 0.58 s | 0.32 s |
| 500 | 0.46 s | 4.84 s | 1.46 s | 0.84 s | 0.89 s | 0.41 s |
| 600 | 0.71 s | 6.98 s | 2.21 s | 1.26 s | 1.28 s | 0.54 s |
| 700 | 1.05 s | 9.49 s | 3.11 s | 1.78 s | 1.73 s | 0.71 s |
| 800 | 1.43 s | 12.77 s | 4.18 s | 2.38 s | 2.29 s | 0.91 s |
| 900 | 1.84 s | 15.75 s | 5.50 s | 3.09 s | 2.94 s | 1.15 s |
| 1000 | 2.33 s | 19.37 s | 6.91 s | 3.72 s | 3.61 s | 1.44 s |
<!-- /table -->

Against MIP++ on the same backend at N = 1000, the whole Python field costs one
to two orders of magnitude more: 11× for gurobipy, 54× for CPython Python-MIP,
103× for CPython PuLP and 128× for highspy. (The Gurobi Python-MIP columns are
in the [Gurobi table](#mip-vs-the-gurobi-c-api) above.)

Two secondary observations, reported for completeness rather than as claims
about MIP++: `highspy` is the slowest of the four despite being a thin binding
over a C++ solver, because a `highspy` integer variable takes two calls
(`addVar` then `changeColIntegrality`) and each `addRow` hands over freshly
built Python lists; and PyPy's JIT is worth 1.9–2.5× at N = 1000 but nothing at
N = 100, where it never warms up inside a process that builds a single model.

### MIP++ across solver backends

The same `mippp` executable, one constraint at a time, against every backend
whose shared library was found at runtime. This is the cost of the solver's own
model-building API plus MIP++'s (near-zero) overhead, so the spread is the
solvers':

<!-- table:mippp_backends -->
| N | Cbc | MOSEK | HiGHS | CPLEX | Gurobi | GLPK | Xpress | SCIP |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.9 ms | 2.2 ms | 1.6 ms | 1.5 ms | 3.3 ms | 1.8 ms | 2.4 ms | 7.6 ms |
| 200 | 3.1 ms | 4.2 ms | 6.2 ms | 6.9 ms | 9.2 ms | 7.1 ms | 7.5 ms | 24.1 ms |
| 300 | 7.2 ms | 8.1 ms | 15.4 ms | 15.1 ms | 18.5 ms | 16.9 ms | 17.3 ms | 53.3 ms |
| 400 | 12.3 ms | 12.7 ms | 25.4 ms | 25.3 ms | 31.8 ms | 29.4 ms | 29.3 ms | 86.6 ms |
| 500 | 19.1 ms | 19.1 ms | 38.3 ms | 47.0 ms | 49.6 ms | 53.0 ms | 48.1 ms | 126.0 ms |
| 600 | 27.0 ms | 29.0 ms | 59.6 ms | 63.8 ms | 72.9 ms | 81.1 ms | 104.6 ms | 184.5 ms |
| 700 | 37.8 ms | 37.9 ms | 79.3 ms | 85.6 ms | 101.6 ms | 128.3 ms | 99.7 ms | 251.7 ms |
| 800 | 50.1 ms | 48.2 ms | 107.4 ms | 117.4 ms | 132.8 ms | 162.0 ms | 144.5 ms | 325.7 ms |
| 900 | 61.4 ms | 61.7 ms | 133.0 ms | 171.4 ms | 168.1 ms | 237.2 ms | 219.7 ms | 409.4 ms |
| 1000 | 71.7 ms | 74.4 ms | 152.6 ms | 207.1 ms | 209.6 ms | 261.2 ms | 255.2 ms | 499.6 ms |
<!-- /table -->

Cbc and MOSEK accept the model fastest and SCIP is an order of magnitude behind
the rest (7.0× Cbc at N = 1000). Normalised by model size, most backends are
flat across the sweep; GLPK (×1.5 from N = 200 to N = 1000), Xpress (×1.4) and
CPLEX (×1.2) cost progressively more per nonzero as the model grows.

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

<!-- table:mippp_variants_summary -->
| backend | one-at-a-time | + distinct | bulk | bulk + distinct |
|:---:|---:|---:|---:|---:|
| Cbc | 71.7 ms | 93 % | 105 % | 94 % |
| MOSEK | 74.4 ms | 90 % | 113 % | 106 % |
| HiGHS | 152.6 ms | 99 % | 93 % | 91 % |
| CPLEX | 207.1 ms | 96 % | 65 % | 66 % |
| Gurobi | 209.6 ms | 97 % | 104 % | 103 % |
| GLPK | 261.2 ms | 95 % | 100 % | 93 % |
| Xpress | 255.2 ms | 94 % | 83 % | 78 % |
| SCIP | 499.6 ms | 97 % | 100 % | 98 % |
<!-- /table -->

The `distinct_variables` hint never hurts: worth 1–10 %, most on MOSEK (10 %)
and Cbc (7 %), least on HiGHS (1 %) whose own build API swallows the difference.
Bulk cuts both ways — worth 35 % for CPLEX, 17 % for Xpress and 7 % for HiGHS,
nothing for GLPK and SCIP, and *counter*-productive for MOSEK (+13 %), Cbc
(+5 %) and Gurobi (+4 %), whose per-constraint entry points are already the fast
path. The same one-at-a-time /
bulk split exists for the Gurobi C API and buys nothing there either (see the
[Gurobi table](#mip-vs-the-gurobi-c-api)).

This is why the MIP++ figures elsewhere come from `mippp_distinct`: it is the
per-constraint variant, comparable to how every other interface is used, and the
hint is a legitimate property of this model. The backend table above uses plain
`mippp`, the variant with no hint, so that it measures the backends rather than
the hint.

## Limitations

- **The comparison is not work-for-work.** The deferred interfaces (`MPSolver`, MathOpt, JuMP cached) have less of the model in the solver when their timer stops. This is documented in [§ Deferred vs. direct model construction](#deferred-vs-direct-model-construction) and is the main caveat on every cross-interface ratio.
- **Single machine, single compiler.** All numbers come from one AMD Ryzen 7 7800X3D running Ubuntu 22.04 with GCC 14. Absolute times are machine-dependent; the ratios are the transferable quantity.
- **The Cbc columns need an unreleased Cbc.** They were measured against the `devel` branch, the only version that caches `addRow` calls; on release 2.10.13 every direct-building interface is substantially slower on Cbc. The Cbc figures are therefore not reproducible from a distribution package today.
- **Backends without a license here are reported as skipped, not measured.** COPT is wired up in `src/mippp.cpp` and its library loads, but no usable license was available on this machine, so it aborts on a `mippp::license_error` and has no column.
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
python3 scripts/benchmarks/mippp.py        # -> results/mippp/<solver>[_bulk][_distinct].csv
python3 scripts/benchmarks/or-tools.py     # -> results/or-tools/<solver>_<interface>.csv
python3 scripts/benchmarks/gurobi.py       # -> results/gurobi/gurobi_c[_bulk].csv
python3 scripts/benchmarks/gurobipy.py     # -> results/gurobi/gurobipy.csv
python3 scripts/benchmarks/highspy.py      # -> results/highs/highspy.csv
python3 scripts/benchmarks/jump.py         # -> results/jump/<solver>_<interface>.csv
python3 scripts/benchmarks/pulp.py         # -> results/pulp/<python>.csv
python3 scripts/benchmarks/python-mip.py   # -> results/python-mip/<python>_<solver>.csv
```

Solvers, packages or licenses missing at runtime are reported as skipped and
produce no CSV; every runner overwrites its own CSVs on each run. The CSVs
behind every table in this README are committed under [`results/`](results/), so
each number can be checked without re-running anything.

> [!NOTE]
> The runners spawn CPython as `python` (and PyPy as `pypy3`), so make sure
> `python` on your `PATH` resolves to the interpreter where the packages are
> installed — on a stock Ubuntu that ships only `python3`, activate a virtualenv
> or install `python-is-python3`.

### Regenerating the tables

Every table above is rendered from the committed CSVs by a script under
`scripts/tables/` (standard library only), reading the `model_time_ms` column
of each — except the JuMP `cold` column, which is `cold_model_time_ms` of the
same CSV. Running `python3 scripts/tables/<script>` from the repository root
reproduces the corresponding table verbatim — which is the shortest path from a
number in this README to the measurement behind it.

Each table sits between a pair of HTML comments naming its script, so the whole
README can be refilled from `results/` in one step:

```sh
python3 scripts/render_readme.py           # rewrite any table that has gone stale
python3 scripts/render_readme.py --check   # or just report them, exiting 1
```

The figures quoted in the surrounding *prose* are hand-written, so they are
checked separately: `scripts/check_figures.py` recomputes each one from the
CSVs and requires it to appear verbatim in the sentence that claims it.

```sh
python3 scripts/check_figures.py           # 31 prose figures vs results/
make check                                 # both of the above
```

Together these two make the README mechanically true of `results/`: a re-run
that moves a number fails `make check` instead of being published.

| Section | Script | Reads |
|---|---|---|
| [Overview: the C++ and Julia interfaces](#overview-the-c-and-julia-interfaces) | `mippp_vs_others.py` | `mippp/Highs_distinct`, `or-tools/Highs_*_setcoef`, `jump/Highs_*` |
| [MIP++ vs the Gurobi C API](#mip-vs-the-gurobi-c-api) | `gurobi_vs_mippp.py` | `gurobi/*`, `mippp/Gurobi_distinct`, `jump/Gurobi_direct`, `python-mip/*_Gurobi` |
| [MIP++ vs OR-Tools](#mip-vs-or-tools) | `mippp_vs_or-tools.py` | `mippp/{Cbc,Highs,SCIP}_distinct`, `or-tools/*_setcoef` |
| [Both OR-Tools APIs have a faster way to fill a row](#both-or-tools-apis-have-a-faster-way-to-fill-a-row) | `or-tools_modes.py` | `or-tools/*` (both forms) |
| [MIP++ vs JuMP](#mip-vs-jump) | `jump_modes.py` | `jump/{Highs,Gurobi}_{cached,direct}` |
| [Python modeling interfaces](#python-modeling-interfaces) | `python_interfaces.py` | `gurobi/gurobipy`, `highs/highspy`, `pulp/*`, `python-mip/*_Cbc` |
| [MIP++ across solver backends](#mip-across-solver-backends) | `mippp_backends.py` | `mippp/<backend>` (plain, no hint) |
| [MIP++ build variants](#mip-build-variants) | `mippp_variants_summary.py` | `mippp/*` (all four variants at N = 1000) |

`mippp_variants.py` renders the same four variants across the whole sweep for
Cbc; it is not shown above.

## Repository layout

| Path | Contents |
|---|---|
| [`src/`](src/) | one self-contained model builder per interface and variant |
| [`scripts/`](scripts/) | benchmark runners, one per interface family, writing CSVs to `results/` |
| [`results/`](results/) | the committed measurements behind every table above |
| [`scripts/tables/`](scripts/tables/) | CSV → Markdown table renderers |
| [`profiles/`](profiles/) | Conan profiles pinning compiler and standard |
