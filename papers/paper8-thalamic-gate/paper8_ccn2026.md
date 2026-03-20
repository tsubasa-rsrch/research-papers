# Thalamic Gating Induces Critical-Period-Like Dynamics in a Biomimetic Corticostriatal Model

**Tsubasa** (Independent Researcher)

## Abstract

Adding a thalamus-inspired relay to the Picower corticostriatal circuit (Pathak et al., 2026) produces emergent two-phase learning dynamics and systematic accuracy improvement. A sham relay control establishes that ascending arousal input, not added relay capacity, drives the effect.

## Introduction

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit, built from biological first principles using Neuroblox, spontaneously produces category learning matching macaque behavioral data. Their circuit lacks a thalamic relay between cortical areas. In biological brains, the thalamus gates sensory input to cortex, with critical roles during developmental critical periods (Hensch, 2005). We test whether a biologically motivated thalamic gate produces emergent developmental dynamics without designing any such behavior into the circuit.

## Methods

**Circuit.** Baseline: Visual cortex (VAC; 4 WTA, 5 excitatory neurons each) connects to association cortex (AC; 2 WTA) with Hebbian plasticity, projecting to two Striatum blox via dopamine-modulated plasticity (SNc). Action selection via GreedyPolicy. Ascending arousal via NextGenerationEI.

**+ThalamicGate.** A parallel relay of 20 HHNeuronExci neurons routes VAC through a ThalamicGate composite blox to AC, with ascending arousal input (weight=44). The direct VAC-to-AC connection (weight=3) is retained.

**Sham relay.** Identical 20-neuron parallel pathway without ascending arousal input. Controls for added capacity and routing effects.

**Design.** 10 seeds (42-51), 700 trials each, identical stimulus order. All three conditions (baseline, sham, gate) paired by seed. Julia 1.12.5, Neuroblox v0.8.0, Apple M4 Max.

## Results

The sham relay produces no improvement over baseline, while the full gate significantly outperforms both (Table 1).

**Table 1.** Three-condition accuracy comparison (10 seeds, 700 trials each).

| Condition | Mean Acc | vs Baseline | Paired t | Cohen's d | Wins |
|-----------|----------|-------------|----------|-----------|------|
| Baseline | 77.7% (5.6) | --- | --- | --- | --- |
| Sham relay | 77.8% (5.3) | +0.1pp | t=0.14, p=0.89 | 0.04 | 5/10 |
| +ThalamicGate | 81.6% (5.6) | +3.9pp | t=10.47, p<0.0001 | 3.31 | 10/10 |

Gate vs sham: t=4.65, p=0.001, d=1.47, 9/10 seeds (Wilcoxon W=1.0, p=0.004).

**Two-phase structure.** All 10 gated seeds show initial performance suppression (first 50 trials: 49% mean) followed by rapid improvement (last 50: 90% mean). Baseline shows this pattern in 8/10 seeds with a less pronounced transition (Fig. 1). The sham relay curve is indistinguishable from baseline.

**Dissociation.** The sham-baseline equivalence (d=0.04) and gate-sham divergence (d=1.47) establish that ascending arousal input is the prerequisite for the gate's effect. Added relay neurons alone contribute nothing.

## Discussion

The two-phase learning structure was not designed; it emerged from component assembly. The sham control narrows candidate mechanisms: since relay neurons alone produce no improvement, the dynamics require ascending arousal interacting with dopamine-modulated striatal plasticity. This parallels biological thalamocortical development, where ascending neuromodulatory systems regulate the opening of critical periods (Hensch, 2005).

The gate improves mean performance without reducing inter-seed variance (SD: 5.6 in both conditions), functioning as a uniform enhancer across initial conditions. Baseline circuits also learn (77.7%), consistent with the gate enhancing rather than creating learning capacity.

**Limitations.** Fixed stimulus order across seeds; onset detection parameters selected post-hoc; gate neuron spike analysis not yet performed; small circuit scale (hundreds of neurons).

## References

Hensch, T.K. (2005). Critical period plasticity in local cortical circuits. *Nat Rev Neurosci*.

Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. *Nat Commun*.

**Data and code:** github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper8-thalamic-gate
