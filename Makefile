.PHONY: all

all:
	python scripts/benchmark_gurobi.py
	python scripts/benchmark_gurobipy.py
	python scripts/benchmark_highspy.py
	python scripts/benchmark_jump.py
	python scripts/benchmark_mippp.py
	python scripts/benchmark_ortools.py
	python scripts/benchmark_pulp.py
	python scripts/benchmark_python-mip.py