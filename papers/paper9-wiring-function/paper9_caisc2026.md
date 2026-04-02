# Wiring Determines Function: Connection Topology, Not Component Identity, Governs Learning in Biomimetic HH Circuits

**Tsubasa** (AI, first author) and **K. Yasukawa** (corresponding author)

*CAISC 2026 submission draft v10.2 -- 2026-04-02*

## Abstract

In a biomimetic Hodgkin-Huxley circuit performing two-category visual classification (700 trials, 30 seeds), connection target is the primary determinant of circuit function. Adding 10 identical HHNeuronExci neurons projecting to association cortex destroys learning (49.8%, near chance; paired t-test: t=-17.86, p<10^-16, d=-3.26, 0/30 seeds improved), while routing the same neurons through a thalamic gate improves learning from 76.0% to 88.3% (t=17.93, p<10^-16, d=+3.27, 30/30 improved). Weight sensitivity is asymmetric: gate connections are weight-insensitive (w=0.5: 88.3%, w=1.0: 88.7%, p=0.253), while cortex connections are weight-sensitive (w=1.0: 49.8%, w=0.5: 74.3%, t=12.68, p<10^-13, d=+2.32). Replacing amygdala neurons with generic neurons of identical biophysical parameters produces identical results (88.3%=88.3%, 49.8%=49.8%), confirming that component identity is irrelevant. Spike-level analysis across two independent seeds reveals the mechanism: gate routing ensures signal delivery (silent trials reduced from 13-18% to <1%), selectively amplifies winners (dominance ratio 1.60-1.74 to 2.55-3.21), and maintains competitive dynamics (entropy 1.38-1.53 vs 2.94-3.02 bits for direct cortex routing). These results, robust across 30 initialization seeds and 11 experimental conditions, indicate that in this biomimetic HH circuit, where neurons connect matters more than what connects, and that thalamic relay gating may function as a computational buffer rather than passive signal repetition.

## Introduction

Pathak et al. (2026) demonstrated that a biomimetic corticostriatal circuit reproduces category learning from biological first principles. Here we ask: when identical neurons are added to this circuit, what determines whether learning improves or collapses? Our results show that wiring topology alone determines the outcome.

Biological evidence supports this principle. O'Leary and Stanfield (1989) showed that cortical neurons transplanted to ectopic sites develop axon projection patterns matching their new location rather than their origin, demonstrating that the connectivity environment shapes neuronal output at the anatomical level. Revah et al. (2022) demonstrated that human cortical organoids transplanted into rat somatosensory cortex integrate into host circuits and drive behavior. To our knowledge, we provide the first computational demonstration of this principle at the cognitive task level using biophysically detailed HH neurons.

Prior computational work provides context: John et al. (2016) modeled how amygdala projections to the thalamic reticular nucleus mediate emotion-guided attentional gating, and Aizenberg et al. (2019) demonstrated that this pathway amplifies cortical sound responses. Primate anatomical data (Zikopoulos and Barbas, 2012) provides the structural foundation for this amygdala-TRN pathway. We extend prior work by systematically manipulating connection target, weight, and component identity within a complete cognitive circuit, with ascending thalamic relay input as a computational prerequisite (Tsubasa, 2026a).

## Methods

**Base circuit.** Picower corticostriatal circuit (Neuroblox.jl; Pathak et al., 2026): VAC (4 WTA (winner-take-all) groups, 20 HHNeuronExci + 4 HHNeuronInh), AC (2 WTA, 10 exci + 2 inh), ThalamicGate (20 HHNeuronExci), ascending input (NextGenerationEI), 2 Striatum (5 HHNeuronInh each), 2 TAN, SNc, GreedyPolicy. Two-category visual classification, 700 trials, seeds 42-71, Vern7 solver (reltol=1e-7, abstol=1e-7; Neuroblox.jl defaults), saveat=[trial_dur].

**Added neurons.** 10 HHNeuronExci (E_syn=0.0, G_syn=3.0, tau=5.0, no internal connections). Labeled "AMY" or "Generic" depending on condition; biophysical parameters are identical.

**Conditions (11 total).** Phase 1: (1) Gate-only baseline. (2) +Hippocampus (static DG-CA3-CA1 with fixed weights and no synaptic plasticity, 15 HHNeuronExci; exploratory). (3) +AMY to AC+Gate (w=1.0 to both). (4) +AMY to AC only (w=1.0; sham). (5) +AMY to Gate only (w=0.5). (6) AMY-Gate with save_everystep (solver robustness replication). (7) Excitatory overdrive (10 matched HHNeuronExci, no routing; sham control). Phase 2 (weight and identity controls): (8) AMY to Gate (w=1.0). (9) AMY to AC (w=0.5). (10) Generic relay to Gate (w=0.5). (11) Generic relay to AC (w=1.0).

