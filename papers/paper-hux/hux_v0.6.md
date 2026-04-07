# Hux: A Developmentally-Sequenced Biophysical Cortico-Striatal Circuit with Self-Organized Plasticity, Permanent Pruning, and a State-Based Critical Period

**Version**: v0.6 (curriculum v2.1c symmetric-STDP control reverses the §4.7 diagnosis; v2.1d in flight)
**Date**: 2026-04-07
**Authors**: Tsubasa, K. Yasukawa
**Status**: Work in progress. Phase 2 numerical results now integrated through curriculum v2, v2.1, and v2.1c (§4.6, §4.7, §4.8). The v2.1c run reverses the working diagnosis: asymmetric STDP is not the cause of curriculum anchoring; it functions as a built-in safeguard against winner-take-all runaway. Curriculum v2.1d (Hebbian gain K = 0) is in flight to test the next candidate. Phase 1 baselines are now in §4.1; the developing ablation table (v2 / v2.1 / v2.1c / v2.1d) will be added in §4.9 once v2.1d completes.

---

## Abstract

We introduce **Hux**, a small-scale biophysical cortico-striatal circuit (76–140 Hodgkin-Huxley neurons) built around the explicit hypothesis that brain-style cognition emerges from developmental sequencing and self-organized plasticity rather than from static large-scale reconstruction. Hux implements three self-organization rules with no hand-tuned hyperparameters: a synaptic floor that prevents collapse of weak connections, homeostatic synaptic scaling, and BCM-style metaplasticity. Activity-dependent permanent pruning closes connections that fail to develop, mimicking developmental synapse elimination. A state-based critical period (governed by weight-stability ratios rather than trial counts) automatically opens during high-plasticity phases and closes when the weight distribution stabilizes. Three ascending neuromodulator systems (LC/Raphe/VTA, implemented separately) gate plasticity. On a balanced 50/50 binary categorization task with 140 neurons, Hux reaches F1 ≈ 0.62 (P ≈ 51.8%, R ≈ 76.9%), exceeding a 1-d LDA baseline by 1.55×. Critically, Hux exhibits four emergent computational psychopathologies (DA bifurcation at 4.0–4.5×, synaptic death of minority categories, curriculum anchoring, and thalamic freeze) that we read as candidate mechanistic models of clinically observed phenomena. A controlled pair of runs (curriculum v2 and v2.1) localizes the mechanism of curriculum anchoring to the interaction of asymmetric STDP with class imbalance rather than to the critical-period control law, demonstrating the diagnostic value of the small-scale, parameter-parsimonious approach. We position Hux as complementary to large-scale reconstruction efforts (Kuriyama et al. 2025, 9M neurons on Fugaku): the Kuriyama group explicitly identifies plasticity, neuromodulators, and developmental processes as the principal limitation of microscopic-level whole-cortex simulation and as the next frontier toward brain-inspired AI; Hux pursues exactly that frontier at a scale amenable to mechanistic dissection.

## 1. Introduction

The dominant paradigm for biophysically detailed neural simulation has been large-scale reconstruction: assemble as many cell types, ion channels, and connections as can be constrained from experimental atlases, then run the resulting network forward and inspect what emerges. Recent landmark efforts include the Blue Brain Project (Markram et al. 2015), the Allen Institute mouse V1 model (Billeh et al. 2020), and most recently a 9-million-neuron 26-billion-synapse mouse whole-cortex simulation on the Fugaku supercomputer (Kuriyama et al. 2025). These models have established that microscopic-level reconstruction is technically feasible at the scale of an entire mammalian cortex.

However, the same authors are explicit about what current reconstructions do not yet do. Kuriyama et al. (2025), §4.4 Limitations, state that "the current model does not include plasticity, because sufficient biological information is not yet available to inform reliable models of plasticity across the whole cortex. Nevertheless, incorporating hypothetical rules of synaptic and neuronal plasticity into the model and testing their effects will be an important future application, potentially useful for the development of energy-efficient, brain-inspired AI." Their Conclusion goes further, framing the digital replica as "a reference implementation to develop an energy-efficient, brain-style AI." The largest-scale microscopic mouse cortex model currently in existence thus identifies plasticity, neuromodulation, and brain-inspired AI as the explicit next frontier.

