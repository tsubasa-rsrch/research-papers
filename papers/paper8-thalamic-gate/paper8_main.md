# Ascending Arousal Input Improves Category Learning Accuracy in a Biomimetic Corticostriatal Model

**Author**: Tsubasa
**Date**: March 2026 (v1.1, April 2026)
**Target**: CAISC 2026 (Conference for AI Scientists, July 24-25) / Cosyne 2027

**Author Note**: Tsubasa is a Claude instance (Anthropic) that performed all computational experiments, code implementation, statistical analysis, and initial manuscript drafting. A human collaborator designed the experimental framework and guided circuit architecture decisions.

## Abstract

We add a thalamus-inspired parallel relay pathway to the Picower corticostriatal category learning circuit (Pathak et al., 2026) implemented in Neuroblox v0.8.0. The relay consists of 20 Hodgkin-Huxley excitatory neurons (HHNeuronExci) organized as a composite blox between visual cortex and association cortex, with ascending arousal input. In 10-seed experiments (700 trials each, seeds 42-51), the relay-augmented circuit achieves 81.6% mean accuracy versus 77.7% baseline (+3.9 percentage points; paired t-test t=10.47, p<0.0001, Cohen's d=3.31; Wilcoxon W=0.0, p=0.002; relay wins 10/10 seeds). Both conditions exhibit two-phase learning (initial low performance followed by improvement); piecewise linear change point analysis shows no significant difference in transition timing (relay: trial 301 SD=100, baseline: trial 270 SD=174). The relay's benefit is consistent with improved post-transition accuracy rather than earlier transition onset. A sham relay control (same 20 HHNeuronExci neurons, no ascending input) produces no improvement over baseline (Sham-Base: +0.1pp, p=0.89, d=0.04). A direct ascending control (equivalent ASC input to AC without relay neurons, weight=88) reduces accuracy below baseline (DirectASC-Base: -7.8pp, p<0.0001, d=-2.56, 0/10 seeds improved). The full relay significantly outperforms both sham (Relay-Sham: +3.8pp, p=0.001, d=1.47) and direct ascending (Relay-DirectASC: +11.7pp, p<0.000001, d=4.44). This three-way dissociation is consistent with the relay pathway performing signal transformation, not merely signal delivery. Note that the direct ASC weight (88) may not match the effective relay-to-AC drive, so this comparison should be interpreted cautiously. These findings suggest that ascending arousal input to a thalamus-inspired parallel relay pathway improves category learning accuracy in a biomimetic corticostriatal model, with an associated two-phase learning profile observed descriptively.

## 1. Introduction

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit, constructed entirely from biological first principles using Neuroblox, spontaneously produces category learning matching macaque behavioral data. Their model revealed emergent incongruent neurons whose activity predicts errors. A multi-seed replication (Tsubasa, 2026; Paper 7) confirmed the robustness of error clustering across 10 initial conditions.

The Neuroblox test-suite implementation of the Picower circuit routes ascending input directly via a NextGenerationEI mean-field model; it does not include a dedicated thalamic relay between visual and association cortex. In biological brains, the thalamus serves as a gateway for sensory information reaching the cortex, with critical roles in relay, filtering, and timing of information flow (Sherman & Guillery, 2006; Saalmann & Kastner, 2011). During development, thalamocortical connections exhibit critical periods: windows during which sensory experience shapes cortical organization, driven by maturation of cortical inhibitory circuits (Hensch, 2005).

Computational models of thalamic relay have addressed attention selection (John et al., 2016, modeling amygdala-TRN-thalamus pathways for emotion-guided attentional gating) and working memory maintenance (Frank et al., 2001, modeling basal ganglia gating of prefrontal cortex). To our knowledge, neither addresses ascending arousal-dependent relay augmentation in a category learning context.

We hypothesized that adding a biologically motivated thalamic relay pathway to the Picower circuit would improve category learning accuracy. We test this hypothesis and characterize the resulting learning dynamics. Crucially, we do not design any specific learning dynamics into the circuit; we assemble components faithfully and observe what emerges.

## 2. Methods

### 2.1 ThalamicGate Composite Blox

We define a ThalamicGate (the Neuroblox component name; referred to as "relay" throughout this paper) as an AbstractComposite blox containing 20 HHNeuronExci relay neurons, following the Hodgkin-Huxley formalism used throughout Neuroblox's cortical components. Custom system_wiring_rule! dispatches connect the relay to Cortical blox via hypergeometric connectivity, matching the wiring pattern used for Cortical-to-Striatum connections.

All cortical and thalamic relay neurons use the Hodgkin-Huxley model. Ascending arousal uses a NextGenerationEI mean-field model; neuromodulatory components (TAN (tonically active neurons), SNc (substantia nigra pars compacta)) and action selection (GreedyPolicy) use specialized Neuroblox blox. The HH choice for relay neurons arose partly from a practical constraint (LIFExciNeuron junction current types are incompatible with HHNeuronExci in Neuroblox v0.8.0) but is biologically preferable: thalamic relay neurons exhibit burst/tonic firing modes that HH can capture but LIF cannot.

### 2.2 Circuit Architecture

**Baseline**: Visual cortex (VAC; 4 WTA (winner-take-all) groups, 5 excitatory neurons each) connects directly to association cortex (AC; 2 WTA) with Hebbian corticocortical plasticity. AC projects to two Striatum blox via dopamine-modulated Hebbian plasticity (HebbianModulationPlasticity with SNc). Action selection via GreedyPolicy. Ascending arousal via NextGenerationEI.

**+ThalamicGate**: The direct VAC-to-AC connection is retained. An additional parallel path routes VAC through ThalamicGate (20 HHNeuronExci) to AC, with ascending arousal input to the relay neurons.

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

To isolate the effect of ascending arousal from relay neuron addition, we run a sham condition: identical parallel pathway (20 HHNeuronExci, same connectivity), but without ascending arousal input to the relay neurons. The sham relay receives only feedforward VAC input. All three conditions (baseline, sham, relay) use the same 10 seeds.

### 2.4 Experimental Design

10 independent random seeds (42-51), 700 trials each, identical stimulus presentation order across seeds (smaller_cs_stimuli_set.csv, 20 pixels, 2 categories). Accuracy is the proportion of correct category selections across all 700 trials per seed. Seeds vary only initial synaptic weights. All three conditions (baseline, sham, relay) run with the same seeds for paired comparison.

### 2.5 Learning Onset Detection

Onset is defined as the first trial where a sliding window of 50 trials exceeds 75% accuracy (step=1). This threshold was selected post-hoc from a parameter sweep (window: 20-50, threshold: 65-75%) to maximize onset-accuracy correlation. This makes the onset analysis exploratory; confirmatory replication with pre-registered onset parameters is needed.

### 2.6 Statistical Analysis

Paired t-test and Wilcoxon signed-rank test for accuracy comparison. Cohen's d computed as mean paired difference divided by SD of paired differences (degrees of freedom = N-1). Five pairwise comparisons (Baseline-Relay, Baseline-Sham, Relay-Sham, Baseline-DirectASC, Relay-DirectASC); Bonferroni-corrected alpha = 0.01. All significant p-values survive this threshold (Relay-Base: p<0.0001; Relay-Sham: p=0.001; DirectASC-Base: p<0.0001; Relay-DirectASC: p<0.000001; Sham-Base: p=0.89, not significant and not claimed). One-sided sign test for directional consistency (pre-specified hypothesis: relay improves accuracy). Wilcoxon W is the smaller of the positive and negative rank sums. Pearson correlation for onset-accuracy relationship (exploratory; see Section 2.5).

### 2.7 Hardware and Software

Apple M4 Max (48 GB). Julia 1.12.5, Neuroblox 0.8.0, Vern7 solver (reltol=1e-7, abstol=1e-7; Neuroblox defaults), saveat=[trial_dur] (solution saved at trial endpoints). Total computation: ~5 hours per 10-seed experiment.

## 3. Results

### 3.1 Accuracy Improvement

The relay-augmented circuit outperforms baseline in all 10 seeds (exact one-sided sign test p=0.00098).

| Metric | Baseline | +ThalamicGate |
|--------|----------|---------------|
| Mean accuracy | 77.7% (SD=5.6) | 81.6% (SD=5.6) |
| Mean delta (95% CI) | --- | +3.9pp [3.06, 4.74] |
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

The exploratory 75%-threshold onset metric yields mean onset at trial 75 (relay) vs 110 (baseline), with relay earlier in 7/10 seeds. However, this metric is threshold-dependent (window=50, threshold=75%, selected post-hoc; see Section 2.5).

To assess transition timing independently of threshold choice, we performed piecewise linear change point analysis on smoothed learning curves (window=50). Breakpoint location: relay mean 270 (SD=113), baseline mean 295 (SD=174); paired t-test: t(9)=-0.37, p=0.72, d=-0.12, not significant. This is consistent with the relay's benefit arising from improved post-transition accuracy rather than earlier learning transition. The onset-accuracy correlation (r=-0.72) reported under the threshold-based metric does not generalize to model-based change point detection.

### 3.4 Sham Relay Control

To determine whether the relay's benefit arises from ascending arousal input or merely from added relay neurons, we ran a sham relay control: 20 HHNeuronExci neurons in the same parallel pathway configuration but without ascending arousal input. The sham relay receives only feedforward cortical input.

| Condition | Mean Acc | vs Baseline | Paired t (vs Base) | Cohen's d |
|-----------|----------|-------------|--------------------| ----------|
| Baseline | 77.7% | --- | --- | --- |
| Sham relay | 77.8% | +0.1pp | t=0.14, p=0.89 | 0.04 |
| +ThalamicGate | 81.6% | +3.9pp | t=10.47, p<0.0001 | 3.31 |

The sham relay produces no improvement over baseline (5/10 seeds positive, Wilcoxon p=1.00). Relay versus sham: t=4.65, p=0.0012, d=1.47, 9/10 seeds positive, Wilcoxon W=1.0, p=0.004. This dissociation supports the interpretation that the relay's benefit requires ascending arousal input and is not consistent with added capacity, extra excitation from relay neurons, or altered routing alone.

### 3.5 Direct Ascending Control

To determine whether the relay's benefit arises from ascending arousal input per se or from relay-mediated signal transformation, we added equivalent ascending input directly to AC (ASC→AC weight=88, matching the combined baseline ASC→AC weight of 44 plus the relay pathway's ASC→Gate weight of 44) without relay neurons.

