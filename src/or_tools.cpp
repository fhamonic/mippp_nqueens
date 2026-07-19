#include <iostream>
#include <memory>
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
        std::cerr << "Usage: nqueens <solver> <N>" << std::endl;
        return EXIT_FAILURE;
    }
    const std::string solver(argv[1]);
    const int N = std::atoi(argv[2]);

    // std::cerr << "solver,N,load_us,fill_ms,solve_ms" << std::endl;
    std::cerr << solver << ',' << N;

    if(solver == "Cbc") return run("CBC", N);
    if(solver == "SCIP") return run("SCIP", N);
    if(solver == "Gurobi") return run("GUROBI", N);
    if(solver == "Highs") return run("HIGHS", N);

    std::cerr << "Unknown solver : " << solver << std::endl;
    return EXIT_FAILURE;
}

int run(const std::string & solver_id, const int N) {
    Chrono chrono;
    std::unique_ptr<MPSolver> solver(MPSolver::CreateSolver(solver_id));
    if(!solver) {
        std::cerr << "Solver unavailable." << std::endl;
        return EXIT_FAILURE;
    }
    int api_time_us = chrono.lapTimeUs();

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
        for(int col = 0; col < N - left_row; ++col) sum += x[left_row + col][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }
    // one per upper diagonal / //
    for(int left_row = 1; left_row < N; ++left_row) {
        LinearExpr sum;
        for(int col = 0; col < left_row + 1; ++col) sum += x[left_row - col][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }
    // one per lower diagonal / //
    for(int bottom_col = 1; bottom_col < N - 1; ++bottom_col) {
        LinearExpr sum;
        for(int col = bottom_col; col < N; ++col)
            sum += x[N - 1 - (col - bottom_col)][col];
        solver->MakeRowConstraint(sum <= 1.0);
    }

    int fill_time_us = chrono.lapTimeUs();
    std::cerr << ',' << solver->NumVariables() << ','
              << solver->NumConstraints() << ',' << api_time_us << ','
              << fill_time_us;

    if(N < 20) {
        const MPSolver::ResultStatus result_status = solver->Solve();
        if(result_status != MPSolver::OPTIMAL &&
           result_status != MPSolver::FEASIBLE) {
            std::cerr << "No solution found." << std::endl;
            return EXIT_FAILURE;
        }
        for(int i = 0; i < N; ++i) {
            for(int j = 0; j < N; ++j) {
                std::cerr << ' '
                          << (x[i][j]->solution_value() > 0.5 ? 'o' : '.');
            }
            std::cerr << std::endl;
        }
    }

    return EXIT_SUCCESS;
}