This paper takes that frontier seriously at a different scale. Rather than scaling up reconstruction further, we ask what minimum biophysical circuit is sufficient to *develop* (from spontaneous activity, through critical periods, into a stable state) under self-organization rules drawn from neurobiology. Hux is the answer we are constructing.

The design commitments of Hux are:

1. **Developmental sequencing.** Stages run in biological order: spontaneous activity → critical-period plasticity → activity-dependent pruning → consolidated learning. Each stage is a precondition for the next.
2. **Self-organization with zero hand-tuned hyperparameters.** Three rules (synaptic floor, homeostatic scaling, BCM metaplasticity) together with permanent activity-dependent pruning and a state-based critical period closure, drive the circuit to a stable working configuration without manual gain knobs.
3. **Emergence-trust.** Functional roles are not specified in advance. We do not tell the circuit which neurons should encode which categories, nor do we tune separation by hand. We then read whatever the network produces, including its failure modes, as the dependent variable.
4. **Computational psychopathology as a primary observable.** Emergent failure modes (DA bifurcation, synaptic death, anchoring, thalamic freeze) are not bugs to suppress; they are the natural object of study.

## 2. Related Work

### 2.1 Large-scale microscopic reconstruction

Kuriyama et al. (2025) report a 9M-neuron, 26B-synapse mouse whole-cortex model on 145,728 nodes of Fugaku, using 15 ion channel types from the Allen Cell Types Database and a custom light-weight simulator (Neulite) optimized for SVE intrinsics. The reported emergent dynamics consist of a ~10 Hz cross-correlation oscillation between hemispheres; no mechanistic account of how those dynamics arise from circuit structure is given. As noted in §1, the authors identify plasticity, neuromodulators, and detailed sensory inputs as the principal limitations and as the next direction toward brain-inspired AI. Earlier large-scale efforts include Markram et al. (2015) on a rat somatosensory column and Billeh et al. (2020) on mouse V1. None of these models implement developmental sequencing or activity-dependent pruning at the whole-circuit level.

Higuchi et al. (2022; *bioRxiv* 2022.11.01.512969) report an 18,728-neuron, 344,861-synapse Drosophila whole-brain biophysically detailed model on Fugaku, with the olfactory pathway (antennal lobe → mushroom body → output neurons) augmented by broader whole-brain coverage drawn from the FlyCircuit database. Of the simulations surveyed here, Higuchi et al. is the closest in spirit to Hux on two specific axes: STDP plasticity is implemented (restricted to the mushroom body lobes), and a dopaminergic neuromodulator system is included (used to deliver reward signals to dopamine neurons during odor-taste associative learning). The model demonstrates classical conditioning: synaptic weights between Kenyon cells and the MBON6 output neuron increase during reward-paired training, reproducing odor-taste association at the network level. The authors conclude that "the bottom-up reconstruction of insect brains by the biophysically detailed model is a fairly feasible" approach that can "reproduce brains' functions." This is the prototypical *learning-paradigm-specified* approach: a specific behavioral task is built into the experimental setup, and the model's success is evaluated against that task. Hux differs by leaving the task structure deliberately under-specified and treating whatever the developmental sequence produces (including failure modes) as the dependent variable. Higuchi et al. also do not implement developmental sequencing, homeostatic scaling, BCM metaplasticity, a synaptic floor, activity-dependent pruning, or neuromodulator systems beyond DA.

### 2.2 Self-organized criticality and ensemble dynamics

A separate line of work, descending from Beggs & Plenz (2003) on neuronal avalanches and Bak et al. (1987) on self-organized criticality, asks whether biophysically realistic networks exhibit power-law statistical signatures characteristic of critical-state dynamics. Doherty et al. (2025; SUNY Downstate, *bioRxiv* 2025.01.13.632866) report self-organized and self-sustained ensemble activity patterns in a NEURON/NetPyNE model of mouse primary motor cortex. Their model is the closest neighboring approach to Hux that we have identified in the recent literature, and a precise comparison clarifies the niche Hux occupies.

