#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gurobi_c.h"

#include "chrono.hpp"

void checkGRBError(int error, GRBenv * env) {
    if(error) {
        fprintf(stderr, "Gurobi Error: %s\n", GRBgeterrormsg(env));
        exit(1);
    }
}

int main(int argc, char * argv[]) {
    if(argc != 2) {
        printf("Usage: %s N\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);

    Chrono chrono;

    GRBenv * env = NULL;
    GRBmodel * model = NULL;
    int error;

    // Create environment
    error = GRBloadenv(&env, NULL);
    checkGRBError(error, env);

    // Create empty model
    error =
        GRBnewmodel(env, &model, "nqueens", 0, NULL, NULL, NULL, NULL, NULL);
    checkGRBError(error, env);

    // Add N*N binary variables x[i][j] = 1 if queen in row i, column j
    const int num_variables = N * N;
    char * vtype = (char *)malloc(sizeof(char) * num_variables);
    memset(vtype, GRB_BINARY, num_variables);

    error = GRBaddvars(model, num_variables, 0, NULL, NULL, NULL, NULL, NULL,
                       NULL, vtype, NULL);
    checkGRBError(error, env);

    // Constraints:
    int * indices = (int *)malloc(sizeof(int) * N);
    double * coeffs = (double *)malloc(sizeof(double) * N);

    // one queen per row and column
    for(int i = 0; i < N; ++i) {
        for(int col = 0; col < N; ++col) {
            indices[col] = col * N + i;
            coeffs[col] = 1.0;
        }
        error = GRBaddconstr(model, N, indices, coeffs, GRB_EQUAL, 1.0, NULL);
        checkGRBError(error, env);
        for(int row = 0; row < N; ++row) {
            indices[row] = i * N + row;
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

    int fill_time_us = chrono.lapTimeUs();

    if(N < 20) {
        error = GRBoptimize(model);
        checkGRBError(error, env);
        double * sol = (double *)malloc(sizeof(double) * num_variables);
        error =
            GRBgetdblattrarray(model, GRB_DBL_ATTR_X, 0, num_variables, sol);
        checkGRBError(error, env);

        printf("Solution for %d-Queens:\n", N);
        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) {
                printf("%c ", sol[i * N + j] > 0.5 ? 'o' : '.');
            }
            printf("\n");
        }
        free(sol);
    }

    free(vtype);
    free(indices);
    free(coeffs);
    GRBfreemodel(model);
    GRBfreeenv(env);

    fprintf(stderr, ",%d", fill_time_us);

    return 0;
}