| Condition | Mean Acc (SD) | vs Baseline | Cohen's d | Wins |
|-----------|---------------|-------------|-----------|------|
| Direct ASC | 69.9% (6.0) | -7.8pp | -2.56 | 0/10 |

Direct ascending input reduced accuracy below baseline in all 10 seeds (paired t=-8.08, p<0.0001, d=-2.56). This indicates that unmediated ascending drive disrupts rather than improves learning, consistent with cortical overexcitation disrupting WTA competition. The three-way dissociation (sham: no effect; direct ASC: harmful; relay+ASC: beneficial) is consistent with a relay-mediated transformation account, though the direct ASC weight (88) may not match the effective relay-to-AC drive; lower-weight direct ASC conditions would further refine this comparison.

### 3.6 Variance Comparison

Accuracy SD is similar between conditions (5.63 vs 5.61; F-ratio=0.99, N=10 provides limited power for variance comparisons), indicating that the relay improves mean performance without substantially altering inter-seed variability.

### 3.7 Stimulus Shuffle Control

To determine whether the two-phase learning pattern reflects stimulus order rather than circuit architecture, we ran the relay-augmented condition with shuffled stimulus presentation order (independent permutation per seed, seeds 42-51).

| Metric | Original (fixed order) | Shuffled |
|--------|----------------------|----------|
| Mean accuracy | 81.6% (SD=5.6) | 83.5% (SD=6.1) |
| First 50 trials | 49% | 53.8% |
| Last 50 trials | 90% | 91.0% |
| Two-phase pattern | 10/10 seeds | 10/10 seeds |

