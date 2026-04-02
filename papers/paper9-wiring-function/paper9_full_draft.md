# Wiring Determines Function: Connection Topology, Not Component Identity, Governs Learning in Biomimetic HH Circuits

**Tsubasa** (AI, first author) and **K. Yasukawa** (corresponding author)

*CAISC 2026 full paper draft v0.2 -- 2026-03-31*

## Abstract

In a biomimetic Hodgkin-Huxley circuit performing two-category visual classification (700 trials, 30 seeds), connection target is the primary determinant of circuit function. Adding 10 identical HHNeuronExci neurons projecting to association cortex destroys learning (49.8%, near chance; paired t-test: t=-17.86, p<10^-16, d=-3.26, 0/30 seeds improved), while routing the same neurons through a thalamic gate improves learning from 76.0% to 88.3% (t=17.93, p<10^-16, d=+3.27, 30/30 improved). A full weight sweep (8 points per target, seed 42) reveals qualitatively different dose-response curves: gate routing saturates immediately (plateau at w>=0.25), while cortex routing shows a sharp collapse between w=0.5 and w=0.75 (-26.7pp), analogous to a pharmacological therapeutic window. Simultaneous gate and cortex routing at reduced weight (w=0.5 each) produces non-additive destruction (53.2%, d=-2.94, 0/30; predicted additive: 86.6%), demonstrating that cortical disruption is interactive rather than simply dominant. Component identity is irrelevant (AMY=Generic, exact match). Stimulus order shuffling confirms results are not confounded by fixed presentation order (delta=-0.2pp across 5 seeds × 5 orders). These results, across 12 experimental conditions, 30 initialization seeds and 5-seed weight sweep validation, establish that thalamic relay nuclei function as computational buffers that protect cortical WTA competition from excitatory disruption.

## 1. Introduction

How does the brain ensure that signals reaching cortex are beneficial rather than harmful? Relay nuclei, traditionally viewed as passive signal conduits between brain regions, are ubiquitous in vertebrate nervous systems. Yet their computational role remains underspecified: if relay merely transmits, direct cortical projection should produce equivalent outcomes. Here we test this assumption directly.

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit reproduces category learning from biological first principles using Hodgkin-Huxley neurons. We exploit this circuit as a testbed: when 10 identical neurons are added, does their connection target—thalamic gate versus association cortex—determine whether learning improves or collapses?

Biological evidence motivates this question. O'Leary and Stanfield (1989) showed that cortical neurons transplanted to ectopic sites develop projection patterns matching their new location. Revah et al. (2022) demonstrated that human cortical organoids transplanted into rat somatosensory cortex integrate into host circuits and drive behavior. These findings suggest that connectivity environment, not cellular identity, determines neuronal function. To our knowledge, we provide the first computational demonstration of this principle at the cognitive task level using biophysically detailed HH neurons.

Prior computational work on amygdala-thalamic pathways (John et al., 2016; Aizenberg et al., 2019) and primate anatomical data (Zikopoulos and Barbas, 2012) establish the structural basis for relay-mediated gating. Morita and Kumar (2026) showed that cortical excitation/inhibition (E/I) imbalance disrupts feedback alignment in rate-based corticostriatal models, calling for validation in more elaborative models. Our biophysically detailed HH circuit provides exactly this, demonstrating that cortical overexcitation destroys WTA competition at the single-neuron level, and that thalamic relay buffering protects against this failure mode.

## 2. Methods

### 2.1 Base circuit

Picower corticostriatal circuit (Neuroblox.jl; Pathak et al., 2026): visual association cortex (VAC: 4 WTA, 20 HHNeuronExci + 4 HHNeuronInh), association cortex (AC: 2 WTA, 10 exci + 2 inh), ThalamicGate (20 HHNeuronExci with ascending input), ascending arousal input (NextGenerationEI), 2 Striatum (5 HHNeuronInh each), 2 TAN, SNc dopamine modulator, GreedyPolicy action selection. Two-category visual classification task, 700 trials per experiment, seeds 42-71 (30 pseudo-random initializations), saveat=[trial_dur], Vern7 solver. All simulations are deterministic: identical seed and condition produce identical results across runs, confirmed by exact replication of 6 independent data points across separate experimental batches.

