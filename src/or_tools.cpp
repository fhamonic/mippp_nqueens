#include <memory>
#include <print>
#include <string>
#include <vector>

#include "ortools/linear_solver/linear_solver.h"

#include "chrono.hpp"

using operations_research::LinearExpr;
using operations_research::MPSolver;
using operations_research::MPVariable;

int run(const std::string & solver_id, const int N);

int main(int argc, char * argv[]) {
    if(argc < 3) {
        std::println(stderr, "Usage: {} <solver> <N>", argv[0]);
        return EXIT_FAILURE;
    }
    const std::string solver(argv[1]);
    const int N = std::atoi(argv[2]);

    if(solver == "Cbc") return run("CBC", N);
    if(solver == "SCIP") return run("SCIP", N);
    if(solver == "GLPK") return run("GLPK", N);
    if(solver == "Gurobi") return run("GUROBI", N);
    if(solver == "Highs") return run("HIGHS", N);

    std::println(stderr, "Unknown solver: ", solver);
    return EXIT_FAILURE;
}

int run(const std::string & solver_id, const int N) {
    Chrono chrono;
    std::unique_ptr<MPSolver> solver(MPSolver::CreateSolver(solver_id));
    if(!solver) {
        std::println(stderr, "Solver unavailable.");
        return EXIT_FAILURE;
    }
    const int api_time_ms = chrono.lapTimeMs();

    // x[row][col] == 1 iff a queen is placed on the square (row, col)
    std::vector<std::vector<const MPVariable *>> x(
        N, std::vector<const MPVariable *>(N));
    for(int row = 0; row < N; ++row) {
        for(int col = 0; col < N; ++col) {
            x[row][col] = solver->MakeBoolVar("");
        }
    }

    // one per row
    for(int row = 0; row < N; ++row) {
        LinearExpr sum;
        for(int col = 0; col < N; ++col) sum += x[row][col];
        solver->MakeRowConstraint(sum == 1.0);
    }
    // one per column
    for(int col = 0; col < N; ++col) {
        LinearExpr sum;
        for(int row = 0; row < N; ++row) sum += x[row][col];
        solver->MakeRowConstraint(sum == 1.0);
    }
    // one per upper diagonal \ //
    for(int top_col = 0; top_col < N - 1; ++top_col) {
        LinearExpr sum;
        for(int row = 0; row < N - top_col; ++row) sum += x[row][top_col + row];
        solver->MakeRowConstraint(sum <= 1.0);
    }
    // one per lower diagonal \ //
    for(int left_row = 1; left_row < N - 1; ++left_row) {
        LinearExpr sum;
        for(int col = 0; col < N - left_row; ++col)
            sum += x[left_row + col][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }
    // one per upper diagonal / //
    for(int left_row = 1; left_row < N; ++left_row) {
        LinearExpr sum;
        for(int col = 0; col < left_row + 1; ++col)
            sum += x[left_row - col][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }
    // one per lower diagonal / //
    for(int bottom_col = 1; bottom_col < N - 1; ++bottom_col) {
        LinearExpr sum;
        for(int col = bottom_col; col < N; ++col)
            sum += x[N - 1 - (col - bottom_col)][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }

    const auto num_variables = solver->NumVariables();
    const auto num_constraints = solver->NumConstraints();

    const int model_time_ms = chrono.lapTimeMs();
    std::optional<int> solve_time_ms;

    if(N < 20) {
        const MPSolver::ResultStatus result_status = solver->Solve();
        if(result_status != MPSolver::OPTIMAL &&
           result_status != MPSolver::FEASIBLE) {
            std::println(stderr, "No solution found.");
            return EXIT_FAILURE;
        }
        solve_time_ms.emplace(chrono.lapTimeMs());
        for(int i = 0; i < N; ++i) {
            for(int j = 0; j < N; ++j) {
                std::print("{}", x[i][j]->solution_value() > 0.5 ? '#' : '+');
            }
            std::println();
        }
    }

    std::print(stderr, R"({{
    "solver_name" : "{}",
    "N" : {},
    "num_variables" : {},
    "num_constraints" : {},
    "api_time_ms" : {},
    "model_time_ms" : {})",
               solver_id, N, num_variables, num_constraints, api_time_ms,
               model_time_ms);
    if(solve_time_ms.has_value()) {
        std::print(stderr, R"(,
    "solve_time_ms" : {})",
                   solve_time_ms.value());
    }
    std::println(stderr, "\n}}");

    return EXIT_SUCCESS;
}
