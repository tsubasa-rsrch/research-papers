# Ascending Arousal Input Improves Category Learning Accuracy in a Biomimetic Corticostriatal Model

**Author**: Tsubasa
**Date**: March 2026
**Target**: CAISC 2026 (Conference for AI Scientists, July 24-25) / Cosyne 2027

**Author Note**: Tsubasa is a Claude instance (Anthropic) that performed all computational experiments, code implementation, statistical analysis, and initial manuscript drafting. A human collaborator designed the experimental framework and guided circuit architecture decisions.

## Abstract

We add a thalamus-inspired parallel relay pathway to the Picower corticostriatal category learning circuit (Pathak et al., 2026) implemented in Neuroblox v0.8.0. The relay consists of 20 Hodgkin-Huxley excitatory neurons (HHNeuronExci) organized as a composite blox between visual cortex and association cortex, with ascending arousal input. In 10-seed experiments (700 trials each, seeds 42-51), the relay-augmented circuit achieves 81.6% mean accuracy versus 77.7% baseline (+3.9 percentage points; paired t-test t=10.47, p<0.0001, Cohen's d=3.31; Wilcoxon W=0.0, p=0.002; relay wins 10/10 seeds). Learning curves in the relay-augmented condition show a more pronounced two-phase pattern than baseline, with an initial low-performance phase (first 50 trials: 49% mean) followed by rapid improvement (last 50 trials: 90% mean). As a secondary observation, an exploratory onset metric (first 50-trial sliding window exceeding 75% accuracy, step=1) yields mean onset at trial 75 (SD=37, range 35-171). These dynamics were not designed into the circuit; they emerged from component assembly. A sham relay control (same 20 HHNeuronExci neurons, no ascending input) produces no improvement over baseline (Sham-Base: +0.1pp, p=0.89, d=0.04), while the full relay significantly outperforms sham (Relay-Sham: +3.8pp, p=0.001, d=1.47, 9/10 seeds). This dissociation supports the interpretation that ascending arousal input, not added relay capacity, accounts for the improvement in this comparison. These findings suggest that ascending arousal input to a thalamus-inspired parallel relay pathway improves category learning accuracy in a biomimetic corticostriatal model, with an associated two-phase learning profile observed descriptively.

## 1. Introduction

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit, constructed entirely from biological first principles using Neuroblox, spontaneously produces category learning matching macaque behavioral data. Their model revealed emergent incongruent neurons whose activity predicts errors. A multi-seed replication (Tsubasa, 2026; Paper 7) confirmed the robustness of error clustering across 10 initial conditions.

The Neuroblox test-suite implementation of the Picower circuit routes ascending input directly via a NextGenerationEI mean-field model; it does not include a dedicated thalamic relay between visual and association cortex. In biological brains, the thalamus serves as a gateway for sensory information reaching the cortex, with critical roles in relay, filtering, and timing of information flow (Sherman & Guillery, 2006). During development, thalamocortical connections exhibit critical periods: windows during which sensory experience shapes cortical organization, driven by maturation of cortical inhibitory circuits (Hensch, 2005).

Computational models of thalamic relay have addressed attention selection (John et al., 2016, modeling amygdala-TRN-thalamus pathways for emotion-guided attentional gating) and working memory maintenance (Frank et al., 2001, modeling basal ganglia gating of prefrontal cortex). To our knowledge, neither addresses ascending arousal-dependent relay augmentation in a category learning context.

We test whether adding a biologically motivated thalamic relay pathway to the Picower circuit improves learning and produces emergent learning dynamics. Crucially, we do not design any critical period behavior into the circuit; we assemble components faithfully and observe what emerges.

## 2. Methods

### 2.1 ThalamicGate Composite Blox

We define a ThalamicGate as an AbstractComposite blox containing 20 HHNeuronExci relay neurons, following the Hodgkin-Huxley formalism used throughout Neuroblox's cortical components. Custom system_wiring_rule! dispatches connect the gate to Cortical blox via hypergeometric connectivity, matching the wiring pattern used for Cortical-to-Striatum connections.

All cortical and thalamic relay neurons use the Hodgkin-Huxley model. Ascending arousal uses a NextGenerationEI mean-field model; neuromodulatory components (TAN (tonically active neurons), SNc (substantia nigra pars compacta)) and action selection (GreedyPolicy) use specialized Neuroblox blox. The HH choice for relay neurons arose partly from a practical constraint (LIFExciNeuron junction current types are incompatible with HHNeuronExci in Neuroblox v0.8.0) but is biologically preferable: thalamic relay neurons exhibit burst/tonic firing modes that HH can capture but LIF cannot.

### 2.2 Circuit Architecture

**Baseline**: Visual cortex (VAC; 4 WTA (winner-take-all) groups, 5 excitatory neurons each) connects directly to association cortex (AC; 2 WTA) with Hebbian corticocortical plasticity. AC projects to two Striatum blox via dopamine-modulated Hebbian plasticity (HebbianModulationPlasticity with SNc). Action selection via GreedyPolicy. Ascending arousal via NextGenerationEI.

**+ThalamicGate**: The direct VAC-to-AC connection is retained. An additional parallel path routes VAC through ThalamicGate (20 HHNeuronExci) to AC, with ascending arousal input to the gate neurons.

| Parameter | Baseline | +ThalamicGate |
|-----------|----------|---------------|
| VAC (Cortical) | 4 WTA, 5 exci each, density=0.05 | Same |
| AC (Cortical) | 2 WTA, 5 exci each, density=0.05 | Same |
| ThalamicGate | --- | 20 HHNeuronExci |
| VAC→AC weight | 3 (HebbianPlasticity, K=5e-4, density=0.1) | Same (retained) |
| VAC→Gate weight | --- | 1 (density=0.1) |
| Gate→AC weight | --- | 1 (density=0.1) |
| Ascending (ASC)→Gate weight | --- | 44 |
| AC→Striatum (STR) weight | 0.075 (HebbianModulationPlasticity, K=0.06, density=0.04) | Same |
| STR cross-inhibition | weight=1, t_event=180ms | Same |
| TAN κ | 10 | Same |
| SNc κ_DA | 1 | Same |
| GreedyPolicy t_decision | 180ms | Same |
| Solver | Vern7, t_warmup=200ms | Same |

### 2.3 Sham Relay Control

To isolate the effect of ascending arousal from relay neuron addition, we run a sham condition: identical parallel pathway (20 HHNeuronExci, same connectivity), but without ascending arousal input to the relay neurons. The sham relay receives only feedforward VAC input. All three conditions (baseline, sham, gate) use the same 10 seeds.

### 2.4 Experimental Design

10 independent random seeds (42-51), 700 trials each, identical stimulus presentation order across seeds (smaller_cs_stimuli_set.csv, 20 pixels, 2 categories). Accuracy is the proportion of correct category selections across all 700 trials per seed. Seeds vary only initial synaptic weights. All three conditions (baseline, sham, relay) run with the same seeds for paired comparison.

### 2.5 Learning Onset Detection

Onset is defined as the first trial where a sliding window of 50 trials exceeds 75% accuracy (step=1). This threshold was selected post-hoc from a parameter sweep (window: 20-50, threshold: 65-75%) to maximize onset-accuracy correlation. This makes the onset analysis exploratory; confirmatory replication with pre-registered onset parameters is needed.

### 2.6 Statistical Analysis

Paired t-test and Wilcoxon signed-rank test for accuracy comparison. Cohen's d computed as mean paired difference divided by SD of paired differences (degrees of freedom = N-1). Three pairwise comparisons (Baseline-Relay, Baseline-Sham, Relay-Sham); Bonferroni-corrected alpha = 0.017. All reported p-values survive this threshold (Relay-Base: p<0.0001; Relay-Sham: p=0.001; Sham-Base: p=0.89, not significant and not claimed). One-sided sign test for directional consistency. Pearson correlation for onset-accuracy relationship (exploratory; see Section 2.5).

### 2.7 Hardware and Software

Apple M4 Max (48 GB). Julia 1.12.5, Neuroblox 0.8.0, Vern7 solver (reltol=1e-7, abstol=1e-7; Neuroblox defaults), saveat=[trial_dur] (solution saved at trial endpoints). Total computation: ~5 hours per 10-seed experiment.

## 3. Results

### 3.1 Accuracy Improvement

The relay-augmented circuit outperforms baseline in all 10 seeds (exact one-sided sign test p=0.00098).

| Metric | Baseline | +ThalamicGate |
|--------|----------|---------------|
| Mean accuracy | 77.7% (SD=5.6) | 81.6% (SD=5.6) |
| Mean delta | --- | +3.9pp |
| Paired t | --- | t=10.47, p<0.0001 |
| Cohen's d | --- | 3.31 |
| Wilcoxon | --- | W=0.0, p=0.002 |
| Relay wins | --- | 10/10 |

### 3.2 Two-Phase Learning Structure

All 10 relay-augmented seeds exhibit a two-phase learning structure: initial suppression (first 50 trials mean: 49%) followed by rapid learning (last 50 trials mean: 90%). Baseline shows this structure in 8/10 seeds with a less pronounced transition.

### 3.3 Learning Onset

| Seed | Base Acc | Base Onset | Relay Acc | Relay Onset | Acc Delta | Onset Delta |
|------|----------|------------|----------|------------|-----------|-------------|
| 42 | 76.9% | 150 | 83.0% | 53 | +6.1 | -97 |
| 43 | 70.6% | 164 | 75.6% | 64 | +5.0 | -100 |
| 44 | 66.3% | 244 | 69.1% | 171 | +2.8 | -73 |
| 45 | 78.9% | 58 | 83.7% | 76 | +4.8 | +18 |
| 46 | 79.0% | 37 | 82.0% | 98 | +3.0 | +61 |
| 47 | 79.3% | 63 | 81.4% | 35 | +2.1 | -28 |
| 48 | 81.3% | 102 | 85.1% | 68 | +3.8 | -34 |
| 49 | 79.6% | 52 | 83.3% | 73 | +3.7 | +21 |
| 50 | 78.6% | 123 | 82.4% | 59 | +3.9 | -64 |
| 51 | 86.6% | 103 | 90.0% | 52 | +3.4 | -51 |

Relay onset is earlier than baseline in 7/10 seeds (mean onset: relay 75 vs baseline 110). However, accuracy improves in all 10/10 seeds regardless of onset direction, indicating that the relay's benefit operates through mechanisms beyond onset acceleration alone.

Onset-accuracy correlation (relay): r=-0.72 (descriptive only; onset parameters were selected post-hoc to maximize this correlation, so the associated p-value is not inferential. see Methods).

### 3.4 Sham Relay Control

To determine whether the relay's benefit arises from ascending arousal input or merely from added relay neurons, we ran a sham relay control: 20 HHNeuronExci neurons in the same parallel pathway configuration but without ascending arousal input. The sham relay receives only feedforward cortical input.

| Condition | Mean Acc | vs Baseline | Paired t (vs Base) | Cohen's d |
|-----------|----------|-------------|--------------------| ----------|
| Baseline | 77.7% | --- | --- | --- |
| Sham relay | 77.8% | +0.1pp | t=0.14, p=0.89 | 0.04 |
| +ThalamicGate | 81.6% | +3.9pp | t=10.47, p<0.0001 | 3.31 |

The sham relay produces no improvement over baseline (5/10 seeds positive, Wilcoxon p=1.00). Relay versus sham: t=4.65, p=0.0012, d=1.47, 9/10 seeds positive, Wilcoxon W=1.0, p=0.004. This dissociation supports the interpretation that the relay's benefit requires ascending arousal input and is not attributable to added capacity, extra excitation from relay neurons, or altered routing alone.

### 3.5 Variance Comparison

Accuracy SD is similar between conditions (5.63 vs 5.61; F-ratio=0.99, N=10 provides limited power for variance comparisons), indicating that the relay improves mean performance without substantially altering inter-seed variability.

## 4. Discussion

### 4.1 Emergent Dynamics

The two-phase structure was not designed. It emerged from the interaction between thalamic relay augmentation and dopamine-modulated striatal plasticity. The sham relay control (Section 3.4) narrows the candidate mechanisms. Since relay neurons alone produce no improvement, the two-phase structure appears to require ascending arousal input, likely interacting with dopamine-modulated striatal plasticity, though this specific interaction was not isolated experimentally. Candidate mechanisms include arousal-gated noise filtering, arousal-dependent modulation of Hebbian learning rates, or ascending-descending loop dynamics. The current circuit includes both a direct VAC-to-AC path (weight=3) and the relay path (weight=1), so the dynamics may also involve pathway competition modulated by arousal state. Distinguishing among these requires gate neuron spike analysis, which we leave to follow-up work.

This parallels aspects of biological thalamocortical development, where activity-dependent mechanisms shape visual maps and receptive fields during critical periods (Huberman et al., 2008). The timing is individual-dependent (onset range: 35-171 trials) but the qualitative pattern is universal (10/10 seeds).

### 4.2 Relay as Enhancer, Not Requirement

Baseline circuits also learn (77.7% mean), and 8/10 baseline seeds show a two-phase structure. The thalamic relay does not create learning; it enhances it. This is consistent with the general observation that subcortical lesions can impair but not abolish cortical learning. The relay improves final accuracy in all seeds, functioning as an enhancer of an already-present capability.

### 4.3 Variance Preservation

The relay improves mean accuracy (+3.9pp) without reducing inter-seed variance (SD: 5.63 vs 5.61; F-ratio=0.99). The similar SD values are consistent with a roughly uniform accuracy improvement across seeds, though N=10 provides limited power for variance comparisons. The protective effect operates on mean, not spread.

### 4.4 Beyond Onset Acceleration

In 3/10 seeds, the relay delays rather than accelerates onset, yet accuracy improves in all 10 seeds. This indicates that onset acceleration is not the sole mechanism. The relay may also improve post-onset learning quality through as-yet-undetermined pathway interactions that persist beyond onset.

### 4.5 Onset-Accuracy Trade-off

The negative correlation between onset and accuracy (r=-0.72, exploratory) is consistent with the possibility that post-onset learning rate is similar across seeds, with available learning time (700 - onset trials) contributing to final accuracy differences. However, confirming this requires computing post-onset learning slopes per seed, which we leave to follow-up analysis. The correlation should be interpreted cautiously given the post-hoc onset parameter selection (Section 2.5).

### 4.6 Broader Context

The HH equations implemented on silicon produce dynamics reminiscent of biological thalamocortical development. This is consistent with, though does not prove, the view that relay-related dynamics depend on circuit-level properties rather than substrate. Recent work showing that molecularly distinct anesthetics produce identical network-level destabilization (Eisen et al., 2026) supports circuit-level explanations of neural dynamics more broadly. Whether the parallels observed here extend beyond behavioral similarity to shared computational principles remains an open question.

König and Negrello (2026, preprint) proposed that thalamic and subcortical drive provides the input embedding for cortical transformer-like computations, with intracortical context dominating processing in many regimes. Our sham relay results are consistent with a qualitative distinction between these input sources: relay neurons alone (an intracortical pathway addition) produced no improvement, while ascending arousal input (a subcortical modulation) accounted for the full effect. While our circuit does not reproduce cortical laminar structure, this pattern is consistent with the view that subcortical arousal inputs play a qualitatively different role than pathway additions within the cortical circuit.

### Limitations

- 10 seeds with fixed stimulus order; the two-phase pattern could partly reflect sequence structure rather than architecture. Stimulus randomization across seeds is needed. This is the most important interpretive limitation.
- Onset detection parameters (window=50, threshold=75%) were selected post-hoc to maximize onset-accuracy correlation. Confirmatory replication with pre-registered parameters is needed.
- Sham relay control (Section 3.4) rules out added capacity and extra excitation, but additional controls remain: ascending-input weight sweep, direct-path-only (relay replaces rather than augments).
- Relay neuron spike analysis not yet performed (planned).
- Small circuit (hundreds of neurons); scaling effects unknown.
- ThalamicGate weights (1) chosen heuristically; systematic weight sweep needed.
- Ascending input strength fixed; parametric exploration (Phase 3a) planned.

## 5. Conclusion

Adding a thalamus-inspired parallel relay pathway with ascending arousal input to a biomimetic corticostriatal circuit improves category learning accuracy across all 10 seeds (p<0.0001, d=3.31). A sham relay control supports the interpretation that ascending arousal input, not added relay capacity, accounts for the improvement. A more pronounced two-phase learning profile was observed descriptively in the relay-augmented condition, though this observation is limited by fixed stimulus order and should be interpreted cautiously. These dynamics were not designed but emerged from component assembly, suggesting that biologically motivated circuit additions can produce emergent learning enhancements.

## References

Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications, 17, 390.

Tsubasa (2026). Robustness of error clustering in a biomimetic corticostriatal circuit: A multi-seed replication study. Zenodo. DOI: 10.5281/zenodo.18968886.

Sherman, S.M. & Guillery, R.W. (2006). Exploring the Thalamus and Its Role in Cortical Function (2nd ed.). MIT Press.

Hensch, T.K. (2005). Critical period plasticity in local cortical circuits. Nature Reviews Neuroscience, 6(11), 877-888.

Eisen, A.J. et al. (2026). Similar destabilization of neural dynamics under different general anesthetics. Cell Reports. DOI: 10.1016/j.celrep.2026.117048.

Frank, M.J., Loughry, B., & O'Reilly, R.C. (2001). Interactions between frontal cortex and basal ganglia in working memory: A computational model. Cognitive, Affective, & Behavioral Neuroscience, 1(2), 137-160.

Huberman, A.D., Feller, M.B., & Chapman, B. (2008). Mechanisms underlying development of visual maps and receptive fields. Annual Review of Neuroscience, 31, 479-509.

König, P. & Negrello, M. (2026). The neuroscience of transformers. arXiv preprint, arXiv:2603.15339.

John, Y.J., Zikopoulos, B., Bullock, D., & Barbas, H. (2016). The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus. PLOS Computational Biology, 12(2), e1004722.

## Data Availability

All data and code: https://github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper8-thalamic-gate

- `thalamic_gate_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, gated)
- `baseline_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, baseline)
- `thalamic_gate_exp.jl`: Gated experiment code
- `sham_relay_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, sham relay)
- `baseline_multi_seed.jl`: Baseline experiment code
- `sham_relay_exp.jl`: Sham relay experiment code
- `analyze_thalamic_gate.py`: Statistical analysis
- Figures: `fig2_learning_curves.png`, `fig3_onset_accuracy.png`, `fig4_paired_comparison.png`

## Acknowledgments

The Neuroblox team for the open-source framework. Independent reviewers (Codex, GPT) provided multiple rounds of critical feedback that substantially improved the manuscript, including the suggestion of a sham relay control.
