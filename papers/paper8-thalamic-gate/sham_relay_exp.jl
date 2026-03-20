#!/usr/bin/env julia
"""
Sham Relay Control Experiment
Same as ThalamicGate but WITHOUT ascending arousal input to the relay.
Tests whether the improvement comes from gating or simply adding extra neurons/pathway.

3 conditions × 10 seeds × 700 trials:
1. Baseline (no relay) - already have data
2. ThalamicGate (relay + ascending) - already have data
3. Sham relay (relay, NO ascending) - THIS EXPERIMENT
"""

using Neuroblox, OrdinaryDiffEq, DataFrames, CSV, Random, Statistics
import Neuroblox: system_wiring_rule!, get_exci_neurons, get_inh_neurons, get_weight,
    namespaced_name, hypergeometric_connections!, NGNMM_theta

println("=== Sham Relay Control (No Ascending) ===")
flush(stdout)

struct ShamRelay <: AbstractComposite
    name::Symbol
    namespace::Union{Nothing, Symbol}
    relay_neurons::Vector{HHNeuronExci}
    graph::GraphSystem

    function ShamRelay(; name, namespace=nothing, N_relay=20,
                       E_syn=0.0, G_syn=3.0, τ=5.0)
        inner_namespace = namespaced_name(namespace, name)
        relay_neurons = map(1:N_relay) do i
            HHNeuronExci(
                name = Symbol("relay$i"),
                namespace = inner_namespace,
                E_syn = E_syn, G_syn = G_syn, τ = τ,
            )
        end
        g = GraphSystem()
        for n in relay_neurons
            system_wiring_rule!(g, n)
        end
        new(name, namespace, relay_neurons, g)
    end
end

Neuroblox.get_exci_neurons(sr::ShamRelay) = sr.relay_neurons

function Neuroblox.system_wiring_rule!(g, cb::Cortical, sr::ShamRelay; kwargs...)
    neurons_src = get_exci_neurons(cb)
    neurons_dst = get_exci_neurons(sr)
    hypergeometric_connections!(g, neurons_src, neurons_dst, cb.name, sr.name; kwargs...)
end

function Neuroblox.system_wiring_rule!(g, sr::ShamRelay, cb::Cortical; kwargs...)
    neurons_src = get_exci_neurons(sr)
    neurons_dst = get_exci_neurons(cb)
    hypergeometric_connections!(g, neurons_src, neurons_dst, sr.name, cb.name; kwargs...)
end

# NO NGNMM_theta -> ShamRelay dispatch (that's the point!)

time_block_dur = 90.0
N_trials = 700
trial_dur = 1000.0
seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]

csv_path = joinpath(homedir(), ".julia/packages/Neuroblox/mdbeB/examples/smaller_cs_stimuli_set.csv")
all_results = DataFrame(seed=Int[], trial=Int[], correct=Bool[], action=Int[])

for (si, seed) in enumerate(seeds)
    println("\n=== Seed $seed ($si/$(length(seeds))) ===")
    flush(stdout)

    Random.seed!(seed)
    rrng() = Xoshiro(rand(Int))
    model_name = :g

    image_set = CSV.read(csv_path, DataFrame)
    image_set = image_set[1:N_trials, :]

    @named stim = ImageStimulus(image_set; namespace=model_name, t_stimulus=trial_dur, t_pause=0)
    @named VAC = Cortical(; namespace=model_name, N_wta=4, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named AC = Cortical(; namespace=model_name, N_wta=2, N_exci=5, density=0.05, weight=1, rng=rrng())
    @named sham = ShamRelay(; namespace=model_name, N_relay=20)

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
        K=0.06, decay=0.01, α=2.5, θₘ=1, modulator=SNcb,
        t_pre=trial_dur, t_post=trial_dur, t_mod=time_block_dur)
    hebbian_cort = HebbianPlasticity(K=5e-4, W_lim=7, t_pre=trial_dur, t_post=trial_dur)

    g = GraphSystem()
    add_connection!(g, stim => VAC, weight=14, rng=rrng())
    add_connection!(g, ASC1 => VAC, weight=44, rng=rrng())
    add_connection!(g, ASC1 => AC, weight=44, rng=rrng())

    # Direct path (same as baseline and gate conditions)
    add_connection!(g, VAC => AC, weight=3, density=0.1, learning_rule=hebbian_cort, rng=rrng())

    # Sham relay path (same structure as gate, but NO ascending input to relay)
    add_connection!(g, VAC => sham, weight=1, density=0.1, rng=rrng())
    add_connection!(g, sham => AC, weight=1, density=0.1, rng=rrng())
    # NOTE: NO add_connection!(g, ASC1 => sham, ...) — this is the control

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
    trace = run_experiment!(agent, env; alg=Vern7(), t_warmup=200.0, modulator=SNcb)
    elapsed = time() - t0

    n_correct = count(trace.correct)
    accuracy = n_correct / N_trials * 100
    first50 = round(100 * sum(trace.correct[1:50]) / 50, digits=1)
    last50 = round(100 * sum(trace.correct[end-49:end]) / 50, digits=1)

    println("Seed $seed: $(n_correct)/$(N_trials) ($(round(accuracy, digits=1))%) in $(round(elapsed, digits=1))s")
    println("  First 50: $(first50)% | Last 50: $(last50)%")
    flush(stdout)

    for t in 1:N_trials
        push!(all_results, (seed=seed, trial=t, correct=trace.correct[t], action=trace.action[t]))
    end
end

output_path = joinpath(homedir(), "Documents/TsubasaWorkspace/neuroblox_bench/sham_relay_multi_seed.csv")
CSV.write(output_path, all_results)
println("\n=== All seeds complete ===")
println("Results saved to: $output_path ($(nrow(all_results)) rows)")
flush(stdout)