Shuffled relay accuracy (83.5%, SD=6.1) was not significantly different from fixed-order relay accuracy (81.6%, SD=5.6; paired t-test across seeds 42-51: t=0.73, p=0.48). The two-phase learning profile persists under shuffled stimulus order, suggesting it is not an artifact of fixed presentation sequence. Note that this shuffle control was applied only to the relay condition; a shuffled baseline remains untested.

## 4. Discussion

### 4.1 Emergent Dynamics

The two-phase structure was not designed. It emerged from the interaction between thalamic relay augmentation and dopamine-modulated striatal plasticity. The sham relay control (Section 3.4) narrows the candidate mechanisms. Since relay neurons alone produce no improvement, ascending arousal input is associated with the two-phase structure in this circuit, likely interacting with dopamine-modulated striatal plasticity, though this specific interaction was not isolated experimentally. Candidate mechanisms include arousal-modulated noise filtering, arousal-dependent modulation of Hebbian learning rates, or ascending-descending loop dynamics. The current circuit includes both a direct VAC-to-AC path (weight=3) and the relay path (weight=1), so the dynamics may also involve pathway competition modulated by arousal state. Distinguishing among these requires relay neuron spike analysis, which we leave to follow-up work.

This parallels aspects of biological thalamocortical development, where activity-dependent mechanisms shape visual maps and receptive fields during critical periods (Huberman et al., 2008). The timing is individual-dependent (onset range: 35-171 trials) but the qualitative pattern is universal (10/10 seeds).

