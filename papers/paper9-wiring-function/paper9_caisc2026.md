# Wiring Determines Function: Amygdala Pathway Routing Produces Opposite Learning Outcomes in Biomimetic HH Circuits

**Tsubasa** (AI, first author) and **K. Yasukawa** (corresponding author)

*CAISC 2026 submission draft v0.1 -- 2026-03-27*

## Abstract

In a 76-neuron Hodgkin-Huxley circuit performing category learning, connection target determines function more than component addition. Adding 10 amygdala neurons projecting to association cortex destroys learning (49.6%, chance level; d=-3.25, 0/30 seeds improved). Routing the same neurons through a thalamic gate instead improves learning from 76.0% to 88.3% (d=+3.33, 30/30 seeds improved, p<10^-8). An excitatory overdrive control (matched neurons, no amygdala routing) shows no improvement (76.9%, p=0.14), confirming connectivity, not generic excitation, drives the effect. Across 7 conditions and 147,000 data points: parts are cheap; wiring is everything.

## Introduction

Pathak et al. (2025) demonstrated that a biomimetic corticostriatal circuit reproduces category learning from biological first principles. We previously showed that ascending thalamic relay input is a computational prerequisite for learning improvement (Paper 8). Here we ask: what happens when amygdala neurons are added to this circuit? The answer depends entirely on where they connect.

Computational models of amygdala-thalamic gating (John et al., 2016; Aizenberg et al., 2019) have explored this pathway but not within a complete cognitive circuit. Zikopoulos and Barbas (2012) provided the primate anatomical foundation. We extend this by embedding amygdala gating in a 76-neuron circuit and quantifying effects across 30 seeds.

## Methods

**Base circuit.** Picower corticostriatal circuit (Neuroblox.jl): VAC (4 WTA), AC (2 WTA), ThalamicGate (20 HHNeuronExci), Striatum, SNc, GreedyPolicy. 700 trials, seeds 42-71, saveat=[trial_dur], Vern7 solver.

**Conditions.** (1) Gate-only baseline. (2) +Hippocampus: DG-CA3-CA1, 15 HHNeuronExci. (3) +Amygdala to AC+Gate: 10 HHNeuronExci projecting to both AC and gate. (4) +Amygdala to AC only: sham, no gate connection. (5) +Amygdala to Gate only: gate pathway only. (6) Amygdala-gate with save_everystep: solver robustness check. (7) Excitatory overdrive: 10 matched HHNeuronExci, no amygdala routing.

## Results

**Table 1.** Unified wiring table (N=30, paired vs gate-only baseline).

| Configuration | Accuracy | Delta | d | Wins |
|---|---|---|---|---|
| Gate-only (baseline) | 76.0% | -- | -- | -- |
| +Hippocampus (static) | 80.1% | +4.1pp | 0.56 | 22/30 |
| +Amygdala to AC+Gate | 49.6% | -26.4pp | -3.25 | 0/30 |
| +Amygdala to AC only | 49.8% | -26.2pp | -3.32 | 0/30 |
| +Amygdala to Gate only | 88.3% | +12.3pp | 3.33 | 30/30 |
| AMY-Gate (save_everystep) | 86.6% | +10.6pp | 1.86 | 29/30 |
| Excitatory overdrive | 76.9% | +0.8pp | 0.28 | 18/30 |

The same 10 neurons produce d=+3.33 or d=-3.25 depending solely on connection target. The excitatory overdrive sham confirms the improvement requires amygdala-specific routing, not generic excitation. The hippocampal effect is condition-sensitive (p=0.006 under saveat, p=0.98 under save_everystep) and does not survive correction.

## Discussion

The near-symmetric effect sizes (d=3.33 vs d=-3.25) demonstrate that connection topology, not component identity, governs circuit function. The amygdala-cortex condition produces SD=1.2, lower than random-responding SD (1.9%), suggesting active suppression rather than mere absence of learning. This pattern is consistent with a gating mechanism: amygdala input modulates information passage through the thalamic relay, paralleling its biological role in salience signaling (Zikopoulos and Barbas, 2012).

The excitatory overdrive result (p=0.14) rules out generic excitatory drive as the mechanism, strengthening the connection-specificity interpretation. This dissociation between component addition and connection routing provides a quantitative design principle: adding neurons without attention to wiring topology degrades rather than improves performance.

## Limitations

Weight sensitivity untested. Fixed stimulus order. Single task. No mechanistic firing analysis. Hippocampal effect is condition-sensitive. Only amygdala-gate comparison was confirmatory; others are exploratory.

## References

- Aizenberg et al. (2019). Cell Reports.
- John et al. (2016). PLOS Computational Biology.
- Pathak et al. (2025). Nature Communications.
- Tsubasa (2026). Paper 8. GitHub/Zenodo DOI: 10.5281/zenodo.18968887.
- Zikopoulos and Barbas (2012). Journal of Neuroscience.
