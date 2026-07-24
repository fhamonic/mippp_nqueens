using JuMP
import LinearAlgebra

const SOLVERS = Dict(
    "Highs"  => (:HiGHS,  :Optimizer),
    "GLPK"   => (:GLPK,   :Optimizer),
    "Cbc"    => (:Cbc,    :Optimizer),
    "Gurobi" => (:Gurobi, :Optimizer),
)

if length(ARGS) < 2
    println(stderr, "Usage: julia $(PROGRAM_FILE) <solver> <N>")
    exit(1)
end

solver_key = ARGS[1]
haskey(SOLVERS, solver_key) || error("Unknown solver $(solver_key).")

N = parse(Int, ARGS[2])
N > 0 || error("N must be positive, got $(N).")

# Load only the requested solver.
pkg, opt = SOLVERS[solver_key]
api_time = @elapsed @eval import $pkg
OPTIMIZER = @eval $pkg.$opt

function build_model(N, optimizer)
    model = Model(optimizer)

    @variable(model, x[1:N, 1:N], Bin)

    # Store reverse, doing it inside the for is O(N^3) -> 10x longer for N=1000
    xr = reverse(x; dims = 1) 

    # One queen in a given row/column
    for i in 1:N
        @constraint(model, sum(x[i, :]) == 1)
        @constraint(model, sum(x[:, i]) == 1)
    end
    # One queen on any given diagonal (skip length-1 corner diagonals)
    for i in -(N-2):(N-2)
        @constraint(model, sum(LinearAlgebra.diag(x, i)) <= 1)
        @constraint(model, sum(LinearAlgebra.diag(xr, i)) <= 1)
    end
    return model
end

cold_model_time = @elapsed model = build_model(N, OPTIMIZER)
warm_model_time = @elapsed model = build_model(N, OPTIMIZER)

as_milliseconds(t) = round(Int, t * 1e3)

println(stderr,
    """{"solver_name":"$(solver_name(model))",""" *
    """"N":$(N),""" *
    """"num_variables":$(num_variables(model)),""" *
    """"num_constraints":$(num_constraints(model; count_variable_in_set_constraints = false)),""" *
    """"api_time_ms":$(as_milliseconds(api_time)),""" *
    """"cold_model_time_ms":$(as_milliseconds(cold_model_time)),""" *
    """"model_time_ms":$(as_milliseconds(warm_model_time))}"""
)