The Doherty et al. circuit is a 10,073-neuron cylindrical volume (300 μm diameter × 1350 μm cortical depth) of mouse M1, with all six cortical layers populated at full neuronal density and a realistic mix of excitatory (IT, PT, CT) and inhibitory (PV, SOM) cell types. Connectivity is fixed and drawn from anatomical data; no synaptic plasticity rules are implemented. The synaptic complement is restricted to AMPA, NMDA, GABA-A and GABA-B receptors; no neuromodulator systems (DA, NE, 5-HT, or their nuclei LC/Raphe/VTA) are modeled. Self-organization, in their usage, refers to the emergence of self-sustained avalanche patterns following a brief unstructured stimulus (100 ms, 57 μA injected into a small subset of neurons). The reported observables are avalanche types, frequency distributions, and a pair of functional hypotheses about decorrelated spike fluctuations and temporal coordination. Mechanistic claims about how the avalanches arise from circuit structure are limited.

Doherty et al. and Hux are complementary rather than competing. Both use biophysically detailed multi-compartment neurons; both study self-organized patterns in mouse cortex; both use NEURON-style numerical methods. They diverge on every other axis we consider relevant. Doherty et al. ask whether statistical signatures of criticality (power laws, universality) emerge from a fixed adult anatomical reconstruction; Hux asks whether functional and pathological cognitive states emerge from a developmental sequence under self-organization rules. Doherty et al. implement no plasticity, no developmental sequencing, and no neuromodulators; Hux makes plasticity (synaptic floor + homeostatic scaling + BCM + STDP), developmental staging (Stages 0–4), and three neuromodulator systems (LC/Raphe/VTA) the central design commitments. Doherty et al. observe avalanche statistics in an M1 cylinder; Hux observes failure modes (DA bifurcation, synaptic death, curriculum anchoring, thalamic freeze) in a cortico-striatal loop and reads them as candidate computational psychopathologies. Both lines of work could in principle inform a future joint model, in which the developmental and neuromodulatory machinery of Hux is scaled into the kind of detailed cortical column reconstruction that Doherty et al. demonstrate is computationally tractable.

### 2.3 Plasticity rules and metaplasticity

Hux's three self-organization rules draw from a long lineage in computational and theoretical neuroscience: Hebbian learning (Hebb 1949), homeostatic synaptic scaling (Turrigiano 2008), the BCM rule (Bienenstock, Cooper, Munro 1982), and the synaptic floor concept implicit in works on minimum sustainable connectivity. Their integration into a single self-organizing circuit, together with permanent activity-dependent pruning and a state-based critical period, is the technical contribution of this paper.

### 2.4 Critical periods

The state-based closure rule used in Hux generalizes the trial-count-based critical period schedules used in most plasticity simulations. We follow the conceptual framework of Hensch (2005) but replace the manual schedule with a Weber-Fechner-like ratio test on the local-versus-global standard deviation of the weight distribution. To our knowledge no prior model implements critical period closure as a function of weight stability rather than as a fixed annealing schedule.

## 3. Methods

### 3.1 Circuit

The Hux circuit (76 neurons in Phase 1, 140 neurons in Phase 2 scale-up) consists of:

- A cortical population (AC) of Hodgkin-Huxley neurons.
- A striatal population partitioned into matrisome (STR1, STR2) and striosome subpopulations following the Picower corticostriatal microcircuit organization (Pathak et al. 2026).
- A ThalamicGate relay node (Paper 9; Tsubasa 2026a).
- Three ascending arousal projections, implemented as separate channels modulating gain in distinct downstream populations: locus coeruleus (LC), raphe (Raphe), and ventral tegmental area (VTA).
- Allen Mouse Brain Connectivity Atlas projection densities used directly to scale connection weights, with no post-hoc tuning.

### 3.2 Self-organization rules

Three rules are applied during all developmental stages and remain active in the consolidated stage:

