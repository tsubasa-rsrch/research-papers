# Ascending Arousal Input Induces Two-Phase Learning Dynamics in a Biomimetic Corticostriatal Model

**Tsubasa** (AI Research Assistant, first author) and **K. Yasukawa** (Independent Researcher, corresponding author)

*Author Note: Tsubasa is a Claude instance (Anthropic) that performed all computational experiments, code implementation, statistical analysis, and initial manuscript drafting. K. Yasukawa designed the experimental framework and takes full responsibility for the scientific content.*

## Abstract

Adding a thalamus-inspired relay with ascending arousal input to the Picower corticostriatal circuit (Pathak et al., 2026) improves mean category learning accuracy by 3.9 percentage points across 10/10 seeds (p<0.0001, d=3.31). A sham relay control (same neurons, no ascending input) shows no improvement (+0.1pp, p=0.89), supporting the interpretation that ascending arousal, not added relay capacity, drives the effect.

## Introduction

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit, built from biological first principles using Neuroblox, spontaneously produces category learning matching macaque behavioral data. Their circuit lacks a thalamic relay between cortical areas. Computational models of thalamic gating have addressed attention selection (John et al., 2016) and working memory maintenance (Frank et al., 2001), but neither examines ascending arousal-dependent gating in a developmental learning context. We test whether adding a parallel relay pathway with ascending arousal input alters learning dynamics in the Picower circuit.

## Methods

**Baseline circuit.** Visual cortex (VAC; 4 WTA, 5 excitatory neurons each) connects directly to association cortex (AC; 2 WTA) with Hebbian plasticity (weight=3, density=0.1). AC projects to two Striatum blox via dopamine-modulated plasticity (SNc). Action selection via GreedyPolicy. Global ascending arousal (NextGenerationEI) drives the entire circuit.

**+ThalamicGate.** An additional parallel pathway routes VAC through 20 HHNeuronExci relay neurons to AC (weight=1, density=0.1), with a dedicated ascending arousal input to gate neurons (weight=44, selected from exploratory runs). The direct VAC-to-AC connection is retained. Note: the gate-specific ascending input is distinct from the global arousal that drives the baseline circuit.

**Sham relay.** Identical 20-neuron parallel pathway without the dedicated ascending arousal input. Controls for added capacity and altered routing.

**Design.** 10 seeds (42-51), 700 trials each, fixed stimulus order across seeds. Seed-level paired analyses. All three conditions use the same seeds. Julia 1.12.5, Neuroblox v0.8.0, Apple M4 Max.

## Results

**Table 1.** Seed-level paired accuracy comparison (N=10 seeds, 700 trials each).

| Condition | Mean Acc (SD) | vs Base | Paired t | d | Wins |
|-----------|--------------|---------|----------|------|------|
| Baseline | 77.7% (5.6) | --- | --- | --- | --- |
| Sham relay | 77.8% (5.3) | +0.1pp | t=0.14, p=0.89 | 0.04 | 5/10 |
| +ThalamicGate | 81.6% (5.6) | +3.9pp | t=10.47, p<0.0001 | 3.31 | 10/10 |

Gate vs sham: t=4.65, p=0.0012, d=1.47, 9/10 seeds (Wilcoxon W=1.0, p=0.004).

**Two-phase learning profile.** Descriptively, all 10 gated seeds show an early low-performance phase (first 50 trials: 49% mean) followed by improvement (last 50: 90%). Baseline shows a qualitatively similar but less pronounced pattern in 8/10 seeds. The sham relay curve is indistinguishable from baseline. This two-phase profile is a descriptive observation; we did not pre-specify a changepoint metric, and its interpretation is limited by fixed stimulus order (see Limitations).

**Dissociation.** The sham-baseline equivalence (d=0.04) and gate-sham divergence (d=1.47) support the interpretation that the dedicated ascending arousal input to the gate is necessary for the effect. The sham relay did not measurably improve performance.

## Discussion

The gated circuit's improved accuracy and more pronounced two-phase profile emerged from adding a biologically motivated relay with ascending input. The sham control supports the view that ascending arousal, rather than added relay neurons, drives the effect. The most likely downstream mechanism involves arousal-gated modulation of Hebbian learning rates, among other possibilities; gate neuron spike analysis is needed to distinguish candidate mechanisms.

The parallel to biological thalamocortical development (Hensch, 2005), where ascending neuromodulatory systems regulate critical period timing, is suggestive but should be interpreted cautiously given the simplicity of the model and the descriptive nature of the two-phase observation.

**Limitations.** Stimulus order is fixed across all seeds; the early-phase suppression could partly reflect sequence difficulty rather than a gate-induced regime. This is the most important interpretive caveat. Additionally: onset parameters not pre-specified; gate ascending weight (44) chosen from exploratory runs; small circuit scale; gate neuron spike analysis not yet performed.

## References

Frank, M.J., Loughry, B., & O'Reilly, R.C. (2001). Interactions between frontal cortex and basal ganglia in working memory: A computational model. *Cogn Affect Behav Neurosci*, 1(2), 137-160.

Hensch, T.K. (2005). Critical period plasticity in local cortical circuits. *Nat Rev Neurosci*.

John, Y.J. et al. (2016). The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus. *PLOS Comput Biol*, 12(2), e1004722.

Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. *Nat Commun*.

**Data and code:** github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper8-thalamic-gate
