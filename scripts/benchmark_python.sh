#!/bin/bash

mkdir -p results/python-mip

if [ ! -f results/python-mip/cbc_cpython.csv ]; then
    echo "Benchmarking n-Queens CBC Python-MIP CPYTHON"
    if python3 python-mip/benchmarks/queens.py cbc; then
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-cbc.csv
        mv queens-mip-cbc.csv results/python-mip/cbc_cpython.csv
    else
        rm queens-mip-cbc.csv
    fi
fi

if [ ! -f results/python-mip/gurobi_cpython.csv ]; then
    echo "Benchmarking n-Queens Gurobi Python-MIP CPYTHON"
    if python3 python-mip/benchmarks/queens.py gurobi; then
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-gurobi.csv
        mv queens-mip-gurobi.csv results/python-mip/gurobi_cpython.csv
    else
        rm queens-mip-gurobi.csv
    fi
fi

if [ ! -f results/python-mip/cbc_pypy.csv ]; then
    echo "Benchmarking n-Queens CBC Python-MIP Pypy"
    if pypy3 python-mip/benchmarks/queens.py cbc; then
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-cbc.csv
        mv queens-mip-cbc.csv results/python-mip/cbc_pypy.csv
    else
        rm queens-mip-cbc.csv
    fi
fi

if [ ! -f results/python-mip/gurobi_pypy.csv ]; then
    echo "Benchmarking n-Queens Gurobi Python-MIP Pypy"
    if pypy3 python-mip/benchmarks/queens.py gurobi; then
        sed -i '1s/^/N,num_variables,num_constraints,num_entries,model_time_s\n/' queens-mip-gurobi.csv
        mv queens-mip-gurobi.csv results/python-mip/gurobi_pypy.csv
    else
        rm queens-mip-gurobi.csv
    fi
fi

mkdir -p results/gurobi

if [ ! -f results/gurobi/gurobipy.csv ]; then
    echo "Benchmarking n-Queens Gurobi"
    if python3 python-mip/benchmarks/queens-gurobi.py; then
        sed -i '1s/^/N,name,model_time_s\n/' queens-gurobi-cpython.csv
        mv queens-gurobi-cpython.csv results/gurobi/gurobipy.csv
    else
        rm queens-gurobi-cpython.csv
    fi
fi

mkdir -p results/pulp

if [ ! -f results/pulp/cpython.csv ]; then
    echo "Benchmarking n-Queens Pulp CPYTHON"
    if python3 python-mip/benchmarks/queens-pulp.py; then
        sed -i '1s/^/N,name,model_time_s\n/' queens-pulp.csv
        mv queens-pulp.csv results/pulp/cpython.csv
    else
        rm queens-pulp.csv
    fi
fi

if [ ! -f results/pulp/pypy.csv ]; then
    echo "Benchmarking n-Queens Pulp Pypy"
    if pypy3 python-mip/benchmarks/queens-pulp.py; then
        sed -i '1s/^/N,name,model_time_s\n/' queens-pulp.csv
        mv queens-pulp.csv results/pulp/pypy.csv
    else
        rm queens-pulp.csv
    fi
fi
