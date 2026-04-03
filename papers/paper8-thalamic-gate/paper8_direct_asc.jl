#!/usr/bin/env julia
"""
Paper 8 追試: Direct ASC→AC control
ASC input directly to AC (weight=44, no relay neurons)
Tests: is it the relay pathway that matters, or just extra modulatory drive?
10 seeds (42-51), 700 trials each.
"""

using Neuroblox, OrdinaryDiffEq, DataFrames, CSV, Random, Statistics, Dates
import Neuroblox: system_wiring_rule!, get_exci_neurons, get_inh_neurons,
    namespaced_name, hypergeometric_connections!, NGNMM_theta

println("=== Paper 8: Direct ASC→AC Control ===")
println("Time: $(Dates.now())")
flush(stdout)

time_block_dur = 90.0; N_trials = 700; trial_dur = 1000.0
csv_path = joinpath(homedir(), ".julia/packages/Neuroblox/mdbeB/examples/smaller_cs_stimuli_set.csv")

results = DataFrame(seed=Int[], accuracy=Float64[], n_correct=Int[])

for seed in 42:51
    println("\n--- Seed $seed ---")
    flush(stdout)

    Random.seed!(seed)
    rrng() = Xoshiro(rand(Int))
    model_name = :g

    image_set = CSV.read(csv_path, DataFrame)[1:N_trials, :]
    @named stim = ImageStimulus(image_set; namespace=model_name, t_stimulus=trial_dur, t_pause=0)
    @named VAC = Cortical(; namespace=model_name, N_wta=4, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named AC = Cortical(; namespace=model_name, N_wta=2, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named ASC1 = NextGenerationEI(; namespace=model_name, Cₑ=2*26, Cᵢ=1*26,
        alpha_invₑₑ=10.0/26, alpha_invₑᵢ=0.8/26, alpha_invᵢₑ=10.0/26, alpha_invᵢᵢ=0.8/26,
        kₑᵢ=0.6*26, kᵢₑ=0.6*26)
    @named STR1 = Striatum(; namespace=model_name, N_inhib=5)
    @named STR2 = Striatum(; namespace=model_name, N_inhib=5)
    @named tan_pop1 = TAN(κ=10; namespace=model_name, rng=rrng())
    @named tan_pop2 = TAN(κ=10; namespace=model_name, rng=rrng())
    @named AS = GreedyPolicy(; namespace=model_name, t_decision=2*time_block_dur)
    @named SNcb = SNc(κ_DA=1; namespace=model_name)

    hebbian_mod = HebbianModulationPlasticity(K=0.06, decay=0.01, α=2.5, θₘ=1,
        modulator=SNcb, t_pre=trial_dur, t_post=trial_dur, t_mod=time_block_dur)
    hebbian_cort = HebbianPlasticity(K=5e-4, W_lim=7, t_pre=trial_dur, t_post=trial_dur)

    g = GraphSystem()
    # Standard circuit
    add_connection!(g, stim => VAC, weight=14, rng=rrng())
    add_connection!(g, ASC1 => VAC, weight=44, rng=rrng())
    add_connection!(g, ASC1 => AC, weight=88, rng=rrng())  # doubled: baseline 44 + extra 44 (matching relay ASC→Gate weight)
    add_connection!(g, VAC => AC, weight=3, density=0.1, learning_rule=hebbian_cort, rng=rrng())
    # NO ThalamicGate — ascending arousal goes directly to AC at double weight

    add_connection!(g, AC => STR1, weight=0.075, density=0.04, learning_rule=hebbian_mod, rng=rrng())
    add_connection!(g, AC => STR2, weight=0.075, density=0.04, learning_rule=hebbian_mod, rng=rrng())
    add_connection!(g, tan_pop1 => STR1, weight=1, t_event=time_block_dur, rng=rrng())
    add_connection!(g, tan_pop2 => STR2, weight=1, t_event=time_block_dur, rng=rrng())
    add_connection!(g, STR1 => tan_pop1, weight=1, rng=rrng())
    add_connection!(g, STR2 => tan_pop1, weight=1, rng=rrng())
    add_connection!(g, STR1 => tan_pop2, weight=1, rng=rrng())
    add_connection!(g, STR2 => tan_pop2, weight=1, rng=rrng())
    add_connection!(g, STR1 => STR2, weight=1, t_event=2*time_block_dur, rng=rrng())
    add_connection!(g, STR2 => STR1, weight=1, t_event=2*time_block_dur, rng=rrng())
    add_connection!(g, STR1 => SNcb, weight=1, rng=rrng())
    add_connection!(g, STR2 => SNcb, weight=1, rng=rrng())
    add_connection!(g, STR1 => AS, rng=rrng())
    add_connection!(g, STR2 => AS, rng=rrng())
    # Note: NO VAC→ThalamicGate→AC path. Just extra ASC→AC.

    env = ClassificationEnvironment(stim, N_trials)
    agent = Agent(g; t_block=time_block_dur)

    t0 = time()
    trace = run_experiment!(agent, env; alg=Vern7(), t_warmup=200.0, modulator=SNcb, save_everystep=false)
    elapsed = time() - t0

    n_correct = count(trace.correct)
    accuracy = n_correct / N_trials * 100
    push!(results, (seed=seed, accuracy=accuracy, n_correct=n_correct))

    println("Seed $seed: $n_correct/$N_trials ($(round(accuracy, digits=1))%) in $(round(elapsed, digits=1))s")
    flush(stdout)
end

# Summary
mean_acc = mean(results.accuracy)
sd_acc = std(results.accuracy)
println("\n=== Direct ASC→AC Summary ===")
println("Mean: $(round(mean_acc, digits=1))% (SD=$(round(sd_acc, digits=1)))")
println("N=10 seeds")
flush(stdout)

# Save
CSV.write(joinpath(@__DIR__, "direct_asc_control_results.csv"), results)
println("Saved: direct_asc_control_results.csv")
