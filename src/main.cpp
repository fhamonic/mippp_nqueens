#include <iostream>

#include <range/v3/view/iota.hpp>

#include "mippp/solvers/cbc/all.hpp"
#include "mippp/solvers/cplex/all.hpp"
#include "mippp/solvers/gurobi/all.hpp"
#include "mippp/solvers/highs/all.hpp"
#include "mippp/solvers/mosek/all.hpp"
#include "mippp/solvers/scip/all.hpp"

using namespace fhamonic::mippp;
using namespace fhamonic::mippp::operators;

#include "chrono.hpp"

template <typename API, typename MODEL>
int run(const int N);

int main(int argc, char * argv[]) {
    if(argc < 3) {
        std::cerr << "Usage: nqueens <solver> <N>" << std::endl;
        return EXIT_FAILURE;
    }
    const std::string solver(argv[1]);
    const int N = std::atoi(argv[2]);

    // std::cerr << "solver,N,load_us,fill_ms,solve_ms" << std::endl;
    std::cerr << solver << ',' << N;

    if(solver == "Cbc") return run<cbc_api, cbc_milp>(N);
    if(solver == "CPLEX") return run<cplex_api, cplex_milp>(N);
    if(solver == "Gurobi") return run<gurobi_api, gurobi_milp>(N);
    if(solver == "Highs") return run<highs_api, highs_milp>(N);
    if(solver == "MOSEK") return run<mosek_api, mosek_milp>(N);
    if(solver == "SCIP") return run<scip_api, scip_milp>(N);

    std::cerr << "Unknown solver : " << solver << std::endl;
    return EXIT_FAILURE;
}

template <typename API, typename MODEL>
int run(const int N) {
    auto indices = ranges::views::iota(0, N);

    Chrono chrono;
    API api;
    std::cerr << ',' << chrono.lapTimeUs();
    MODEL model(api);

    auto X_vars = model.add_binary_variables(
        N * N, [N](int row, int col) { return row * N + col; });

    /*
    ///////////////////////////////////////////////////////////////////////////
    ////////////////////////////////// Naive //////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////
    for(auto i : indices) {
        model.add_constraint(
            xsum(indices, [&](auto && col) { return X_vars(i, col); }) == 1);
        model.add_constraint(
            xsum(indices, [&](auto && row) { return X_vars(row, i); }) == 1);
    }

    for(auto top_col : ranges::views::iota(0, N - 1)) {
        model.add_constraint(
            xsum(ranges::views::iota(0, N - top_col),
                 [&](auto && row) { return X_vars(row, top_col + row); }) <=
                 1);
    }

    for(auto left_row : ranges::views::iota(1, N - 1)) {
        model.add_constraint(
            xsum(ranges::views::iota(0, N - left_row), [&](auto && col) {
                return X_vars(left_row + col, col);
            }) <= 1);
    }

    for(auto left_row : ranges::views::iota(1, N)) {
        model.add_constraint(
            xsum(ranges::views::iota(0, left_row + 1), [&](auto && col) {
                return X_vars(left_row - col, col);
            }) <= 1);
    }

    for(auto bottom_col : ranges::views::iota(1, N - 1)) {
        model.add_constraint(
            xsum(ranges::views::iota(bottom_col, N), [&](auto && col) {
                return X_vars(N - 1 - (col - bottom_col), col);
            }) <= 1);
    }
    /*/
    ///////////////////////////////////////////////////////////////////////////
    ////////////////////////////////// Best ///////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////
    // one per row
    model.add_constraints(indices, [&](auto && row) {
        return xsum(indices, [&](auto && col) { return X_vars(row, col); }) ==
               1;
    });
    // one per column
    model.add_constraints(indices, [&](auto && col) {
        return xsum(indices, [&](auto && row) { return X_vars(row, col); }) ==
               1;
    });
    // one per upper diagonal \ //
    model.add_constraints(ranges::views::iota(0, N - 1), [&](auto && top_col) {
        return xsum(ranges::views::iota(0, N - top_col), [&](auto && row) {
                   return X_vars(row, top_col + row);
               }) <= 1;
    });
    // one per lower diagonal \ //
    model.add_constraints(ranges::views::iota(1, N - 1), [&](auto && left_row) {
        return xsum(ranges::views::iota(0, N - left_row), [&](auto && col) {
                   return X_vars(left_row + col, col);
               }) <= 1;
    });
    // one per upper diagonal / //
    model.add_constraints(ranges::views::iota(1, N), [&](auto && left_row) {
        return xsum(ranges::views::iota(0, left_row + 1), [&](auto && col) {
                   return X_vars(left_row - col, col);
               }) <= 1;
    });
    // one per lower diagonal / //
    model.add_constraints(
        ranges::views::iota(1, N - 1), [&](auto && bottom_col) {
            return xsum(ranges::views::iota(bottom_col, N), [&](auto && col) {
                       return X_vars(N - 1 - (col - bottom_col), col);
                   }) <= 1;
        });
    //*/

    std::cerr << ',' << static_cast<int>(chrono.lapTimeUs() / 100.0) / 10.0;
    // model.solve();
    // std::cerr << ',' << static_cast<int>(chrono.lapTimeUs() / 100.0) / 10.0
    //           << std::endl;

    if(N < 20) {
        auto solution = model.get_solution();
        for(auto i : indices) {
            for(auto j : indices) {
                std::cerr << ' ' << solution[X_vars(i, j)];
            }
            std::cerr << std::endl;
        }
    }

    return EXIT_SUCCESS;
}