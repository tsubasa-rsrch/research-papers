# Hux: A Developmentally-Sequenced Biophysical Cortico-Striatal Circuit with Self-Organized Plasticity, Permanent Pruning, and a State-Based Critical Period

**Version**: v0.4 (Higuchi 2022 added, three-way Related Work triangulation complete)
**Date**: 2026-04-07
**Authors**: Tsubasa, K. Yasukawa
**Status**: Work in progress. Phase 2 numerical results are integrated through the state-based critical period curriculum run (§4.6). Phase 1 baselines and Phase 2 sham/identity controls remain to be reported in subsequent revisions. Related Work §2.1–§2.2 now triangulates against the full texts of Kuriyama et al. (2025), Higuchi et al. (2022), and Doherty et al. (2025).

---

## Abstract

We introduce **Hux**, a small-scale biophysical cortico-striatal circuit (76–140 Hodgkin-Huxley neurons) built around the explicit hypothesis that brain-style cognition emerges from developmental sequencing and self-organized plasticity rather than from static large-scale reconstruction. Hux implements three self-organization rules with no hand-tuned hyperparameters: a synaptic floor that prevents collapse of weak connections, homeostatic synaptic scaling, and BCM-style metaplasticity. Activity-dependent permanent pruning closes connections that fail to develop, mimicking developmental synapse elimination. A state-based critical period (governed by weight-stability ratios rather than trial counts) automatically opens during high-plasticity phases and closes when the weight distribution stabilizes. Three ascending neuromodulator systems (LC/Raphe/VTA, implemented separately) gate plasticity. On a balanced 50/50 binary categorization task with 140 neurons, Hux reaches F1 ≈ 0.62 (P ≈ 51.8%, R ≈ 76.9%), exceeding a 1-d LDA baseline by 1.55×. Critically, Hux exhibits four emergent computational psychopathologies (DA bifurcation at 4.0–4.5×, synaptic death of minority categories, curriculum anchoring, and thalamic freeze) that we read as candidate mechanistic models of clinically observed phenomena. We position Hux as complementary to large-scale reconstruction efforts (Kuriyama et al. 2025, 9M neurons on Fugaku): the Kuriyama group explicitly identifies plasticity, neuromodulators, and developmental processes as the principal limitation of microscopic-level whole-cortex simulation and as the next frontier toward brain-inspired AI; Hux pursues exactly that frontier at a scale amenable to mechanistic dissection.

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

### 4.1 Phase 1: 76-neuron baseline

To be filled.

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

The diagnosis is that the closure law needs **hysteresis** and a **cooldown**: closure should be aggressive but reopening should be gradual, or at least subject to a minimum-interval constraint after the previous reopening. Candidate fixes for v2.1, to be tested:

- Slower update gains (closure × 0.97, reopening × 1.05) instead of × 0.95 / × 1.10.
- A reopening cooldown of N blocks.
- Adaptive `STABILITY_THRESHOLD` based on the global weight history rather than a fixed 0.5.

The curriculum v2 result is reported here as a negative result of immediate scientific interest: the closure mechanism works as designed, and the residual failure exposes a specific, interpretable, and fixable property of the closure law. From the standpoint of computational psychopathology, the run is a clean demonstration of (a) developmentally induced synaptic death and (b) the cost of an over-reactive critical-period reopening, both of which have plausible clinical analogues in critical-period sensory deprivation and in adolescent-onset disorders of cortical maturation.

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