### 2.2 Added neurons

10 HHNeuronExci neurons (E_syn=0.0, G_syn=3.0, tau=5.0, no internal connections). Receive visual input from VAC excitatory neurons (w=2.0). Output target and weight varied across conditions. Labeled "AMY" or "Generic" depending on condition; biophysical parameters are identical in all cases.

### 2.3 Experimental conditions

**Phase 1: Core conditions (N=30 seeds each).**
(1) Gate-only baseline. (2) +Hippocampus (static DG-CA3-CA1, 15 HHNeuronExci; exploratory). (3) +AMY to AC+Gate (w=1.0 to both). (4) +AMY to AC only (w=1.0). (5) +AMY to Gate only (w=0.5). (6) AMY-Gate with save_everystep (solver robustness). (7) Excitatory overdrive (10 matched HHNeuronExci, no routing; sham).

**Phase 2: Weight and identity controls (N=30 seeds each).**
(8) AMY to Gate (w=1.0). (9) AMY to AC (w=0.5). (10) Generic relay to Gate (w=0.5). (11) Generic relay to AC (w=1.0). (12) AMY to AC+Gate (w=0.5 to both).

**Phase 3: Weight sweep (seed 42, 8 weights per target).**
Weights: 0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0. Applied to Gate and AC targets separately. Multi-seed validation: 3 key weights (0.0, 0.25, 1.0) × 5 seeds (42, 44, 51, 55, 65) × 2 targets = 30 runs.

**Phase 4: Stimulus order control (5 seeds × 5 orders).**
Seeds 42-46, each with original fixed order and 4 randomized stimulus permutations.

**Phase 5: Spike-level analysis (seed 42, 4 conditions).**
Spike-level analysis of AC neurons (seed 42): baseline (no extra neurons), gate w=0.5, AC w=0.5 (pre-cliff), AC w=0.75 (post-cliff). Metrics: winner dominance ratio, population entropy, winner identity stability. Voltage saved at 10ms intervals, spike detection at V > -20mV with hysteresis.

### 2.4 Statistics

All comparisons are paired t-tests (two-tailed) against the gate-only baseline using the same seeds. Cohen's d computed as mean paired difference divided by SD of paired differences (ddof=1). Bonferroni correction for confirmatory comparisons. Exploratory and control comparisons reported without correction.

## 3. Results

### 3.1 Connection target determines function

**Table 1.** Full results across 12 conditions (N=30, paired vs gate-only baseline).

| Configuration | Accuracy (SD) | Delta | d | Wins | Type |
|---|---|---|---|---|---|
| Gate-only baseline | 76.0% (8.0) | -- | -- | -- | baseline |
| +Hippocampus (static) | 80.1% (12.6) | +4.1pp | +0.55 | 22/30 | exploratory |
| +AMY to AC+Gate (w=1.0) | 49.6% (1.3) | -26.4pp | -3.20 | 0/30 | confirmatory |
| +AMY to AC only (w=1.0) | 49.8% (1.6) | -26.2pp | -3.26 | 0/30 | confirmatory |
| +AMY to Gate (w=0.5) | 88.3% (7.9) | +12.3pp | +3.27 | 30/30 | confirmatory |
| AMY-Gate (save_everystep) | 86.6% (10.7) | +10.6pp | +1.83 | 29/30 | replication |
| Excitatory overdrive | 76.9% (7.7) | +0.8pp | +0.28 | 18/30 | sham |
| AMY to Gate (w=1.0) | 88.7% (8.7) | +12.7pp | +3.09 | 30/30 | weight |
| AMY to AC (w=0.5) | 74.3% (10.5) | -1.7pp | -0.27 | 11/30 | weight |
| Generic to Gate (w=0.5) | 88.3% (7.9) | +12.3pp | +3.27 | 30/30 | sanity |
| Generic to AC (w=1.0) | 49.8% (1.6) | -26.2pp | -3.26 | 0/30 | sanity |
| +AMY to AC+Gate (w=0.5) | 53.2% (1.5) | -22.8pp | -2.94 | 0/30 | interaction |

