.PHONY: all build readme check

all: build
	python scripts/benchmarks/gurobi.py
	python scripts/benchmarks/gurobipy.py
	python scripts/benchmarks/highspy.py
	python scripts/benchmarks/jump.py
	python scripts/benchmarks/mippp.py
	python scripts/benchmarks/or-tools.py
	python scripts/benchmarks/pulp.py
	python scripts/benchmarks/python-mip.py
	$(MAKE) readme

# Refill the README tables from results/; --check only reports, for CI.
readme:
	python scripts/render_readme.py

check:
	python scripts/render_readme.py --check
	python scripts/check_figures.py

build:
	conan build . -of=build -pr=profiles/gcc14_c++23 -b=missing