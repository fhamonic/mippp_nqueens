from helper import *

# Both OR-Tools APIs offer two ways to fill a row. The expression form builds a
# `LinearExpr` / `LinearExpression`, which accumulates the terms in a hash map
# before the finished row is handed over; the coefficient form opens the row
# first and writes into it -- `MakeRowConstraint(lb, ub)` + `SetCoefficient`,
# `AddLinearConstraint(lb, ub)` + `set_coefficient`. The coefficient form is the
# faster of the two and the one every other table uses; here it is the baseline
# in milliseconds, with the expression form as a percentage of it.


def to_ms(N, value):
    return "{:.1f} ms".format(float(value))


def percentage_to(ref_col):
    def f(N, value):
        ref = float(ref_col[N])
        return "—" if ref == 0 else "{:.0f} %".format(float(value) / ref * 100)

    return f


def col(interface, solver):
    return read_col(f"results/or-tools/{solver}_{interface}.csv", "model_time_ms")


table_data = []
for interface, expr_label, setcoef_label, solvers in [
    (
        "mpsolver",
        "MPSolver<br>LinearExpr",
        "MPSolver<br>SetCoefficient",
        [("Cbc", "Cbc"), ("Highs", "HiGHS"), ("SCIP", "SCIP")],
    ),
    (
        "mathopt",
        "MathOpt<br>LinearExpression",
        "MathOpt<br>set_coefficient",
        [("Highs", "HiGHS"), ("SCIP", "SCIP")],
    ),
]:
    table_data.append(
        (
            setcoef_label,
            [(label, col(f"{interface}_setcoef", s), to_ms) for s, label in solvers],
        )
    )
    table_data.append(
        (
            expr_label,
            [
                (
                    label,
                    col(interface, s),
                    percentage_to(col(f"{interface}_setcoef", s)),
                )
                for s, label in solvers
            ],
        )
    )

print_markdown_table(table_data)