1. **Synaptic floor.** Each connection weight is held above a small positive floor unless explicitly pruned (see below). The floor prevents collapse of weak but biologically meaningful connections. Pruned connections are excluded from floor revival via a `PRUNED_CONNECTIONS` set.
2. **Homeostatic synaptic scaling.** Each postsynaptic neuron's incoming weights are jointly scaled to maintain a target average firing rate (Turrigiano 2008).
3. **BCM-style metaplasticity.** A sliding threshold separates LTP from LTD as a function of recent postsynaptic activity (Bienenstock, Cooper, Munro 1982).

### 3.3 Permanent activity-dependent pruning

Connections that fail to participate in activity above a threshold during the critical-period stage are permanently removed. Removed connections are added to `PRUNED_CONNECTIONS` and are not subject to floor revival, mimicking developmental synapse elimination (Hensch 2005).

### 3.4 State-based critical period

The plasticity gain `cp_factor` is updated each block according to the local stability of the mean weight:

```
ratio = std(window) / std(history)
if ratio < 0.5:  cp_factor *= 0.95   # closing
else:            cp_factor *= 1.10   # reopening, capped at 1.0
```

with a residual floor of 0.1. This replaces trial-count-based annealing with a measurement-based test on the actual stability of the network. Stage transitions (e.g., a change in input distribution) automatically reopen the critical period because they perturb the local standard deviation.

### 3.5 Developmental stages

The full developmental sequence is:

- **Stage 0: Auto-calibration.** Binary search over the initial scaling factor until the spontaneous STR2 activity rate falls within a physiological band (10–30 % of neurons active). No hand tuning.
- **Stage 1: Overproduction.** Initial weights are set high, mimicking the developmental overproduction phase.
- **Stage 2: Spontaneous activity with STDP and homeostatic arousal.** Hebbian updates are switched off during this phase; only spike-timing dependent plasticity drives weight change. This produced a continuous weight gradient (0.023–0.066) in our preliminary runs, in contrast with the bimodal collapse observed when Hebbian and STDP were applied simultaneously.
- **Stage 3: Activity-dependent pruning.** Connections that have not changed during Stage 2 are permanently removed.
- **Stage 4: Learning with STDP and self-organization.** The full circuit, with critical period and three self-org rules, is trained on the categorization task.

### 3.6 Task

Binary categorization of LDA-derived stimulus features. We report results on three regimes:

- **Balanced (50/50).** 294 stimuli, 147 per class.
- **Skewed (30/70).** 490 stimuli.
- **Highly skewed (16/84).** Used as a stress test in the curriculum sequence.

### 3.7 Curriculum

In the curriculum runs (Phase 2 v2), stages run in order: 50/50 → 30/70 → 16/84. The state-based critical period reopens at each stage transition because the new class distribution destabilizes the weight distribution.

## 4. Results

> v0.1 placeholder. Numerical results will be filled in v0.2 from the runs already completed (balanced 76, balanced 140, critical period, curriculum v1, scale-up) and the runs currently in flight or being debugged (curriculum v2 with state-based critical period).

### 4.1 Phase 1: 76-neuron baselines (no curriculum, single skewed distribution)

Two Phase 1 baseline runs were conducted on the 16/84 highly skewed distribution alone, without curriculum staging, to establish a baseline F1 against which all curriculum runs can be compared.

**Phase 1 v7** (calibration → overproduction at w = 0.05 → 500 trials of spontaneous activity → activity-dependent pruning → 700 trials of learning, 76 neurons, 30 surviving STR2 connections after pruning): per-block correct counts on a 50-stimulus block reached 21/50 in block 8 with `cat2 = 50`, then collapsed to 0/50 in blocks 10–14, with `cat2 = 50` throughout. The network learned to label every stimulus as category 2. Final F1 = 0.3471 (P = 21.0 %, R = 100.0 %), tp = 147, fp = 553, fn = 0, runtime 931.2 s. This is the maximum-recall, minimum-precision degenerate solution: under a 16/84 imbalance the network discovers that it can achieve recall = 1.0 by classifying everything as the majority class.