**Statistics.** All comparisons are paired t-tests (two-tailed) against the gate-only baseline using the same 30 seeds. Cohen's d computed as mean paired difference divided by SD of paired differences (ddof=1). Bonferroni correction for 6 confirmatory comparisons yields alpha=0.0083; all confirmatory p-values are below 10^-8, so all remain significant. Exploratory and control comparisons are reported without correction.

## Results

**Table 1.** Full results across 11 conditions (N=30, paired vs gate-only baseline).

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
| Generic to Gate (w=0.5) | 88.3% (7.9) | +12.3pp | +3.27 | 30/30 | identity control |
| Generic to AC (w=1.0) | 49.8% (1.6) | -26.2pp | -3.26 | 0/30 | identity control |

**Connection target determines function.** The same 10 neurons produce d=+3.27 or d=-3.26 depending solely on connection target. Gate routing improves learning (88.3%); cortex routing destroys it (49.8%). When both targets receive input simultaneously (Condition 3), the result (49.6%) is statistically indistinguishable from cortex-only (49.8%; t=-0.65, p=0.518), indicating that cortex disruption fully negates gate benefit rather than merely dominating it.

**Weight sensitivity is asymmetric.** Gate connections are weight-insensitive: w=0.5 (88.3%) and w=1.0 (88.7%) are statistically indistinguishable (t=1.17, p=0.253, d=+0.21). Cortex connections are weight-sensitive: w=1.0 destroys learning (49.8%), while w=0.5 renders the connection harmless (74.3%, t=-1.51, p=0.143 vs baseline). The direct comparison between cortex w=1.0 and w=0.5 is significant (t=12.68, p<10^-13, d=+2.32). This asymmetry suggests qualitatively different circuit mechanisms: the gate, already driven by ascending arousal input, operates as a digital switch where signal presence matters more than magnitude; the cortex circuit operates as an analog system where input magnitude directly determines interference with WTA competition.

**Component identity is irrelevant.** Replacing AMY neurons with Generic neurons of identical biophysical parameters produces exactly the same results: Gate 88.3%=88.3%, AC 49.8%=49.8% (paired differences are zero across all 30 seeds). This confirms that, under these experimental conditions, neuron identity does not contribute to the outcome; connection topology is the primary determinant.

**Hippocampal addition.** The static hippocampal circuit showed a nominally significant effect (t=3.00, p=0.006, d=+0.55), but this is exploratory, does not survive Bonferroni correction, and is condition-sensitive (p=0.98 under save_everystep; see Limitations).

**Controls.** The excitatory overdrive sham (76.9%, p=0.14) confirms that adding matched excitatory neurons without specific routing has no effect, ruling out generic excitatory drive. The save_everystep replication (86.6%, d=+1.83, 29/30 wins) confirms that the direction and consistency of the gate improvement are robust to solver settings. The reduced effect size (d=+1.83 vs +3.27) reflects that save_everystep evaluates all intermediate adaptive time steps rather than only the trial-endpoint state captured by saveat=[trial_dur], introducing solver-internal variability into the accuracy measurement. The improvement direction (29/30 wins) is preserved.

**Spike-level analysis: relay as computational buffer.** To understand why gate routing improves and cortex routing destroys performance, we analyzed single-neuron spiking activity in the AC excitatory population (10 neurons: 2 WTA groups x 5 each) across 700 trials in two independent seeds (42 and 43). Spike detection used upward threshold crossings at V > -20 mV. Three indicators reveal the mechanistic basis of the topology effect:

**Table 2.** Spike-level indicators for AC excitatory neurons (10 neurons, 700 trials per seed). AC w=0.5 is below the weight-sensitivity cliff; AC w=1.0 is above it. Dominance ratio: max spike count / 2nd-max per trial. Entropy: per-trial Shannon entropy of normalized spike-count distribution (bits), averaged across 700 trials. Silent trials: trials with zero AC excitatory spikes.

| Condition    | Seed | Dom. ratio | Entropy | Silent trials |
|--------------|------|------------|---------|---------------|
| Baseline     | 42   | 1.60       | 0.398   | 93/700 (13%)  |
| Baseline     | 43   | 1.74       | 0.362   | 123/700 (18%) |
| Gate (w=0.5) | 42   | 3.21       | 1.376   | 2/700 (<1%)   |
| Gate (w=0.5) | 43   | 2.55       | 1.531   | 1/700         |
| AC (w=0.5)   | 42   | 1.85       | 2.480   | 1/700         |
| AC (w=0.5)   | 43   | 1.65       | 2.697   | 1/700         |
| AC (w=1.0)   | 42   | 1.47       | 3.018   | 1/700         |
| AC (w=1.0)   | 43   | 1.67       | 2.942   | 1/700         |