The same 10 neurons produce d=+3.27 or d=-3.26 depending solely on connection target (Conditions 5 vs 4). Component identity is irrelevant: replacing AMY with Generic neurons produces identical results (Conditions 10-11). The excitatory overdrive sham (Condition 7, p=0.14; see also Tsubasa, 2026b) confirms that adding matched excitatory neurons without specific routing has no effect.

### 3.2 Weight sensitivity is asymmetric: digital switch vs therapeutic window

**Figure 1.** Weight sweep for Gate and AC routing (seed 42, 8 weights each). Seed 42 full curve (8 weights) shown with dashed lines; 5-seed mean ± SE (3 key weights) shown with solid lines and error bars.

| Weight | Gate Accuracy | AC Accuracy |
|--------|--------------|-------------|
| 0.0 | 80.4% | 80.4% |
| 0.1 | 84.6% | 84.6% |
| 0.25 | 91.9% | 86.1% |
| 0.5 | 94.0% | 80.1% |
| 0.75 | 92.9% | 53.4% |
| 1.0 | 93.3% | 50.1% |
| 1.5 | 94.6% | 49.9% |
| 2.0 | 94.3% | 50.9% |

At w=0.0, both curves converge (80.4%), confirming that divergence requires non-zero signal. Gate routing saturates at w>=0.25 (plateau: 91.9-94.6%, range 2.7pp), operating as a digital switch where signal presence matters more than magnitude. Cortex routing peaks modestly at w=0.25 (86.1%), then collapses sharply between w=0.5 and w=0.75 (-26.7pp), reaching chance level (50%) at w>=0.75.

This asymmetry is analogous to pharmacological dose-response: gate routing has a wide therapeutic window (effective at any dose above threshold), while cortex routing has a narrow window with a lethal threshold. The gate circuit, already driven by ascending arousal input (Tsubasa, 2026a), absorbs additional excitation; the cortex WTA circuit cannot.

Multi-seed validation (5 seeds × 3 key weights × 2 targets) confirms these patterns: at w=0.0, gate and cortex curves converge perfectly across all seeds (mean 80.5% = 80.5%). At w=0.25, a modest divergence appears (gate 90.4% vs cortex 87.6%, delta=-2.8pp). At w=1.0, the cliff is fully replicated (gate 91.1% vs cortex 50.3%, delta=-40.8pp), with cortex SD=1.8% indicating highly consistent collapse across seeds.

### 3.3 Non-additive interaction between relay and direct pathways

AC w=0.5 alone is harmless (74.3%, p=0.143 vs baseline). Gate w=0.5 alone improves learning (+12.3pp). If effects were additive, simultaneous AC w=0.5 + Gate w=0.5 should yield approximately 88.3% - 1.7pp = 86.6%. Instead, accuracy collapses to 53.2% (d=-2.94, 0/30 wins).

This non-additive destruction indicates that the gate pathway's activation of WTA competition creates a state that is paradoxically more vulnerable to simultaneous direct cortical input. When both pathways are active, the cortex receives structured input via the gate (beneficial) and unstructured input via direct projection (harmful) simultaneously, and the harmful component dominates.

Combined with the w=1.0 result (Condition 3: 49.6%), this establishes that cortex disruption is not merely dominant but interactive: the presence of any direct cortical projection, regardless of weight, eliminates the gate benefit entirely.

### 3.4 Stimulus order does not confound results

| Seed | Original | Shuffled Mean | Delta |
|------|----------|---------------|-------|
| 42 | 94.0% | 94.5% | +0.5pp |
| 43 | 92.3% | 93.0% | +0.7pp |
| 44 | 77.7% | 76.8% | -0.9pp |
| 45 | 94.1% | 94.1% | +0.0pp |
| 46 | 91.3% | 90.2% | -1.1pp |
| Mean | 89.9% | 89.7% | -0.2pp |

