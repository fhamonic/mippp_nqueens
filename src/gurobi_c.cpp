#include <stdlib.h>
#include <string.h>

#include <optional>
#include <print>

#include "gurobi_c.h"

#include "chrono.hpp"

void checkGRBError(int error, GRBenv * env) {
    if(error) {
        std::println(stderr, "Gurobi Error: {}", GRBgeterrormsg(env));
        exit(EXIT_FAILURE);
    }
}

int main(int argc, char * argv[]) {
    if(argc != 2) {
        std::print("Usage: {} N\n", argv[0]);
        return EXIT_FAILURE;
    }
    int N = atoi(argv[1]);

    Chrono chrono;

    GRBenv * env = NULL;
    GRBmodel * model = NULL;
    int error;

    // Create empty model
    error = GRBloadenv(&env, NULL);
    checkGRBError(error, env);
    error =
        GRBnewmodel(env, &model, "nqueens", 0, NULL, NULL, NULL, NULL, NULL);
    checkGRBError(error, env);

    // Add N*N binary variables indexed as (col * N + row)
    const int num_variables = N * N;
    char * vtype = (char *)malloc(sizeof(char) * num_variables);
    memset(vtype, GRB_BINARY, num_variables);
    error = GRBaddvars(model, num_variables, 0, NULL, NULL, NULL, NULL, NULL,
                       NULL, vtype, NULL);
    checkGRBError(error, env);

    // C arrays to store linear expressions
    int * indices = (int *)malloc(sizeof(int) * N);
    double * coeffs = (double *)malloc(sizeof(double) * N);

    // One queen per row
    for(int row = 0; row < N; ++row) {
        for(int col = 0; col < N; ++col) {
            indices[col] = col * N + row;
            coeffs[col] = 1.0;
        }
        error = GRBaddconstr(model, N, indices, coeffs, GRB_EQUAL, 1.0, NULL);
        checkGRBError(error, env);
    }
    // One queen per column
    for(int col = 0; col < N; ++col) {
        for(int row = 0; row < N; ++row) {
            indices[row] = col * N + row;
            coeffs[row] = 1.0;
        }
        error = GRBaddconstr(model, N, indices, coeffs, GRB_EQUAL, 1.0, NULL);
        checkGRBError(error, env);
    }
    // one per upper diagonal \ //
    for(int top_col = 0; top_col < N - 1; ++top_col) {
        int idx = 0;
        for(int row = 0; row < N - top_col; ++row) {
            indices[idx] = (top_col + row) * N + row;
            coeffs[idx] = 1.0;
            ++idx;
        }
        error = GRBaddconstr(model, idx, indices, coeffs, GRB_LESS_EQUAL, 1.0,
                             NULL);
        checkGRBError(error, env);
    }
    // one per lower diagonal \ //
    for(int left_row = 1; left_row < N - 1; ++left_row) {
        int idx = 0;
        for(int col = 0; col < N - left_row; ++col) {
            indices[idx] = col * N + left_row + col;
            coeffs[idx] = 1.0;
            ++idx;
        }
        error = GRBaddconstr(model, idx, indices, coeffs, GRB_LESS_EQUAL, 1.0,
                             NULL);
        checkGRBError(error, env);
    }
    // one per upper diagonal / //
    for(int left_row = 1; left_row < N; ++left_row) {
        int idx = 0;
        for(int col = 0; col < left_row + 1; ++col) {
            indices[idx] = col * N + left_row - col;
            coeffs[idx] = 1.0;
            ++idx;
        }
        error = GRBaddconstr(model, idx, indices, coeffs, GRB_LESS_EQUAL, 1.0,
                             NULL);
        checkGRBError(error, env);
    }
    // // one per lower diagonal / //
    for(int bottom_col = 1; bottom_col < N - 1; ++bottom_col) {
        int idx = 0;
        for(int col = bottom_col; col < N; ++col) {
            indices[idx] = col * N + (N - 1 - (col - bottom_col));
            coeffs[idx] = 1.0;
            idx++;
        }
        error = GRBaddconstr(model, idx, indices, coeffs, GRB_LESS_EQUAL, 1.0,
                             NULL);
        checkGRBError(error, env);
    }

    // Load the problem into Gurobi (effectively ready to optimize)
    error = GRBupdatemodel(model);
    checkGRBError(error, env);

    int num_constraints;
    error = GRBgetintattr(model, GRB_INT_ATTR_NUMCONSTRS, &num_constraints);
    checkGRBError(error, env);

    const int model_time_us = chrono.lapTimeUs();
    std::optional<int> solve_time_ms;

    if(N < 20) {
        error = GRBoptimize(model);
        checkGRBError(error, env);
        const int solve_time_ms = chrono.lapTimeMs();
        double * sol = (double *)malloc(sizeof(double) * num_variables);
        error =
            GRBgetdblattrarray(model, GRB_DBL_ATTR_X, 0, num_variables, sol);
        checkGRBError(error, env);

        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) {
                std::print("{}", sol[i * N + j] > 0.5 ? '#' : '+');
            }
            std::println();
        }
        free(sol);
    }

    free(vtype);
    free(indices);
    free(coeffs);
    GRBfreemodel(model);
    GRBfreeenv(env);

    std::print(stderr, R"({{
    "solver_name" : "Gurobi",
    "N" : {},
    "num_variables" : {},
    "num_constraints" : {},
    "model_time_us" : {})",
               N, num_variables, num_constraints, model_time_us);
    if(solve_time_ms.has_value()) {
        std::print(stderr, R"(,
    "solve_time_ms" : {})",
                   solve_time_ms.value());
    }
    std::println(stderr, "\n}}");

    return EXIT_SUCCESS;
}