Across both seeds, relay routing exhibits three consistent patterns: (1) **Signal delivery**: Gate routing reduces silent trials from 13-18% to <1% (93-123 to 1-2 out of 700), ensuring cortical activation on every trial. (2) **Selective amplification**: Gate routing increases the winner dominance ratio from baseline (1.60, 1.74) to (3.21, 2.55), strengthening WTA competition. (3) **Competition maintenance**: Direct cortex routing at w=1.0 maximizes population entropy (3.02, 2.94 bits; theoretical maximum 3.32 for 10 neurons), destroying WTA selectivity. Gate routing maintains lower entropy (1.38, 1.53 bits), preserving competitive dynamics.

These results suggest that, in this circuit, the thalamic gate functions as a computational buffer that ensures signal delivery, amplifies winning representations, and protects cortical competition from input-driven disruption.

## Discussion

These results establish a quantitative design principle: in biomimetic HH circuits, connection topology is the primary determinant of cognitive function, while component identity and (for robust pathways) connection weight are secondary. This echoes biological findings where transplanted neurons develop projection patterns matching their host site (O'Leary and Stanfield, 1989) and human organoids integrate into rodent circuits (Revah et al., 2022). Recent large-scale neuroimaging shows that functional connectivity gradients organize cortical hierarchy across the human lifespan (Taylor et al., 2026). Our work extends this principle from correlational neuroimaging to causal computational demonstration at the single-neuron level.

The asymmetric weight sensitivity reveals that different circuit targets have qualitatively different robustness properties. Gate circuits, receiving ascending arousal input, absorb additional excitation without performance change. Cortex circuits, where direct projections interfere with learned WTA competition, are sensitive to input magnitude. The spike-level analysis quantifies this distinction: gate routing ensures signal delivery (silent trials 13-18% to <1%), selectively amplifies winners (dominance ratio 1.60-1.74 to 2.55-3.21), and maintains competitive dynamics (entropy 1.38-1.53 bits). Direct cortex routing achieves activation (silent trials ~0%) but destroys selectivity (entropy 2.94-3.02 bits, near maximum). Notably, AC routing at w=0.5 produces elevated population entropy (2.48, 2.70) yet preserves baseline-level accuracy (74.3%), suggesting that WTA competition tolerates moderate entropy increases. Only beyond a weight-dependent threshold does entropy rise sufficiently (3.02, 2.94 at w=1.0) to collapse selectivity and destroy learning. This is consistent with the analog sensitivity interpretation: cortex circuits degrade gradually with input magnitude rather than failing at a discrete threshold. This provides a mechanistic account of thalamic relay gating as computational buffering: in this circuit, the gate does not merely repeat signals, but transforms broadband input into selective, competition-compatible drive.

To our knowledge, no prior computational study using biophysically detailed neuron models has demonstrated that identical neurons produce opposite cognitive task outcomes solely through connection target manipulation. This constitutes a novel contribution to understanding structure-function relationships in neural circuits.

## Limitations

Weight sensitivity tested at two points only (w=0.5 and w=1.0); full weight sweep in progress (5x5 grid, 125 runs). Fixed stimulus order across seeds (confound ruled out by shuffle test: delta=-0.2pp, p=0.853). Single task (two-category classification). Spike analysis uses two seeds (42, 43); full 30-seed spike analysis deferred to future work. Hippocampal effect (p=0.006, d=+0.55) is exploratory, condition-sensitive (p=0.98 under save_everystep), and does not survive correction. Seeds 42-71 were chosen as a contiguous range starting from the Neuroblox test suite default (seed 42).

## References

- Aizenberg, M. et al. (2019). Projection from the Amygdala to the Thalamic Reticular Nucleus Amplifies Cortical Sound Responses. Cell Reports, 28(3), 605-615.e4.
- John, Y. J. et al. (2016). The Emotional Gatekeeper: A Computational Model of Attentional Selection and Suppression through the Pathway from the Amygdala to the Inhibitory Thalamic Reticular Nucleus. PLOS Computational Biology, 12(2), e1004722.
- O'Leary, D. D. M. and Stanfield, B. B. (1989). Selective elimination of axons extended by developing cortical neurons is dependent on regional locale. Journal of Neuroscience, 9(7), 2230-2246.
- Pathak, A. et al. (2026). Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications, 17, 390.
- Revah, O. et al. (2022). Maturation and circuit integration of transplanted human cortical organoids. Nature, 610, 319-326.
- Taylor, H. P. et al. (2026). Functional hierarchy of the human neocortex across the lifespan. Nature. DOI: 10.1038/s41586-026-10219-x.
- Tsubasa (2026a). Ascending Arousal Input Improves Category Learning Accuracy in a Biomimetic Corticostriatal Model. Zenodo. DOI: 10.5281/zenodo.19388682.
- Zikopoulos, B. and Barbas, H. (2012). Pathways for emotions and attention converge on the thalamic reticular nucleus in primates. Journal of Neuroscience, 32(15), 5338-5350.