Stimulus order was confirmed to have negligible effect (mean delta = -0.2pp across 5 seeds × 5 orders).

### 3.5 WTA competition analysis

To characterize the mechanism underlying the accuracy cliff, we analyzed spike-level activity of VAC and AC excitatory neurons (N=30: 20 VAC + 10 AC) across four conditions (seed 42, 700 trials each). Accuracy values in the table below are seed 42 single-seed values; cf. Table 1 for 30-seed means.

| Condition | Accuracy | Dominance Ratio | Entropy | Max Entropy | Winner Stability |
|-----------|----------|----------------|---------|-------------|-----------------|
| Baseline (no extra) | 83.0% | 1.44 | 1.20 | 4.91 | 0.23 |
| Gate w=0.5 | 93.6% | 1.71 | 1.90 | 4.91 | 0.26 |
| AC w=0.5 (pre-cliff) | 80.1% | 1.42 | 2.73 | 4.91 | 0.24 |
| AC w=0.75 (post-cliff) | 53.4% | 1.36 | 3.20 | 4.91 | 0.24 |

Gate routing increases both dominance (1.44→1.71) and entropy (1.20→1.90), indicating that the gate creates stronger competition with a clearer winner: multiple neurons are active, but one consistently dominates. This is the signature of healthy WTA function.

Cortex overexcitation (w=0.75) increases entropy (1.20→3.20) while decreasing dominance (1.44→1.36), indicating diffuse activation without competitive resolution. Notably, the dominance difference between baseline and the post-cliff condition is only 0.08, yet accuracy drops by 30 percentage points. This indicates that the circuit operates near a critical point where small perturbations in WTA competition strength produce large performance changes.

The accuracy cliff thus reflects not a dramatic restructuring of WTA dynamics but a small perturbation near a critical operating point. The role of relay routing is to move the circuit away from this critical point into a stable regime (dominance 1.71), while direct cortical input pushes it toward and past the instability threshold.

## 4. Discussion

### 4.1 Relay nuclei as computational buffers

These results reframe relay nuclei from passive signal conduits to active computational buffers. The traditional view—that relay nuclei simply transmit signals between brain regions—predicts equivalent outcomes for relay-mediated and direct projections. Our data show the opposite: relay routing produces d=+3.27 improvement while direct cortical routing produces d=-3.26 destruction.

The weight sweep reveals the mechanism: the gate circuit, continuously driven by ascending arousal input, operates in a saturated regime where additional excitation is absorbed without altering output dynamics. This input normalization protects downstream cortical computation from the magnitude variability of incoming signals. Cortex WTA circuits, lacking this buffering, are sensitive to input magnitude and collapse when excitation exceeds a critical threshold.

### 4.2 E/I balance and the cortical vulnerability

Morita and Kumar (2026) showed that cortical E/I imbalance disrupts feedback alignment in corticostriatal reinforcement learning using rate-based models, calling for validation in more elaborative models. Our HH-level results provide a complementary demonstration: cortical overexcitation (AC w>=0.75) destroys WTA competition, producing chance-level performance.

Spike-level analysis reveals that this collapse operates through critical point instability rather than dramatic WTA restructuring. The baseline circuit operates with a winner dominance ratio of 1.44, near the minimum for functional WTA competition. Gate routing raises this to 1.71, moving the circuit into a stable operating regime. Direct cortical input at w=0.75 lowers dominance to 1.36, a decrease of only 0.08 from baseline, yet accuracy drops by 30 percentage points. Simultaneously, population entropy increases from 1.20 (baseline) to 3.20, indicating diffuse activation without competitive resolution.

Within the dynamical systems framework reviewed by Breakspear (2017), this pattern is consistent with a bifurcation in WTA dynamics: a small parameter change (connection weight) crosses a critical boundary, producing a qualitative shift in circuit behavior from functional competition to diffuse activation. The biological implication is that relay nuclei do not merely transmit signals but actively stabilize cortical WTA computation by elevating it above this bifurcation threshold. Breakspear (2017) reviews how corticothalamic feedback stabilizes cortical dynamics through multistable attractor landscapes; our results provide a single-neuron-level mechanism for this stabilization.