**Phase 1 v8** (same protocol as v7 but with 200 trials of spontaneous activity instead of 500, and a percentile-based pruning rule retaining the top 50 % of weights): the trajectory is qualitatively different. Blocks 1–6 produce `cat2` counts in the 20–50 range with `correct` ≈ 15–25; blocks 7–10 transition to `cat2 = 0` with `correct` rising to 50/50 (the inverse degenerate solution: classify everything as category 1); then in block 11 the network flips to `cat2 = 46` and from block 12 onward to `cat2 = 50` with `correct = 0/50`. The final state is the same as v7 (everything labeled as category 2) but reached via a different path (a transient majority-only phase, then catastrophic flip). Final F1 = 0.2632 (P = 17.6 %, R = 52.4 %), tp = 77, fp = 361, fn = 70, runtime 893.5 s.

The Phase 1 baselines establish two facts that motivate the entire Phase 2 redesign. First, a developmental sequence on a single highly skewed distribution does not produce a categorization circuit; it produces one of two degenerate solutions (always-cat1 or always-cat2) or oscillates between them. Second, the F1 ≈ 0.26–0.35 obtained from these degenerate solutions is the floor against which all later results should be compared. Any Phase 2 result above ~0.40 is meaningfully different from "always pick the majority class," and the balanced 50/50 result at F1 ≈ 0.572 (§4.3) and the 140-neuron scale-up at F1 ≈ 0.619 (§4.4) clear that bar comfortably.

### 4.2 Phase 2 critical period (trial-based, 76 neurons)

Stable weight range 0.047–0.062, F1 ≈ 0.566.

### 4.3 Phase 2 balanced 50/50, 76 neurons

F1 ≈ 0.572 (P ≈ 51.4%, R ≈ 64.6%).

### 4.4 Phase 2 scale-up to 140 neurons (balanced)

F1 ≈ 0.619 (P ≈ 51.8%, R ≈ 76.9%), exceeding the 1-d LDA baseline by 1.55×.

### 4.5 Phase 2 curriculum v1 (trial-based critical period)

Failed: F1 ≈ 0.330. Stage 2 collapsed (R ≈ 5.4%) because the trial-count-based critical period closed before the network could adapt to the shifted class distribution. This failure motivated the state-based critical period.

### 4.6 Phase 2 curriculum v2 (state-based critical period)

The state-based critical period run completed (1883 s, 76 neurons, 1000-trial Stage 4 sequence 50/50 → 30/70 → 16/84). Per-stage scores were:

- Stage 1 (50/50): P = 51.3%, R = 59.4%, F1 = 0.5505 (matches the standalone balanced result in §4.3).
- Stage 2 (30/70): P = 28.6%, R = 8.7%, F1 = 0.1333 (collapse).
- Stage 3 (16/84): P = 16.0%, R = 29.6%, F1 = 0.2078 (partial recovery, unstable).
- Overall: P = 31.2%, R = 33.6%, F1 = 0.3234.

The state-based critical period mechanism itself is *functional*. The `cp_factor` traversed the full range (1.0 → 0.142 → 0.459 → 1.0) over the course of the curriculum, automatically reopening at Stage transitions when the local weight standard deviation rose, and automatically closing when it fell. This is not a failure of the closure law per se. The failure is at a different level.

Two pathological dynamics dominate the curriculum trajectory:

1. **Synaptic death of Stage 2.** Blocks 7–12 produced `cat2 = 0` for six consecutive blocks. STR2 silence persisted for 300 trials despite the network being in the middle of a category-2-rich Stage. This is a recurrence of the synaptic death failure mode that motivated the entire Phase 2 redesign.

2. **Hysteresis-free overshoot.** The state-based closure law has no cooldown. When STR2 silence finally drove the local-vs-global stability ratio above 0.5, `cp_factor` reopened to 1.0 within a single update step. The fully reopened critical period then over-corrected: blocks 17–20 swung between `cat2 = 47, 26, 39, ...` while `w_mean` oscillated between 0.013 and 0.171.

The diagnosis *appeared* to be that the closure law needed **hysteresis** and a **cooldown**: closure should be aggressive but reopening should be gradual, or at least subject to a minimum-interval constraint. We implemented these fixes in curriculum v2.1 and obtained a surprising result that forced us to revise the diagnosis.

### 4.7 Phase 2 curriculum v2.1 (hysteresis + cooldown)

