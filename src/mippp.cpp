#include <iostream>
#include <ranges>

#include "mippp/solvers/cbc/all.hpp"
#include "mippp/solvers/copt/all.hpp"
#include "mippp/solvers/cplex/all.hpp"
#include "mippp/solvers/glpk/all.hpp"
#include "mippp/solvers/gurobi/all.hpp"
#include "mippp/solvers/highs/all.hpp"
#include "mippp/solvers/mosek/all.hpp"
#include "mippp/solvers/scip/all.hpp"
#include "mippp/solvers/xpress/all.hpp"

using namespace mippp;
using namespace mippp::operators;

#include "chrono.hpp"

template <typename API, typename MODEL>
int run(const std::string & solver, const int N);

int main(int argc, char * argv[]) {
    if(argc < 3) {
        std::println(stderr, "Usage: {} <solver> <N>", argv[0]);
        return EXIT_FAILURE;
    }
    const std::string solver(argv[1]);
    const int N = std::atoi(argv[2]);

    if(solver == "Cbc") return run<cbc_api, cbc_milp>(solver, N);
    if(solver == "CPLEX") return run<cplex_api, cplex_milp>(solver, N);
    if(solver == "COPT") return run<copt_api, copt_milp>(solver, N);
    if(solver == "Highs") return run<highs_api, highs_milp>(solver, N);
    if(solver == "GLPK") return run<glpk_api, glpk_milp>(solver, N);
    if(solver == "Gurobi") return run<gurobi_api, gurobi_milp>(solver, N);
    if(solver == "MOSEK") return run<mosek_api, mosek_milp>(solver, N);
    if(solver == "SCIP") return run<scip_api, scip_milp>(solver, N);
    if(solver == "Xpress") return run<xpress_api, xpress_milp>(solver, N);

    std::println(stderr, "Unknown solver: ", solver);
    return EXIT_FAILURE;
}

template <typename API, typename MODEL>
int run(const std::string & solver, const int N) {
    Chrono chrono;
    API api;
    int api_time_us = chrono.lapTimeUs();
    MODEL model(api);

    auto X = model.add_binary_variables(
        N * N, [N](int row, int col) { return row * N + col; });

    auto indices = std::views::iota(0, N);
    // one per row
    for(auto && row : indices) {
        model.add_constraint(
            xsum(indices, [&](auto && col) { return X(row, col); }) == 1);
    }
    // one per column
    for(auto && col : indices) {
        model.add_constraint(
            xsum(indices, [&](auto && row) { return X(row, col); }) == 1);
    }
    // one per upper diagonal \ //
    for(auto && top_col : std::views::iota(0, N - 1)) {
        model.add_constraint(
            xsum(std::views::iota(0, N - top_col),
                 [&](auto && row) { return X(row, top_col + row); }) <= 1);
    }
    // one per lower diagonal \ //
    for(auto && left_row : std::views::iota(1, N - 1)) {
        model.add_constraint(
            xsum(std::views::iota(0, N - left_row),
                 [&](auto && col) { return X(left_row + col, col); }) <= 1);
    }
    // one per upper diagonal / //
    for(auto && left_row : std::views::iota(1, N)) {
        model.add_constraint(
            xsum(std::views::iota(0, left_row + 1),
                 [&](auto && col) { return X(left_row - col, col); }) <= 1);
    }
    // one per lower diagonal / //
    for(auto && bottom_col : std::views::iota(1, N - 1)) {
        model.add_constraint(
            xsum(std::views::iota(bottom_col, N), [&](auto && col) {
                return X(N - 1 - (col - bottom_col), col);
            }) <= 1);
    }

    // also trigger update for buffered models
    const auto num_variables = model.num_variables();
    const auto num_constraints = model.num_constraints();

    const int model_time_us = chrono.lapTimeUs();
    std::optional<int> solve_time_ms;

    if(N < 20) {
        model.solve();
        solve_time_ms.emplace(chrono.lapTimeMs());
        auto solution = model.get_solution();
        for(auto i : indices) {
            for(auto j : indices) {
                std::print(" {}", (solution[X(i, j)] ? '#' : '-'));
            }
            std::println();
        }
    }

    std::print(stderr, R"({{
    "solver_name" : "{}",
    "N" : {},
    "num_variables" : {},
    "num_constraints" : {},
    "api_time_us" : {},
    "model_time_us" : {})",
               solver, N, num_variables, num_constraints, api_time_us,
               model_time_us);
    if(solve_time_ms.has_value()) {
        std::print(stderr, R"(,
    "solve_time_ms" : {})",
                   solve_time_ms.value());
    }
    std::println(stderr, "\n}}");

    return EXIT_SUCCESS;
}