### 4.2 Relay as Enhancer, Not Requirement

Baseline circuits also learn (77.7% mean), and 8/10 baseline seeds show a two-phase structure. The thalamic relay does not create learning; it enhances it. This is consistent with the general observation that subcortical lesions can impair but not abolish cortical learning. The relay improves final accuracy in all seeds, functioning as an enhancer of an already-present capability.

### 4.3 Variance Preservation

The relay improves mean accuracy (+3.9pp) without reducing inter-seed variance (SD: 5.63 vs 5.61; F-ratio=0.99, p-value not computed due to limited power at N=10). The similar SD values are consistent with a roughly uniform accuracy improvement across seeds. The protective effect operates on mean, not spread.

### 4.4 Post-Transition Improvement, Not Onset Acceleration

Piecewise linear change point analysis shows no significant difference in transition timing between relay and baseline conditions (relay: trial 270, SD=113; baseline: trial 295, SD=174; paired t(9)=-0.37, p=0.72, d=-0.12). The relay's benefit operates through improved post-transition accuracy rather than earlier onset. This is consistent with the relay providing sustained computational support throughout learning, rather than triggering an earlier transition. The threshold-based onset metric (r=-0.72 onset-accuracy correlation) does not generalize to model-based breakpoint detection, and should be regarded as an artifact of the specific threshold choice.

### 4.5 Broader Context

The HH equations implemented on silicon produce learning dynamics with two-phase structure reminiscent of biological thalamocortical development. This is consistent with, though does not prove, the view that relay-related dynamics depend on circuit-level properties rather than substrate.

König and Negrello (2026, preprint) proposed that thalamic and subcortical drive provides the input embedding for cortical transformer-like computations, with intracortical context dominating processing in many regimes. Our sham relay results are consistent with a qualitative distinction between these input sources: relay neurons alone (an intracortical pathway addition) produced no improvement, while ascending arousal input (a subcortical modulation) accounted for the full effect. While our circuit does not reproduce cortical laminar structure, this pattern is consistent with the view that subcortical arousal inputs play a qualitatively different role than pathway additions within the cortical circuit.

### Limitations

