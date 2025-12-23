#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>

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

    error = GRBloadenv(&env, NULL);
    checkGRBError(error, env);

    const int num_variables = N * N;
    const int num_constraints = 6 * N - 6;
    const int num_entries = 4 * num_variables - 4;

    char * vtype = (char *)malloc(sizeof(char) * num_variables);
    memset(vtype, GRB_BINARY, num_variables);
    error = GRBnewmodel(env, &model, "nqueens", num_variables, NULL, NULL, NULL,
                        vtype, NULL);
    checkGRBError(error, env);

    char * sense = (char *)malloc(sizeof(char) * num_constraints);
    memset(sense, GRB_EQUAL, 2 * N);
    memset(sense + 2 * N, GRB_LESS_EQUAL, 4 * N - 6);
    double * rhs = (double *)malloc(sizeof(double) * num_constraints);
    std::fill(rhs, rhs + num_constraints, 1.0);
    int * cbeg = (int *)malloc(sizeof(int) * num_constraints);
    int * cind = (int *)malloc(sizeof(int) * num_entries);
    double * cval = (double *)malloc(sizeof(double) * num_entries);
    std::fill(cval, cval + num_entries, 1.0);

    int row_cpt = 0;
    int idx = 0;

    // one per row and column
    for(int i = 0; i < N; ++i) {
        cbeg[row_cpt++] = idx;
        for(int col = 0; col < N; ++col) cind[idx++] = col * N + i;
        cbeg[row_cpt++] = idx;
        for(int row = 0; row < N; ++row) cind[idx++] = i * N + row;
    }
    // one per upper diagonal \ //
    for(int top_col = 0; top_col < N - 1; ++top_col) {
        cbeg[row_cpt++] = idx;
        for(int row = 0; row < N - top_col; ++row)
            cind[idx++] = (top_col + row) * N + row;
    }
    // one per lower diagonal \ //
    for(int left_row = 1; left_row < N - 1; ++left_row) {
        cbeg[row_cpt++] = idx;
        for(int col = 0; col < N - left_row; ++col)
            cind[idx++] = col * N + left_row + col;
    }
    // one per upper diagonal / //
    for(int left_row = 1; left_row < N; ++left_row) {
        cbeg[row_cpt++] = idx;
        for(int col = 0; col < left_row + 1; ++col)
            cind[idx++] = col * N + left_row - col;
    }
    // one per lower diagonal / //
    for(int bottom_col = 1; bottom_col < N - 1; ++bottom_col) {
        cbeg[row_cpt++] = idx;
        for(int col = bottom_col; col < N; ++col)
            cind[idx++] = col * N + (N - 1 - (col - bottom_col));
    }

    error = GRBaddconstrs(model, num_constraints, num_entries, cbeg, cind, cval,
                          sense, rhs, NULL);
    checkGRBError(error, env);
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
    free(sense);
    free(rhs);
    free(cbeg);
    free(cind);
    free(cval);

    GRBfreemodel(model);
    GRBfreeenv(env);

    fprintf(stderr, ",%d", fill_time_us);

    return 0;
}
