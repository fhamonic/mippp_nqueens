#include <iostream>

#include <range/v3/view/iota.hpp>

#include "mippp/solvers/gurobi/all.hpp"

using namespace fhamonic::mippp;
using namespace fhamonic::mippp::operators;

#include "chrono.hpp"

int main(int argc, char * argv[]) {
    if(argc < 2) {
        std::cout << "Usage: nqueens <n>" << std::endl;
        return EXIT_FAILURE;
    }
    const int N = std::atoi(argv[1]);

    Chrono chrono;

    gurobi_api api;

    std::cout << chrono.lapTimeUs() << " us to load API." << std::endl;

    gurobi_milp model(api);

    auto X_vars = model.add_binary_variables(
        N * N, [N](int row, int col) { return row * N + col; });

    auto indices = ranges::views::iota(0, N);

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
    // one per bottom diagonal \ //
    model.add_constraints(ranges::views::iota(1, N - 1), [&](auto && left_row) {
        return xsum(ranges::views::iota(0, N - left_row), [&](auto && col) {
                   return X_vars(left_row + col, col);
               }) <= 1;
    });
    // one per upper diagonal / //
    model.add_constraints(ranges::views::iota(0, N), [&](auto && left_row) {
        return xsum(ranges::views::iota(0, left_row + 1), [&](auto && col) {
                   return X_vars(left_row - col, col);
               }) <= 1;
    });
    // one per bottom diagonal / //
    model.add_constraints(
        ranges::views::iota(1, N - 1), [&](auto && bottom_col) {
            return xsum(ranges::views::iota(bottom_col, N),
                        [&](auto && col) {
                            return X_vars(N - 1 - (col - bottom_col), col);
                        }) <= 1;
        });

    std::cout << chrono.lapTimeMs() << " ms to fill the model." << std::endl;

    model.solve();

    std::cout << chrono.lapTimeMs() << " ms to solve the model." << std::endl;

    auto solution = model.get_solution();

    for(auto i : indices) {
        for(auto j : indices) {
            std::cout << ' ' << solution[X_vars(i, j)];
        }
        std::cout << std::endl;
    }
    return EXIT_SUCCESS;
}