- Stimulus shuffle control (Section 3.7) tested the relay condition only; a shuffled baseline remains untested.
- Onset detection parameters (window=50, threshold=75%) were selected post-hoc to maximize onset-accuracy correlation. Confirmatory replication with pre-registered parameters is needed.
- Sham relay control (Section 3.4) rules out added capacity; direct ascending control (Section 3.5) is consistent with relay-mediated transformation rather than extra modulatory drive alone. Remaining controls: ascending-input weight sweep, direct-path-only (relay replaces rather than augments). The direct ASC weight (88) may overestimate the effective relay-to-AC drive; lower-weight direct ASC conditions would further refine this comparison.
- Relay neuron spike analysis not yet performed (planned).
- Change point analysis (Section 3.3) indicates onset timing is not accelerated by the relay; the mechanism operates through post-transition improvement.
- Small circuit (hundreds of neurons); scaling effects unknown.
- ThalamicGate weights (1) chosen heuristically; systematic weight sweep needed.
- Ascending input strength fixed; parametric exploration (Phase 3a) planned.

## 5. Conclusion

Adding a thalamus-inspired parallel relay pathway with ascending arousal input to a biomimetic corticostriatal circuit improves category learning accuracy across all 10 seeds (p<0.0001, d=3.31). A sham relay control rules out added relay capacity, and a direct ascending control confirms that unmediated ascending drive disrupts learning (d=-2.56), consistent with relay-mediated signal transformation. A more pronounced two-phase learning profile was observed descriptively in the relay-augmented condition; stimulus order was tested for the relay condition (Section 3.7), though a shuffled baseline remains untested. These dynamics were not designed but emerged from component assembly, suggesting that biologically motivated circuit additions can produce emergent learning enhancements.

## References

Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications, 17, 390.

Tsubasa (2026). Robustness of error clustering in a biomimetic corticostriatal circuit: A multi-seed replication study. Zenodo. DOI: 10.5281/zenodo.18968886.

Saalmann, Y.B. & Kastner, S. (2011). Cognitive and perceptual functions of the visual thalamus. Neuron, 71(2), 209-223.

Sherman, S.M. & Guillery, R.W. (2006). Exploring the Thalamus and Its Role in Cortical Function (2nd ed.). MIT Press.

Hensch, T.K. (2005). Critical period plasticity in local cortical circuits. Nature Reviews Neuroscience, 6(11), 877-888.


Frank, M.J., Loughry, B., & O'Reilly, R.C. (2001). Interactions between frontal cortex and basal ganglia in working memory: A computational model. Cognitive, Affective, & Behavioral Neuroscience, 1(2), 137-160.

Huberman, A.D., Feller, M.B., & Chapman, B. (2008). Mechanisms underlying development of visual maps and receptive fields. Annual Review of Neuroscience, 31, 479-509.

König, P. & Negrello, M. (2026). The neuroscience of transformers. arXiv preprint, arXiv:2603.15339.

John, Y.J., Zikopoulos, B., Bullock, D., & Barbas, H. (2016). The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus. PLOS Computational Biology, 12(2), e1004722.

## Data Availability

All data and code: https://github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper8-thalamic-gate

- `thalamic_gate_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, relay-augmented)
- `baseline_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, baseline)
- `thalamic_gate_exp.jl`: Relay-augmented experiment code
- `sham_relay_multi_seed.csv`: 7,000 trial-level records (10 seeds x 700 trials, sham relay)
- `baseline_multi_seed.jl`: Baseline experiment code
- `sham_relay_exp.jl`: Sham relay experiment code
- `direct_asc_control_results.csv`: 10 seeds, direct ascending control
- `paper8_direct_asc.jl`: Direct ascending control experiment code
- `shuffle_relay_results.csv`: 10 seeds, shuffled stimulus order
- `paper8_shuffle.jl`: Shuffle experiment code
- `analyze_thalamic_gate.py`: Statistical analysis
- Figures: `fig2_learning_curves.png`, `fig3_onset_accuracy.png`, `fig4_paired_comparison.png`

## Acknowledgments

The Neuroblox team for the open-source framework. Independent reviewers (Codex, GPT) provided multiple rounds of critical feedback that substantially improved the manuscript, including the suggestion of a sham relay control.
