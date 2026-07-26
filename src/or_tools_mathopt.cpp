#include <memory>
#include <optional>
#include <print>
#include <string>
#include <utility>
#include <vector>

#include "ortools/math_opt/cpp/math_opt.h"

#include "chrono.hpp"

namespace math_opt = operations_research::math_opt;

using math_opt::LinearExpression;
using math_opt::Model;
using math_opt::SolverType;
using math_opt::Variable;

int run(const std::string & solver_id, const SolverType solver_type,
        const int N);

int main(int argc, char * argv[]) {
    if(argc < 3) {
        std::println(stderr, "Usage: {} <solver> <N>", argv[0]);
        return EXIT_FAILURE;
    }
    const std::string solver(argv[1]);
    const int N = std::atoi(argv[2]);

    // MathOpt has no Cbc backend, and the Glpk one is not built by Conan's
    // or-tools recipe.
    if(solver == "SCIP") return run("GSCIP", SolverType::kGscip, N);
    if(solver == "Gurobi") return run("GUROBI", SolverType::kGurobi, N);
    if(solver == "Highs") return run("HIGHS", SolverType::kHighs, N);
    if(solver == "Xpress") return run("XPRESS", SolverType::kXpress, N);
    if(solver == "CPSAT") return run("CP_SAT", SolverType::kCpSat, N);

    std::println(stderr, "Unknown solver: {}", solver);
    return EXIT_FAILURE;
}

int run(const std::string & solver_id, const SolverType solver_type,
        const int N) {
    Chrono chrono;
    Model model("nqueens");
    // Unlike the one-shot math_opt::Solve(), NewIncrementalSolver() builds the
    // backend solver right away, which is what MPSolver::CreateSolver() did.
    const auto solver = math_opt::NewIncrementalSolver(&model, solver_type);
    if(!solver.ok()) {
        std::println(stderr, "Solver unavailable: {}",
                     solver.status().message());
        return EXIT_FAILURE;
    }
    const int api_time_ms = chrono.lapTimeMs();

    // x[row][col] == 1 iff a queen is placed on the square (row, col)
    std::vector<std::vector<Variable>> x;
    x.reserve(static_cast<std::size_t>(N));
    for(int row = 0; row < N; ++row) {
        std::vector<Variable> row_vars;
        row_vars.reserve(static_cast<std::size_t>(N));
        for(int col = 0; col < N; ++col)
            row_vars.push_back(model.AddBinaryVariable());
        x.push_back(std::move(row_vars));
    }

    // one per row
    for(int row = 0; row < N; ++row) {
        LinearExpression sum;
        for(int col = 0; col < N; ++col) sum += x[row][col];
        model.AddLinearConstraint(std::move(sum) == 1.0);
    }
    // one per column
    for(int col = 0; col < N; ++col) {
        LinearExpression sum;
        for(int row = 0; row < N; ++row) sum += x[row][col];
        model.AddLinearConstraint(std::move(sum) == 1.0);
    }
    // one per upper diagonal \ //
    for(int top_col = 0; top_col < N - 1; ++top_col) {
        LinearExpression sum;
        for(int row = 0; row < N - top_col; ++row) sum += x[row][top_col + row];
        model.AddLinearConstraint(std::move(sum) <= 1.0);
    }
    // one per lower diagonal \ //
    for(int left_row = 1; left_row < N - 1; ++left_row) {
        LinearExpression sum;
        for(int col = 0; col < N - left_row; ++col)
            sum += x[left_row + col][col];
        model.AddLinearConstraint(std::move(sum) <= 1.0);
    }
    // one per upper diagonal / //
    for(int left_row = 1; left_row < N; ++left_row) {
        LinearExpression sum;
        for(int col = 0; col < left_row + 1; ++col)
            sum += x[left_row - col][col];
        model.AddLinearConstraint(std::move(sum) <= 1.0);
    }
    // one per lower diagonal / //
    for(int bottom_col = 1; bottom_col < N - 1; ++bottom_col) {
        LinearExpression sum;
        for(int col = bottom_col; col < N; ++col)
            sum += x[N - 1 - (col - bottom_col)][col];
        model.AddLinearConstraint(std::move(sum) <= 1.0);
    }

    const auto num_variables = model.num_variables();
    const auto num_constraints = model.num_linear_constraints();

    const double model_time_ms = chrono.lapTimeUs() / 1000.0;
    std::optional<double> solve_time_ms;

    if(N < 20) {
        const auto result = (*solver)->Solve();
        if(!result.ok()) {
            std::println(stderr, "Solve failed: {}", result.status().message());
            return EXIT_FAILURE;
        }
        if(!result->has_primal_feasible_solution()) {
            std::println(stderr, "No solution found.");
            return EXIT_FAILURE;
        }
        solve_time_ms.emplace(chrono.lapTimeUs() / 1000.0);
        const auto & values = result->variable_values();
        for(int i = 0; i < N; ++i) {
            for(int j = 0; j < N; ++j) {
                std::print("{}", values.at(x[i][j]) > 0.5 ? '#' : '+');
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
