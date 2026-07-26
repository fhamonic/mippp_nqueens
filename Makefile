.PHONY: all build

all: build
	python scripts/benchmark_gurobi.py
	python scripts/benchmark_gurobipy.py
	python scripts/benchmark_highspy.py
	python scripts/benchmark_jump.py
	python scripts/benchmark_mippp.py
	python scripts/benchmark_or-tools.py
	python scripts/benchmark_pulp.py
	python scripts/benchmark_python-mip.py

build:
	conan build . -of=build -pr=profiles/gcc14_c++23 -b=missing