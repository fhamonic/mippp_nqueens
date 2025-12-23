#include <iostream>
#include <vector>
#include "ortools/linear_solver/linear_solver.h"

#include "chrono.hpp"

namespace operations_research {

void SolveNQueens(int N) {
    Chrono chrono;

    std::unique_ptr<MPSolver> solver(
        MPSolver::CreateSolver("CBC_MIXED_INTEGER_PROGRAMMING"));
    if(!solver) {
        std::cerr << "Solver unavailable.\n";
        return;
    }

    // Create variables x[i][j] ∈ {0,1}
    std::vector<std::vector<const MPVariable *>> x(
        N, std::vector<const MPVariable *>(N));
    for(int i = 0; i < N; ++i) {
        for(int j = 0; j < N; ++j) {
            x[i][j] = solver->MakeIntVar(
                0.0, 1.0, "x_" + std::to_string(i) + "_" + std::to_string(j));
        }
    }

    // 1. One queen per row
    for(int i = 0; i < N; ++i) {
        LinearExpr row_sum;
        for(int j = 0; j < N; ++j) row_sum += x[i][j];
        solver->MakeRowConstraint(row_sum == 1.0);
    }

    // 2. One queen per column
    for(int j = 0; j < N; ++j) {
        LinearExpr col_sum;
        for(int i = 0; i < N; ++i) col_sum += x[i][j];
        solver->MakeRowConstraint(col_sum == 1.0);
    }

    // 3. At most one queen per diagonal (↘ direction)
    for(int d = 0; d <= 2 * N - 2; ++d) {
        LinearExpr diag;
        for(int i = 0; i < N; ++i) {
            int j = d - i;
            if(j >= 0 && j < N) diag += x[i][j];
        }
        solver->MakeRowConstraint(diag <= 1.0);
    }

    // 4. At most one queen per anti-diagonal (↙ direction)
    for(int d = 1 - N; d <= N - 1; ++d) {
        LinearExpr diag;
        for(int i = 0; i < N; ++i) {
            int j = i - d;
            if(j >= 0 && j < N) diag += x[i][j];
        }
        solver->MakeRowConstraint(diag <= 1.0);
    }

    // No particular objective — just find a feasible solution.
    MPObjective * const objective = solver->MutableObjective();
    objective->SetMinimization();

    std::cerr << ',' << static_cast<int>(chrono.lapTimeUs() / 100.0) / 10.0;

    if(N < 20) {
        const MPSolver::ResultStatus result_status = solver->Solve();
        if(result_status != MPSolver::OPTIMAL &&
           result_status != MPSolver::FEASIBLE) {
            std::cout << "No solution found.\n";
            return;
        }
        std::cerr << ',' << static_cast<int>(chrono.lapTimeUs() / 100.0) / 10.0;
        std::cout << "Solution for " << N << "-Queens:\n";
        for(int i = 0; i < N; ++i) {
            for(int j = 0; j < N; ++j) {
                std::cout << (x[i][j]->solution_value() > 0.5 ? " o" : " .");
            }
            std::cout << "\n";
        }
    }
}

}  // namespace operations_research

int main(int argc, char ** argv) {
    int N = 8;
    if(argc == 2) N = std::stoi(argv[1]);
    operations_research::SolveNQueens(N);
    return 0;
}
