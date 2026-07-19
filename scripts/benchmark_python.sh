#!/bin/bash

mkdir -p results/python-mip

if [ ! -f results/python-mip/cbc_cpython.csv ]; then
    echo "Benchmarking n-Queens CBC Python-MIP CPYTHON"
    python3 python-mip/benchmarks/queens.py cbc && \
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-cbc.csv && \
        mv queens-mip-cbc.csv results/python-mip/cbc_cpython.csv
    rm queens-mip-cbc.csv
fi

if [ ! -f results/python-mip/gurobi_cpython.csv ]; then
    echo "Benchmarking n-Queens Gurobi Python-MIP CPYTHON"
    python3 python-mip/benchmarks/queens.py gurobi && \
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-gurobi.csv && \
        mv queens-mip-gurobi.csv results/python-mip/gurobi_cpython.csv
    rm queens-mip-gurobi.csv
fi

if [ ! -f results/python-mip/cbc_pypy.csv ]; then
    echo "Benchmarking n-Queens CBC Python-MIP Pypy"
    pypy3 python-mip/benchmarks/queens.py cbc && \
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-cbc.csv && \
        mv queens-mip-cbc.csv results/python-mip/cbc_pypy.csv
    rm queens-mip-cbc.csv
fi

if [ ! -f results/python-mip/gurobi_pypy.csv ]; then
    echo "Benchmarking n-Queens Gurobi Python-MIP Pypy"
    pypy3 python-mip/benchmarks/queens.py gurobi && \
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-gurobi.csv && \
        mv queens-mip-gurobi.csv results/python-mip/gurobi_pypy.csv
    rm queens-mip-gurobi.csv
fi

if [ ! -f results/gurobipy.csv ]; then
    echo "Benchmarking n-Queens Gurobi"
    python3 python-mip/benchmarks/queens-gurobi.py && \
        mv queens-gurobi-cpython.csv results/gurobipy.csv
    rm queens-gurobi-cpython.csv
fi

mkdir -p results/pulp

if [ ! -f results/pulp/cpython.csv ]; then
    echo "Benchmarking n-Queens Pulp CPYTHON"
    python3 python-mip/benchmarks/queens-pulp.py && \
        sed -i '1s/^/N,name,model_time_s\n/' queens-pulp.csv && \
        mv queens-pulp.csv results/pulp/cpython.csv
    rm queens-pulp.csv
fi

if [ ! -f results/pulp/pypy.csv ]; then
    echo "Benchmarking n-Queens Pulp Pypy"
    pypy3 python-mip/benchmarks/queens-pulp.py && \
        sed -i '1s/^/N,name,model_time_s\n/' queens-pulp.csv && \
        mv queens-pulp.csv results/pulp/pypy.csv
    rm queens-pulp.csv
fi