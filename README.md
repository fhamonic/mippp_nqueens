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
