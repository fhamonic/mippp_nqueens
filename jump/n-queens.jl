# N-Queens model fill benchmark for JuMP, adapted from the JuMP tutorial
# originally contributed by Matthew Helm and Mathieu Tanneau (MIT license).
#
# As in the python-mip benchmarks, only the model fill time is measured, and
# a warm-up run is performed first so that the reported times exclude Julia's
# JIT compilation. Note that the timer covers the constraint construction
# (variable creation happens before it), and that JuMP builds the model in its
# own backend-independent representation, only copied to the solver on
# optimize!().
#
# Usage: julia jump/n-queens.jl [output.csv]

using JuMP
import HiGHS
import LinearAlgebra

function build(N)
    model = Model(HiGHS.Optimizer)
    set_silent(model)

    @variable(model, x[1:N, 1:N], Bin)

    t = @elapsed begin
        # There must be exactly one queen in a given row/column
        for i in 1:N
            @constraint(model, sum(x[i, :]) == 1)
            @constraint(model, sum(x[:, i]) == 1)
        end

        # There can only be one queen on any given diagonal
        for i in -(N-1):(N-1)
            @constraint(model, sum(LinearAlgebra.diag(x, i)) <= 1)
            @constraint(model, sum(LinearAlgebra.diag(reverse(x; dims = 1), i)) <= 1)
        end
    end
    return t
end

out = length(ARGS) >= 1 ? ARGS[1] : "queens-jump.csv"

build(100)  # warm-up: JIT compilation

open(out, "w") do f
    for N in 100:100:1000
        t = build(N)
        println(f, "$(N),$(round(Int, 1000 * t))")
        flush(f)
        println("$(N)-queens: $(round(1000 * t; digits = 1)) ms")
    end
end
