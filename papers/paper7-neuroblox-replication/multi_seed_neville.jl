#!/usr/bin/env julia
"""
Multi-seed Neville analysis — 10 seeds × 700 trials
Output: CSV with per-trial data for Python analysis
"""

using Neuroblox, OrdinaryDiffEq, DataFrames, CSV, Random, Statistics

println("=== Multi-seed Neville Analysis ===")

seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
time_block_dur = 90.0
N_trials = 700
trial_dur = 1000.0

csv_path = joinpath(homedir(), ".julia/packages/Neuroblox/mdbeB/examples/smaller_cs_stimuli_set.csv")

all_results = DataFrame()

for (si, seed) in enumerate(seeds)
    println("\n--- Seed $seed ($si/$(length(seeds))) ---")
    Random.seed!(seed)
    rrng() = Xoshiro(rand(Int))

    image_set = CSV.read(csv_path, DataFrame)
    image_set = image_set[1:N_trials, :]
    categories = image_set.category
    model_name = :g

    @named stim = ImageStimulus(image_set; namespace=model_name, t_stimulus=trial_dur, t_pause=0)
    @named VAC = Cortical(; namespace=model_name, N_wta=4, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named AC = Cortical(; namespace=model_name, N_wta=2, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named ASC1 = NextGenerationEI(; namespace=model_name,
        Cₑ=2*26, Cᵢ=1*26, alpha_invₑₑ=10.0/26, alpha_invₑᵢ=0.8/26,
        alpha_invᵢₑ=10.0/26, alpha_invᵢᵢ=0.8/26, kₑᵢ=0.6*26, kᵢₑ=0.6*26)
    @named STR1 = Striatum(; namespace=model_name, N_inhib=5)
    @named STR2 = Striatum(; namespace=model_name, N_inhib=5)
    @named tan_pop1 = TAN(κ=10; namespace=model_name, rng=rrng())
    @named tan_pop2 = TAN(κ=10; namespace=model_name, rng=rrng())
    @named AS = GreedyPolicy(; namespace=model_name, t_decision=2*time_block_dur)
    @named SNcb = SNc(κ_DA=1; namespace=model_name)

    hebbian_mod = HebbianModulationPlasticity(
        K=0.06, decay=0.01, α=2.5, θₘ=1,
        modulator=SNcb, t_pre=trial_dur, t_post=trial_dur, t_mod=time_block_dur)
    hebbian_cort = HebbianPlasticity(K=5e-4, W_lim=7, t_pre=trial_dur, t_post=trial_dur)

    g = GraphSystem()
    add_connection!(g, stim => VAC, weight=14, rng=rrng())
    add_connection!(g, ASC1 => VAC, weight=44, rng=rrng())
    add_connection!(g, ASC1 => AC, weight=44, rng=rrng())
    add_connection!(g, VAC => AC, weight=3, density=0.1, learning_rule=hebbian_cort, rng=rrng())
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

    env = ClassificationEnvironment(stim, N_trials)
    agent = Agent(g; t_block=time_block_dur)

    t0 = time()
    trace = run_experiment!(agent, env; alg=Vern7(), t_warmup=200.0, modulator=SNcb, save_everystep=false)
    elapsed = time() - t0

    n_correct = count(trace.correct)
    acc = n_correct / N_trials * 100

    # Build per-trial DataFrame
    seed_df = DataFrame(
        seed = fill(seed, N_trials),
        trial = 1:N_trials,
        correct = trace.correct,
        action = trace.action,
        category = categories[1:N_trials],
        DA = trace.DA
    )
    append!(all_results, seed_df)

    println("  Accuracy: $n_correct/$N_trials ($(round(acc, digits=1))%) in $(round(elapsed, digits=1))s")
end

# Save all results
outpath = joinpath(@__DIR__, "multi_seed_results.csv")
CSV.write(outpath, all_results)
println("\n=== All seeds complete ===")
println("Saved $(nrow(all_results)) rows to $outpath")