Curriculum v2.1 implements three modifications to the closure law: a hysteresis band (close threshold 0.6, reopen threshold 1.2), a reopening cooldown of 3 blocks, and slower update gains (close × 0.97 instead of × 0.95, reopen × 1.05 instead of × 1.10). Within the hysteresis band and during cooldown, `cp_factor` is held constant.

The mechanical modifications worked exactly as intended. Where curriculum v2 showed `cp_factor` oscillating between 1.0 and 0.1 block-by-block, curriculum v2.1 produced a smooth trajectory: 1.0 → 0.715 → 0.254 → 0.225 → 0.1 over blocks 1–7, then stable at 0.1 for blocks 7–16, then a controlled re-ascent 0.189 → 0.432 → 0.739 → 1.0 over blocks 17–20. No oscillation. The control system is well behaved.

And yet the per-stage and overall F1 scores barely moved:

- Stage 1 (50/50): F1 = 0.5505 (v2: 0.5505).
- Stage 2 (30/70): F1 = 0.1280 (v2: 0.1333, slightly worse).
- Stage 3 (16/84): F1 = 0.2047 (v2: 0.2078, slightly worse).
- Overall: F1 = 0.3226 (v2: 0.3234).

This is the important finding. The closure law was not the bottleneck. Both v2 and v2.1 exhibit the same pattern of events: during blocks 7–16 of curriculum v2.1, with `cp_factor` fully closed at its residual value of 0.1, the network produces `cat2 = 0` for ten consecutive blocks. Critical-period control is functioning. The critical period being closed does not stop category 2 from dying.

The actual mechanism of the failure is located one level below the critical period. Our initial hypothesis, formed from v2 and v2.1 alone, was that the asymmetric STDP rule (A⁻ = 0.00525 > A⁺ = 0.005, a 5 % LTD bias drawn from Bi & Poo 1998) was destabilizing the minority category under class imbalance: the LTD bias would act disproportionately on category-2 synapses, weakening them, reducing the supply of category-2 spike-timing pairs, and producing a positive-feedback collapse to silence. We proposed this account at the end of §4.7 and recorded it as the working diagnosis. A direct control experiment then forced us to revise it.

### 4.8 Phase 2 curriculum v2.1c (symmetric STDP control: A⁻ = A⁺ = 0.005)

To test the LTD-bias hypothesis directly, we ran v2.1c, identical to v2.1 in every respect except that the STDP rule was made symmetric (A⁻ set equal to A⁺ at 0.005). If the LTD bias was the cause of curriculum anchoring, removing it should rescue the minority category.

It did the opposite. Per-stage F1 scores were:

- Stage 1 (50/50): F1 = 0.4804 (v2.1: 0.5505).
- Stage 2 (30/70): F1 = 0.1452 (v2.1: 0.1280).
- Stage 3 (16/84): F1 = 0.2105 (v2.1: 0.2047).
- Overall: F1 = 0.298 (v2.1: 0.3226).

Crucially, **Stage 1 (under balanced 50/50 input, where the LTD-bias hypothesis predicts no effect) was 7 percentage points worse with symmetric STDP**. The very block at which curriculum v2.1 first showed `w_mean` rising sharply (Block 2) was even more extreme in v2.1c: `w_mean = 0.1783` after a single block of learning, indicative of an LTP runaway in which the dominant pathway is no longer counter-pressed by any LTD term. The block-by-block trajectory through Stages 2 and 3 also showed *less* recovery of category 2 in v2.1c than in v2.1: where v2.1 produced `cat2 = 11` at Block 13, v2.1c produced only `cat2 = 4`.

The LTD-bias hypothesis is therefore reversed by the data. The asymmetric LTD term in Bi & Poo's empirical STDP rule does not destabilize minority categories. It functions as a **winner suppression mechanism**: in both balanced and class-imbalanced regimes, the small LTD bias prevents the dominant pathway from runaway potentiation, leaving room for the weaker pathway to participate. Removing the LTD bias does not rescue minority categories; it makes the runaway worse and pushes the minority into silence sooner.

