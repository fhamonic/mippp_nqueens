#!/bin/bash

rm -f results/python-mip/cbc_cpython.csv results/python-mip/gurobi_cpython.csv results/python-mip/cbc_pypy.csv results/python-mip/gurobi_pypy.csv results/gurobipy.csv results/pulp_cpython.csv results/pulp_pypy.csv

echo "Benchmarking n-Queens CBC Python-MIP CPYTHON"
python3 python-mip/benchmarks/queens.py cbc
mv queens-mip-cbc.csv results/python-mip/cbc_cpython.csv

echo "Benchmarking n-Queens Gurobi Python-MIP CPYTHON"
python3 python-mip/benchmarks/queens.py gurobi
mv queens-mip-gurobi.csv results/python-mip/gurobi_cpython.csv

echo "Benchmarking n-Queens CBC Python-MIP Pypy"
pypy3 python-mip/benchmarks/queens.py cbc
mv queens-mip-cbc.csv results/python-mip/cbc_pypy.csv

echo "Benchmarking n-Queens Gurobi Python-MIP Pypy"
pypy3 python-mip/benchmarks/queens.py gurobi
mv queens-mip-gurobi.csv results/python-mip/gurobi_pypy.csv

echo "Benchmarking n-Queens Gurobi"
python3 python-mip/benchmarks/queens-gurobi.py
mv queens-gurobi-cpython.csv results/gurobipy.csv

echo "Benchmarking n-Queens Pulp CPYTHON"
python3 python-mip/benchmarks/queens-pulp.py
mv queens-pulp.csv results/pulp_cpython.csv

echo "Benchmarking n-Queens Pulp Pypy"
pypy3 python-mip/benchmarks/queens-pulp.py
mv queens-pulp.csv results/pulp_pypy.csv