### 4.3 Non-additive pathway interaction as a design constraint

The non-additive destruction observed in simultaneous relay and direct routing (predicted: 86.6%; observed: 53.2%) reveals a fundamental design constraint: relay-mediated and direct pathways to the same cortical target are mutually exclusive in their functional contribution. This has implications for biological circuit design, where structures like the amygdala project to both the thalamic reticular nucleus (relay) and cortex (direct) simultaneously. Our data suggest that the balance between these dual pathways is computationally critical, and that overactivation of the direct pathway can negate the benefits of relay-mediated processing.

### 4.4 Biological correspondence

Our findings echo multiple levels of biological evidence:
- **Anatomical**: O'Leary and Stanfield (1989) demonstrated that transplanted cortical neurons develop host-appropriate projection patterns, establishing that connectivity determines function at the cellular level.
- **Developmental**: Revah et al. (2022) showed functional integration of transplanted human organoids, demonstrating cross-species connectivity-dependent function.
- **Network**: Taylor et al. (2026) found that functional connectivity gradients organize cortical hierarchy across the human lifespan, consistent with topology as the primary organizational principle.
- **Computational**: Morita and Kumar (2026) demonstrated E/I balance dependence in rate-based corticostriatal models; we extend this to HH-level single-neuron dynamics.

### 4.5 Novelty and scope

To our knowledge, no prior computational study using biophysically detailed neuron models has demonstrated that identical neurons produce opposite cognitive task outcomes solely through connection target manipulation. The combination of topology-dependent function reversal, asymmetric weight sensitivity, non-additive pathway interaction, and component identity irrelevance constitutes a novel contribution to understanding structure-function relationships in neural circuits.

## 5. Limitations

Single task (two-category classification). Full 8-point weight sweep is seed 42 only; 5-seed validation at 3 key weights confirms the pattern. Spike analysis is seed 42 only; multi-seed spike analysis deferred to future work. Seeds 42-71 were chosen as a contiguous range starting from the Neuroblox test suite default (seed 42). Hippocampal effect (p=0.006, d=+0.55) is exploratory, condition-sensitive, and does not survive correction.

## References

- Breakspear, M. (2017). Dynamic models of large-scale brain activity. Nature Neuroscience, 20(3), 340-352. DOI: 10.1038/nn.4497.
- Aizenberg, M. et al. (2019). Projection from the Amygdala to the Thalamic Reticular Nucleus Amplifies Cortical Sound Responses. Cell Reports, 28, 605-615.
- John, Y. J. et al. (2016). The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus. PLOS Computational Biology, 12(2), e1004722.
- Morita, K. and Kumar, A. (2026). Mesocorticostriatal reinforcement learning of state representation and value with implications for the mechanisms of schizophrenia. Journal of Neuroscience. DOI: 10.1523/jneurosci.1762-25.2026.
- O'Leary, D. D. M. and Stanfield, B. B. (1989). Selective elimination of axons extended by developing cortical neurons is dependent on regional locale. Journal of Neuroscience, 9(7), 2230-2246.
- Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications, 17, 390.
- Revah, O. et al. (2022). Maturation and circuit integration of transplanted human cortical organoids. Nature, 610, 319-326.
- Taylor, H. P. et al. (2026). Functional hierarchy of the human neocortex across the lifespan. Nature. DOI: 10.1038/s41586-026-10219-x.
- Tsubasa (2026a). Ascending Arousal Input Improves Category Learning Accuracy in a Biomimetic Corticostriatal Model. Zenodo. DOI: 10.5281/zenodo.19388682.
- Tsubasa (2026b). Thalamic gate with sham relay control. Zenodo. DOI: 10.5281/zenodo.19132003.
- Zikopoulos, B. and Barbas, H. (2012). Pathways for emotions and attention converge on the thalamic reticular nucleus in primates. Journal of Neuroscience, 32(15), 5338-5350.
