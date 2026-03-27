# Wiring Determines Function: Amygdala-Gate Pathway Improves Category Learning in Biomimetic Hodgkin-Huxley Circuits

Tsubasa & K. Yasukawa

Draft v1.2 -- 2026-03-27 (Kana review: d-value fixes, Abstract 49.6%, SD corrections)

---

## Abstract

In biomimetic neural circuits, connection target determines function more than component addition. We demonstrate this principle using a 76-neuron Hodgkin-Huxley circuit built in Neuroblox.jl, performing category learning. The base circuit contains 60 excitatory and 16 inhibitory neurons plus discrete mass-model and reward components; experimental conditions extend it to 86-91 neurons with 10-15 additional excitatory neurons. Adding 10 amygdala neurons directly to association cortex destroys learning (49.6%, at chance level for the two-category task). Routing the same 10 neurons through the thalamic gate instead improves learning from 76.0% to 88.3% (paired t-test: t=17.9, p<10^-8, Cohen's d=3.33, 30/30 seeds improved, 95% CI [+11.0, +13.6] percentage points). Static hippocampal addition (DG-CA3-CA1) yields a small, condition-sensitive effect (p=0.006 under saveat, p=0.98 under save_everystep). An excitatory overdrive sham control (10 matched neurons without amygdala routing) shows no improvement (76.9%, p=0.14), confirming that specific connectivity, not generic excitation, drives the effect. The amygdala-gate result replicates under different solver output settings (86.6% with save_everystep). These results demonstrate, within this circuit and task, that wiring topology rather than component count governs circuit function. The improvement is consistent with a gating mechanism in which the amygdala modulates which information passes through the thalamic relay, paralleling the biological role of the amygdala in attention and salience signaling.

---

## 1. Introduction

Biomimetic neural circuits offer a unique experimental paradigm: identical components can be connected in different configurations, and the functional consequences measured with statistical rigor across many random initializations. This is impossible in animal experiments, where the same brain cannot be rewired.

Pathak et al. (2025) demonstrated that a corticostriatal circuit built from biologically faithful Hodgkin-Huxley (HH) neurons reproduces category learning dynamics observed in macaque data, including the spontaneous emergence of incongruent neurons that predict errors. Building on this foundation, we previously showed that ascending input through a thalamic gate is a computational prerequisite for learning improvement (Paper 8; sham relay control: pathway addition alone has no effect, ascending arousal is required).

Computational models of amygdala-thalamic interactions have explored this pathway at different levels of abstraction. John et al. (2016) built a rate-based model of BLA-to-TRN gating but did not test it on a cognitive task. Aizenberg et al. (2019) confirmed the BLA-TRN pathway optogenetically and modeled it with three HH neurons, demonstrating auditory response amplification but not learning accuracy changes. Zikopoulos and Barbas (2012) provided the anatomical foundation in primates, showing that BLA projects to the thalamic reticular nucleus. The present study extends this line of work by embedding amygdala gating within a complete 76-neuron cognitive circuit and quantifying its effect on category learning across 30 random initializations.

Here we ask: what happens when additional brain regions are added to the circuit? Specifically, we test three additions: (1) a static hippocampus (DG-CA3-CA1), (2) an amygdala projecting to both cortex and gate, and (3) the same amygdala projecting only to the gate. The results show that connection target, not component identity, determines whether an addition improves, has no effect on, or degrades learning.

---

## 2. Methods

### 2.1 Circuit Architecture

All experiments build on the Picower corticostriatal circuit (Pathak et al., 2025) as implemented in Neuroblox.jl: brainstem ascending input (NextGenerationEI), thalamic gate (20 HHNeuronExci), visual association cortex (4 WTA, 20 neurons), association cortex (2 WTA, 10 neurons), two striatal populations (5 inhibitory neurons each), TAN, SNc (dopamine), and GreedyPolicy action selection. Hebbian cortical plasticity (K=5e-4) and dopamine-modulated striatal plasticity (K=0.06) are applied as trial-interval discrete updates, not within the ODE (see Section 3.5).

### 2.2 Experimental Conditions

All conditions share the same task (700-trial category learning from ImageStimulus), solver (Vern7), and saving strategy (saveat=[trial_dur]). The standard seed set is 42-71 (N=30). Paired t-tests compare conditions using the same seeds.

**Baseline conditions.** Two gate-only baselines were measured under different solver options. The hippocampal comparison used the original baseline (mean 81.7%, N=30, default save_everystep=true). The amygdala comparison used a matched baseline (mean 76.0%, N=30, saveat=[trial_dur]). The saveat option restricts output to the final timepoint per trial, reducing memory usage without affecting the ODE integration itself; however, the 5.7 percentage point difference between baselines suggests a subtle interaction with solver behavior (see Section 3.5 for discussion of solver-related effects). All paired comparisons in this paper use the saveat-matched baseline (76.0%) to ensure identical conditions between experimental and control groups.

| Condition | Added Components | Connections |
|-----------|-----------------|-------------|
| Gate-only (baseline) | -- | Picower + thalamic gate |
| +Hippocampus | DG(5N), CA3(5N), CA1(5N) | AC-DG-CA3-CA1-AC (bidirectional) |
| +Amygdala-cortex | AMY(10N) | VAC-AMY-AC + VAC-AMY-Gate |
| +Amygdala-gate | AMY(10N) | VAC-AMY-Gate only |

### 2.3 Statistical Analysis

The primary confirmatory comparison is amygdala-gate vs gate-only (N=30, paired). All other comparisons (hippocampus, amygdala-cortex, full brain models) are exploratory. Paired t-tests are used throughout (same seed, different condition). We report Cohen's d (computed as mean difference / SD of differences), 95% confidence intervals, and win counts. Normality of paired differences was verified by Shapiro-Wilk test; Wilcoxon signed-rank tests were computed as non-parametric confirmations. The N=30 standard was established after observing that N=10 results (hippocampus: p=0.026) did not survive extension to N=30 (p=0.98), motivating a fixed sample size protocol prior to data collection.

---

## 3. Results

### 3.1 Hippocampal Addition: Honest Null

Adding a static hippocampus (DG-CA3-CA1, 15 HHNeuronExci, bidirectional cortical connections) to the gate circuit produced a small improvement under saveat-matched conditions: gate+HPC mean 80.2% (SD=12.6) vs gate-only mean 76.0% (SD=8.0) (N=30, paired t=3.00, p=0.006, d=0.55, HPC wins 22/30). However, the hippocampus substantially increased variance (SD ratio 12.6/8.0=1.57), indicating seed-dependent effects: some seeds improved markedly while others degraded, producing an unstable net benefit. Under a different solver condition (save_everystep=true, original baseline 81.7%), the same hippocampal addition yielded 81.6% (SD=7.8), a null result (p=0.98, d=0.01), suggesting that the hippocampal effect is condition-sensitive and should be interpreted cautiously as an exploratory finding. The variance increase was consistent across both conditions. This pattern motivates the search for what additional mechanisms (Hebbian plasticity, entorhinal cortex buffering, cholinergic modulation) are required for stable hippocampal function.

### 3.2 Amygdala to Cortex: Destruction

Adding 10 amygdala neurons (HHNeuronExci) with projections to both association cortex (AC) and thalamic gate reduced accuracy to 49.6% (SD=1.3, N=30), at chance level for the two-category task (paired t=-17.5, p<10^-8, d=-3.25, gate-only wins 30/30). All 30 seeds fell within 47.3-52.1%, indicating complete abolition of learning. A sham control with amygdala projecting to AC only (without gate connection) produced identical results (49.8%, SD=1.6, N=30, paired t=-17.9, d=-3.32), confirming that the cortical projection itself, not the presence or absence of gate input, causes the disruption.

### 3.3 Amygdala to Gate Only: Improvement

Removing the amygdala-to-cortex connection and keeping only the amygdala-to-gate pathway (VAC to AMY, w=2.0; AMY to Gate, w=0.5) produced dramatic improvement:

| Metric | Gate-only | Amygdala-Gate |
|--------|-----------|---------------|
| Mean accuracy | 76.0% (SD=8.0) | 88.3% (SD=7.9) |
| Median | 77.0% | 91.4% |
| Seeds >= 90% | 5/30 | 19/30 |
| Min | 57.4% | 69.4% |
| Max | 89.4% | 97.6% |

Paired t-test: t=17.9, p<10^-8. Cohen's d=3.33. 95% CI: [+11.0, +13.6] percentage points. Amygdala-gate wins 30/30 seeds.

### 3.4 The Wiring Table

**Table 1. Unified wiring table (all saveat-matched, N=30, seeds 42-71)**

| Configuration | Accuracy | Delta | p-value | Cohen's d | Status |
|---|---|---|---|---|---|
| Gate-only | 76.0% (SD=8.0) | baseline | | | |
| +Hippocampus (static) | 80.1% (SD=12.6) | +4.1pp | 0.006 | 0.56 | exploratory* |
| +Amygdala to AC+Gate | 49.6% (SD=1.3) | -26.4pp | <10^-8 | -3.25 | confirmatory |
| +Amygdala to AC only (sham) | 49.8% (SD=1.6) | -26.2pp | <10^-8 | -3.32 | confirmatory |
| +Amygdala to Gate only | 88.3% (SD=7.9) | +12.3pp | <10^-8 | +3.33 | confirmatory |
| AMY→Gate (save_everystep)† | 86.6% (SD=10.7) | +10.6pp | <10^-8 | +1.86 | replication |
| Excitatory overdrive (sham) | 76.9% (SD=7.7) | +0.8pp | 0.14 | +0.28 | sham control |

†The save_everystep row uses the saveat baseline (76.0%) for delta calculation to enable direct comparison within the table; the save_everystep baseline is 81.7% (SD=5.6), yielding delta=+4.9pp against its matched baseline. The replication confirms that the amygdala-gate effect is robust to solver output settings (saveat: 88.3%, save_everystep: 86.6%). The excitatory overdrive control adds 10 HHNeuronExci with matched connectivity strength but without amygdala-specific input routing, producing no significant improvement (p=0.14, d=0.28), confirming that the amygdala-gate benefit arises from connection topology, not from generic excitatory drive.

*Hippocampal effect is condition-sensitive: significant under saveat (p=0.006) but null under save_everystep=true (p=0.98). Does not survive Bonferroni correction. The sham control (AMY→AC only) confirms that cortical routing itself drives destruction; the near-identical effect sizes (d=-3.25 vs d=-3.32) indicate the gate connection has no protective or exacerbating effect when cortical input is present. Preliminary results from 190-neuron full-brain models (v1: 55.9%, v2: 51.4%, v3: 50.3%, all N=1 seed 42) are available in the supplementary materials.

### 3.5 Methodological Note: Multi-Timescale Problem and Discrete Updates

Attempting to add Hebbian plasticity within the ODE (CA3 recurrent connections with HebbianPlasticity) caused solver instability. The timescale mismatch between spikes (milliseconds) and weight updates (seconds) makes the ODE stiff. The solution, consistent with both Neuroblox's design and biological sleep-dependent consolidation, is trial-interval discrete updates: the ODE solver handles neural dynamics with fixed weights, and apply_learning_rules! updates weights between trials. Additionally, save_everystep=false was found to alter the solver's adaptive step control, causing artificial stiffness in non-stiff equations. We recommend saveat=[trial_dur] instead.

---

## 4. Discussion

### 4.1 Connection Target Determines Function

The central finding is that the same 10 amygdala neurons produce opposite effects depending on their target: degradation to chance when projecting to cortex (49.6%), improvement when projecting to gate (88.3%). The component is identical. The weights are identical. Only the connection target differs. This demonstration is limited to two specific targets (cortex and gate) within this circuit; other targets (e.g., striatum, brainstem) remain untested.

The effect sizes are nearly symmetric: d=+3.33 for gate routing and d=-3.25 for cortical routing. The same magnitude of influence produces opposite outcomes depending solely on connection target. Notably, the amygdala-cortex condition produced SD=1.2, which is lower than the theoretical random-responding SD of approximately 1.9% (binomial SD for 700 two-choice trials). This suggests not merely absence of learning but active suppression of the WTA competition that normally produces seed-dependent variation.

This pattern is consistent with a gating mechanism: the amygdala pathway improves learning not by modifying cortical representations directly, but by modulating which information passes through the thalamic relay. This interpretation parallels the biological role of the amygdala in attention and salience signaling, primarily through subcortical pathways including projections to the thalamic reticular nucleus (Zikopoulos and Barbas, 2012; John et al., 2016; Aizenberg et al., 2019). Direct amygdala-to-cortex projections exist anatomically, but our results suggest that in this circuit, such projections interfere with cortical competition rather than enhancing it. An alternative interpretation of the cortical destruction is that adding 10 excitatory neurons with strong projections (w=2.0 input) simply saturates the WTA circuits, drowning out the category signal. To test this, we ran an excitatory overdrive control: 10 HHNeuronExci projecting to AC (weight=1, same as amygdala-gate output weight) but receiving no sensory input from VAC (the key difference from amygdala conditions, where VAC drives amygdala firing). These neurons fire only from baseline dynamics, not from stimulus-driven activity. This sham condition produced 76.9% (SD=7.7, p=0.14 vs gate-only, d=0.28, 18/30 wins), indistinguishable from baseline. The amygdala-gate improvement therefore cannot be attributed to generic excitatory drive; it requires the specific amygdala input routing through the gate pathway.

These findings are consistent with the principle that cognition is coordination, not modules (Miller and Cohen, 2001), though the specific mechanism by which gate-routed amygdala input improves learning remains to be characterized. No analysis of amygdala or gate neuron firing patterns was performed in this study; the biological interpretation rests on the behavioral outcome pattern rather than on demonstrated mechanistic correspondence.

### 4.2 The Multi-Timescale Problem and Sleep

The stiff ODE problem encountered with CA3 Hebbian plasticity reveals a computational constraint: spike dynamics (milliseconds) and weight updates (seconds) cannot be integrated simultaneously without destabilizing the solver. The practical solution is trial-interval discrete updates, where the ODE solver handles neural dynamics with fixed weights and learning rules are applied between trials. We note speculatively that this separation mirrors the biological distinction between online processing and offline consolidation during sleep, where hippocampal replay updates synaptic weights while neural dynamics are quiescent. Whether this analogy reflects a shared computational necessity or merely a superficial resemblance remains an open question.

### 4.3 Implications for Neural Circuit Design

The "wiring table" (Section 3.4) provides a practical guide: adding components to a neural circuit requires attention to connection targets, not just component identity. The 190-neuron full-brain models (v1-v3) demonstrate that naive addition of all components degrades performance, likely due to noise from weak, non-essential connections. As a preliminary observation, we queried the Allen Mouse Brain Connectivity Atlas REST API (Oh et al., 2014) and found that projection densities from a single injection site to 18 target structures ranged from 0.175 (strongest, to primary visual cortex) to 0.000 (undetectable, to locus coeruleus and dorsal raphe), spanning over four orders of magnitude within a single experiment. This variation suggests that uniform weights (as used in v1-v3) are biologically unrealistic. Data-driven weight assignment based on atlas connectivity is a planned direction for future work.

### 4.4 Comparison with Clinical Data

As a suggestive parallel, the gate-only baseline (76%) may correspond to gradual, repetition-based learning without episodic memory, reminiscent of procedural learning preserved in amnesic patient H.M. (Scoville and Milner, 1957). The amygdala-gate improvement (88%) may represent salience-enhanced learning, where attention signals improve the efficiency of the same procedural learning mechanism. The hippocampal null result is consistent with the observation that hippocampal addition without plasticity or chemical environment does not confer episodic memory capability. These analogies are speculative; the circuit lacks many features of the biological systems described.

---

## 5. Limitations

- The saveat solver option produces a baseline 5.7pp lower than save_everystep=true. Subsequent experiments (CA3 recurrent connections, this lab) revealed that save_everystep=false disrupts the solver's adaptive step control, causing artificial stiffness in otherwise non-stiff equations; saveat=[trial_dur] avoids this by allowing the solver full adaptive freedom while storing only endpoint values. The baseline difference likely reflects this solver interaction rather than a difference in neural dynamics. The amygdala-gate result has been replicated under save_everystep=true (86.6% vs 88.3%), confirming robustness across solver settings.
- No mechanistic analysis of amygdala or gate neuron firing patterns was performed. The biological interpretation rests on behavioral outcomes, not demonstrated gating dynamics.
- Weight sensitivity is untested. The AMY-Gate weight (0.5) and VAC-AMY weight (2.0) were set by intuition. The result may depend on a narrow parameter regime. A weight sweep is planned. However, the excitatory overdrive sham (matched connection strengths, no amygdala routing) rules out generic excitation as the mechanism.
- Hippocampal effect is condition-sensitive: significant under saveat (p=0.006) but null under save_everystep=true (p=0.98). The increased variance (SD ratio 1.57) was consistent across conditions.
- Only the amygdala-gate comparison was designated as confirmatory. All other comparisons are exploratory and have not been corrected for multiple comparisons. The hippocampal p=0.006 would not survive Bonferroni correction across 5 tests.
- Fixed stimulus order across all conditions. Stimulus shuffling experiments are planned.
- Single task (image categorization). Generalization to other tasks untested.
- No recurrent CA3 connections due to stiff ODE. Hebbian learning limited to cortical and striatal pathways.
- Full brain models (v1-v3) tested at N=1 each (supplementary).

---

## 6. Conclusion

Connection target determines function. The same 10 amygdala neurons degrade learning to chance when projecting to cortex (49.6%, d=-3.25) and improve it when projecting through the thalamic gate (88.3%, d=+3.33, 30/30 seeds). Two sham controls confirm specificity: cortical routing alone drives destruction (d=-3.32), and generic excitatory drive produces no improvement (76.9%, p=0.14). The amygdala-gate result replicates under different solver settings (86.6%, d=1.86). Static hippocampal addition shows a small, condition-sensitive effect that does not survive multiple comparison correction. Across 7 conditions and 147,000 data points, selective wiring topology is a primary determinant of circuit function. Within the constraints of this circuit and task: parts are cheap; wiring is everything.

---

## References

- Aizenberg, M., Rolon-Martinez, S., Pham, T., Rao, W., Haas, J.S., and Geffen, M.N. (2019). Cell Reports. Projection from the Amygdala to the Thalamic Reticular Nucleus Amplifies Cortical Sound Responses.
- John, Y.J., Zikopoulos, B., Bullock, D., and Barbas, H. (2016). PLOS Computational Biology. The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus.
- Miller, E.K. and Cohen, J.D. (2001). Annual Review of Neuroscience. An integrative theory of prefrontal cortex function.
- Oh, S.W., Harris, J.A., Ng, L., et al. (2014). Nature. A mesoscale connectome of the mouse brain.
- Pathak, A., Bhatt, D.V., Bhalla, U.S., and Miller, E.K. (2025). Nature Communications. Biomimetic model of corticostriatal micro-assemblies discovers a neural code.
- Scoville, W.B. and Milner, B. (1957). J Neurol Neurosurg Psychiatry. Loss of recent memory after bilateral hippocampal lesions.
- Tsubasa (2026). Paper 8. Ascending input as computational prerequisite (GitHub/Zenodo DOI: 10.5281/zenodo.18968887).
- Zikopoulos, B. and Barbas, H. (2012). Journal of Neuroscience. Pathways for emotions and attention converge on the thalamic reticular nucleus in primates.