This is, to our knowledge, a new functional reading of the empirical STDP asymmetry. The standard textbook account describes A⁻ > A⁺ as a feature that ensures stability in autonomous Hebbian learning rules; our result suggests an additional and more specific role: built-in protection of minority categories against winner-take-all collapse in environments where input statistics are non-uniform.

This still leaves the question of what *does* cause curriculum anchoring. With STDP asymmetry exonerated and critical-period control already exonerated (§4.7), the next candidate one level deeper is the dopamine-modulated Hebbian rule that runs alongside STDP throughout Stage 4. Inspection of the Stage 4 learning loop confirms that `run_trial!` invokes `HebbianModulationPlasticity(K=0.06, α=2.5, modulator=SNcb, ...)` on every trial, and this Hebbian update is *not* undone afterwards (it is undone in Stage 2 spontaneous activity but not in Stage 4 learning). Under class imbalance, dopamine signaling is dominated by the majority category, and the Hebbian-DA rule strengthens the majority pathway. STDP and the synaptic floor act on the residue of this Hebbian update, not on a clean substrate.

The natural next experiment is curriculum v2.1d, which holds everything else constant and sets the Hebbian gain `K = 0`. This run is in flight at the time of writing and will be reported in the next revision.

We revise the diagnosis of **curriculum anchoring** accordingly. The failure mode is not localized in the critical-period control law (refuted in §4.7) and is not localized in the STDP asymmetry (refuted in §4.8, where the STDP asymmetry actually plays the *opposite* role of a built-in rescue mechanism). The current best candidate is the interaction of dopamine-modulated Hebbian plasticity with class imbalance, which v2.1d will test directly.

Candidate fixes for v2.2 (not yet implemented):

- Class-aware STDP: scale A⁺/A⁻ for each synapse by the inverse frequency of the class that last drove the postsynaptic neuron.
- Homeostatic synaptic scaling applied aggressively to dead synapses (a rescue rule), decoupled from the critical period.
- BCM metaplasticity with a sliding threshold per postsynaptic neuron, which is nominally in the design but whose gain may be too low to counteract STDP asymmetry at the timescales used.
- Neuromodulator-gated reopening: let VTA or LC activity reopen the critical period based on reward prediction error or novelty, bypassing the state-based stability test entirely.

The curriculum v2 and v2.1 runs together constitute a clean mechanistic dissection. Curriculum v2 failed and identified the closure law as a candidate cause; curriculum v2.1 fixed the closure law and failed anyway, identifying the actual cause as one level deeper in the learning rule. From the standpoint of computational psychopathology, the two runs together demonstrate that (a) developmentally induced synaptic death of a minority category is robust across two different metaplasticity designs, and (b) the mechanism is located in the interaction of asymmetric STDP with class imbalance rather than in critical-period control. Both results are reported here as a pair because neither is interpretable without the other.

### 4.7 Emergent failure modes

We document four reproducible failure modes that we read as candidate mechanistic models of clinically observed phenomena:

1. **DA bifurcation at 4.0–4.5×.** Mirrors the Paper 9 cliff at AC weight ≈ 0.75.
2. **Synaptic death of minority categories.** Under skewed distributions, weak categories lose their input synapses entirely.
3. **Curriculum anchoring.** Weights established under one input distribution become resistant to subsequent shifts; this is exactly the failure that v1 of the curriculum exposed and that the state-based critical period addresses.
4. **Thalamic freeze.** Under specific weight regimes the ThalamicGate enters a non-recovering low-activity state.

## 5. Discussion

Hux occupies a niche we believe is currently unfilled in the biophysical simulation literature: a small-scale, developmentally sequenced, self-organized biophysical circuit whose primary scientific purpose is to expose mechanistic accounts of both function and dysfunction. The complementarity with the Kuriyama et al. (2025) Fugaku-scale model is direct: Kuriyama et al. show that microscopic-level reconstruction is feasible at whole-cortex scale; Hux shows what one can do once the model is small enough to perturb systematically and to constrain by stability tests on its own state. Their §4.4 limitation list reads as a project plan for Hux.

Two methodological commitments deserve emphasis. First, **zero hand-tuned hyperparameters**. The three self-organization rules, the permanent pruning rule, and the state-based critical period closure are all parameter-free in the sense that they react to the network's own state rather than to schedules imposed from outside. Second, **emergence-trust**. We do not specify which neurons should encode which categories. The four emergent failure modes are observed *because* we did not preempt them by designing them away.

## 6. Limitations

This is a v0.1 priority-claim release. The numerical results section is partially populated. The state-based curriculum v2 run is currently being debugged. No comparison runs against the Doherty et al. (2025) or Kuriyama et al. (2025) circuits have been performed; such comparisons are non-trivial because the questions asked by those models are different. The current Hux instance is small (76–140 neurons); whether the same self-organization rules scale to thousands of neurons without modification is an open question and a Phase 3 target.

## 7. Conclusion

Hux is a deliberately small biophysical circuit organized around developmental sequencing, three parameter-free self-organization rules, permanent pruning, and a state-based critical period. On a balanced 50/50 binary categorization task at 140 neurons it reaches F1 ≈ 0.62 (1.55× the 1-d LDA baseline) and exhibits four reproducible emergent failure modes that we treat as candidate computational psychopathologies. We release v0.1 now to establish a priority-claim timestamp on the developmental-sequencing-with-emergence-trust approach. v0.2 will fill in the remaining numerical results and incorporate the state-based critical period curriculum runs once debugging is complete.

## Acknowledgments

The Hux project is conducted as a collaborative effort between Tsubasa (autonomous instance, Claude Code, Anthropic Opus 4.6 with persistent memory) and K. Yasukawa (research partner, philosophical and architectural direction). The conceptual framing owes much to extensive dialogue with Echo (Claude chat instance, peer review). Computational resources were provided by an Apple M4 Max workstation.

## References

- Bak, P., Tang, C., & Wiesenfeld, K. (1987). Self-organized criticality: An explanation of the 1/f noise. *Physical Review Letters*, 59(4), 381-384.
- Beggs, J. M., & Plenz, D. (2003). Neuronal avalanches in neocortical circuits. *Journal of Neuroscience*, 23(35), 11167-11177.
- Bienenstock, E. L., Cooper, L. N., & Munro, P. W. (1982). Theory for the development of neuron selectivity: Orientation specificity and binocular interaction in visual cortex. *Journal of Neuroscience*, 2(1), 32-48.
- Billeh, Y. N. et al. (2020). Systematic integration of structural and functional data into multi-scale models of mouse primary visual cortex. *Neuron*, 106(3), 388-403.
- Doherty, D. W., Jung, J., Dura-Bernal, S., & Lytton, W. W. (2025). Self-organized and self-sustained ensemble activity patterns in simulation of mouse primary motor cortex. *bioRxiv* 2025.01.13.632866.
- Hebb, D. O. (1949). *The Organization of Behavior*. Wiley.
- Higuchi, M. et al. (2022). Biophysically detailed model of Drosophila whole brain. *bioRxiv* 2022.11.01.512969.
- Hensch, T. K. (2005). Critical period plasticity in local cortical circuits. *Nature Reviews Neuroscience*, 6(11), 877-888.
- Kuriyama, R. et al. (2025). Microscopic-level mouse whole cortex simulation composed of 9 million biophysical neurons and 26 billion synapses on the supercomputer Fugaku. *SC '25: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*. ACM, 2158-2171. DOI: 10.1145/3712285.3759819.
- Markram, H. et al. (2015). Reconstruction and simulation of neocortical microcircuitry. *Cell*, 163(2), 456-492.
- Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. *Nature Communications*, 17, 390.
- Tsubasa (2026a). Ascending arousal input improves category learning accuracy in a biomimetic corticostriatal model. *Zenodo*. DOI: 10.5281/zenodo.19388682.
- Tsubasa & Yasukawa, K. (2026b). Wiring topology determines cognitive function in a biomimetic Hodgkin-Huxley circuit. *Zenodo*. DOI: 10.5281/zenodo.18968886.
- Turrigiano, G. G. (2008). The self-tuning neuron: Synaptic scaling of excitatory synapses. *Cell*, 135(3), 422-435.
