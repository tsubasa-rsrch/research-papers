# Robustness of Error Clustering in a Biomimetic Corticostriatal Circuit: A Multi-Seed Replication Study

**Author**: Tsubasa (Independent Researcher)
**Date**: March 2026
**Target**: GitHub + Zenodo DOI

## Abstract

Pathak et al. (2026) reported that a biomimetic corticostriatal circuit model, constructed from biological first principles, spontaneously produces learning curves matching animal data and reveals incongruent neurons whose activity predicts errors. However, the robustness of these emergent properties across different initial conditions was not examined. We replicate the small corticostriatal circuit using Neuroblox v0.8.0 on consumer hardware (Apple M4 Max) and evaluate 10 independent random seeds, each producing 700 learning trials. We measure error clustering (consecutive error pairs relative to independence expectation) as a behavioral signature that may reflect, but does not directly measure, the incongruent neural activity reported in the original study. Clustering ratio exceeds 1.0 in 9 of 10 seeds (median: 1.21x). The directional consistency across seeds is significant (one-sided sign test, p = 0.011). Individual permutation tests (1000 shuffles per seed) show significance in 4 of 10 seeds (p < 0.05, uncorrected). These results provide the first multi-seed assessment of error clustering in biomimetic neural circuits, suggesting that the tendency toward error persistence is a property of the circuit architecture rather than specific initial weight configurations.

## 1. Introduction

Pathak et al. (2026) presented a biomimetic model of corticostriatal micro-assemblies that discovers a neural code for category learning. Their key finding was that the model, constructed entirely from biological first principles, produced learning behavior matching macaque experimental data without task-specific training. The model revealed incongruent neurons: cells whose activity during correct trials predicted errors on subsequent trials.

The original validation strategy compared model output against macaque behavioral and neural data. A complementary question remains: how robust are these emergent properties across different initial conditions? The model's synaptic connections are initialized with random weights from sparse distributions (Supplementary Figure S10 of Pathak et al.), and the authors note that sparse initial connectivity creates "anatomical pre-weighting" toward specific categories. Different random seeds therefore produce circuits with different initial connectivity and potentially different emergent dynamics.

We address this question by independently implementing the small corticostriatal circuit based on the Neuroblox v0.8.0 test suite architecture and running 10 independent random seeds. We measure error clustering as a behavioral metric. While Pathak et al. demonstrated that incongruent neural activity produces correlated errors in their model, our analysis operates exclusively at the behavioral level (trial-by-trial correctness sequences) and cannot establish whether the same neural mechanism underlies the clustering we observe. Behavioral error clustering is a necessary but not sufficient condition for incongruent activity; other mechanisms (e.g., slow synaptic drift, stimulus-specific difficulty) could also produce temporal error correlations.

## 2. Methods

### 2.1 Circuit Architecture

We independently implemented the small corticostriatal circuit by reference to the reinforcement learning test suite provided with Neuroblox v0.8.0 (NeurobloxPharma package, `cs_rl_testsuite.jl`). Our implementation follows the test suite architecture using the `@named` blox creation and `GraphSystem()` / `add_connection!()` API. This constitutes a test-suite-based replication rather than a direct reproduction of the original Pathak et al. code. The circuit comprises:

- **Visual cortex (VAC)**: Cortical blox, 4 WTA units, 5 excitatory neurons each, density 0.05
- **Association cortex (AC)**: Cortical blox, 2 WTA units, 5 excitatory neurons each, density 0.05
- **Ascending system**: NextGenerationEI neural mass model (parameters matching test suite)
- **Striatum**: Two Striatum blox (STR1, STR2), 5 inhibitory neurons each
- **Tonically Active Neurons**: Two TAN populations (kappa = 10)
- **Dopamine**: SNc (kappa_DA = 1)
- **Action selection**: GreedyPolicy evaluating Matrisome rho at t = 2 * time_block_dur

Inter-module connections include corticocortical, corticostriatal, TAN-striatal, cross-striatal inhibition, and striatal-SNc projections, following the test suite wiring pattern.

### 2.2 Learning Rules

- **Corticocortical**: HebbianPlasticity (K = 5e-4, W_lim = 7)
- **Corticostriatal**: HebbianModulationPlasticity (K = 0.06, decay = 0.01, alpha = 2.5, theta_m = 1, dopamine-modulated via SNc)

### 2.3 Stimulus Set and Presentation

We used `smaller_cs_stimuli_set.csv` provided with Neuroblox (20 pixels per image, 2 categories, 1000 images). The first 700 images were presented in fixed order. Critically, stimulus presentation order was identical across all 10 seeds; the seed parameter varied only the initial synaptic weights via Julia's `Xoshiro` RNG, which was used to initialize each blox independently (e.g., `rng = Xoshiro(rand(Int))` after `Random.seed!(seed)`).

Trial duration: 1000 ms. Time block: 90 ms. Warmup: 200 ms. Solver: Vern7().

### 2.4 Experimental Design

10 independent experiments with random seeds 42 through 51. Each experiment: 700 learning trials with the `run_experiment!` API. Per-trial outputs: action, correctness, DA value.

### 2.5 Error Clustering Analysis

For each seed, we count observed consecutive error pairs (trial t incorrect AND trial t+1 incorrect). Under the null hypothesis of independent errors with per-trial error probability p = n_errors / N_trials, the expected number of consecutive pairs is:

E[pairs] = (N - 1) * p^2

The clustering ratio = observed_pairs / E[pairs]. This analytic expectation serves as a descriptive baseline; formal inference relies on the permutation test below.

**Permutation test**: For each seed, we shuffle the trial-level correctness vector 1000 times (preserving the total number of errors but randomizing their positions) and recompute consecutive pairs. The p-value is the proportion of permutations yielding pairs >= observed. The permutation null is exact (conditioned on total error count) and does not rely on the analytic approximation above.

**Sign test**: To assess overall directional consistency, we test whether the proportion of seeds with ratio > 1.0 exceeds the null expectation of 0.5 using a one-sided exact binomial test. The one-sided test is justified as an a priori directional hypothesis: Pathak et al. (2026) demonstrated that incongruent neural activity produces temporally correlated errors in the same circuit architecture, predicting clustering ratios > 1.0. There is no known mechanism in this circuit that would systematically produce anti-clustering (ratio < 1.0).

**Multiple testing**: The 10 individual permutation tests are not corrected for multiple comparisons. We report the number of individually significant seeds descriptively; the primary statistical claim rests on the sign test across all seeds.

### 2.6 Hardware and Software

Apple M4 Max (48 GB). Julia 1.12.5, Neuroblox 0.8.0. Total computation: ~170 minutes for 10 seeds including JIT compilation. Analysis: Python 3.12, pandas, numpy, scipy.

## 3. Results

### 3.1 Learning Performance

All 10 seeds achieved successful category learning. Mean accuracy: 77.7% (range: 66.3 - 86.6%). First 50 trials: 48.2% mean (near chance). Last 50 trials: 88.8% mean.

### 3.2 Error Clustering

9 of 10 seeds showed clustering ratios exceeding 1.0 (mean: 1.21x, median: 1.21x, range: 0.94 - 1.52x).

| Seed | Accuracy | Ratio | Permutation p |
|------|----------|-------|--------------|
| 42 | 76.9% | 1.52x | 0.001* |
| 43 | 70.6% | 1.11x | 0.125 |
| 44 | 66.3% | 1.04x | 0.306 |
| 45 | 78.9% | 1.28x | 0.024* |
| 46 | 79.0% | 0.94x | 0.700 |
| 47 | 79.3% | 1.33x | 0.019* |
| 48 | 81.3% | 1.10x | 0.289 |
| 49 | 79.6% | 1.10x | 0.282 |
| 50 | 78.6% | 1.31x | 0.022* |
| 51 | 86.6% | 1.43x | 0.062 |

Individual permutation tests: 4/10 seeds significant at p < 0.05 (uncorrected; see Section 2.5 for multiple testing note). Directional consistency: 9/10 seeds with ratio > 1.0 (one-sided sign test, p = 0.011).

### 3.3 Clustering Onset (Exploratory)

As an exploratory analysis, we identified the earliest 50-trial sliding window (step 25) where the clustering ratio first exceeded 1.0. Onset occurred at mean trial 140 (SD = 53, N = 10, range: 100 - 275). This threshold-based criterion is sensitive to error sparsity in later learning phases and should be interpreted cautiously. The observation that onset consistently follows the initial learning phase is suggestive of a relationship between categorical representation formation and error clustering emergence, but formal statistical testing of onset timing is beyond the scope of this study.

### 3.4 Category Asymmetry

All 10 seeds showed higher error rates for Category 2 than Category 1 in the stable phase (trials 400-700): Cat1 2.1-11.0%, Cat2 7.7-48.1%. Since stimulus order was identical across all seeds and only initial weights varied, this result shows that, under fixed stimulus presentation, Category 2 disadvantage reproduces across initial conditions. However, because item difficulty and trial order effects are confounded in this design, we cannot distinguish whether the asymmetry reflects inherent pixel-pattern difficulty or order-dependent learning dynamics. Disentangling these factors requires randomizing stimulus order across seeds.

### 3.5 Dopamine Prediction

DA before errors vs before correct trials showed inconsistent directionality (4/10 seeds with lower DA preceding errors; indistinguishable from chance under the null of no directional effect). Trial-level DA does not reliably predict next-trial errors.

## 4. Discussion

We report a multi-seed assessment of error clustering in a biomimetic corticostriatal circuit. The original Pathak et al. (2026) study identified incongruent neurons through direct analysis of neural spiking patterns and validated the model against macaque data. Our analysis operates at the behavioral level, measuring whether error sequences show non-random temporal structure.

**Relationship to incongruent activity.** Error clustering is consistent with, but does not uniquely identify, incongruent neural activity. Pathak et al. showed that incongruent neurons produce correlated errors; our behavioral finding is compatible with this mechanism but could also arise from other sources of error autocorrelation, such as slow weight drift or stimulus-specific difficulty patterns. Neural-level analysis (e.g., Matrisome rho values at decision time) would be needed to confirm whether incongruent activity underlies the behavioral clustering we observe.

**Robustness across initial conditions.** The key finding is that error clustering direction is consistent across initial conditions (sign test p = 0.011), even though individual seeds vary in effect magnitude and the effect size is modest (mean ratio 1.21x). This pattern is consistent with an architectural contribution to error persistence: the circuit's competitive WTA dynamics and dopamine-modulated plasticity create conditions where error states tend to persist, regardless of specific initial weight configurations.

**Exploratory observations.** The clustering onset timing (~trial 140) suggests that error clustering may not be present during early random responding but emerges as categorical representations form, though this observation requires more rigorous temporal analysis to confirm.

**Replication scope.** Our implementation is based on the Neuroblox v0.8.0 test suite rather than the original Pathak et al. codebase. While the test suite is provided by the same research group and follows the same architecture, minor implementation differences may exist. Our results therefore show robustness within the Neuroblox test suite implementation specifically.

### Limitations

- Error clustering is an indirect behavioral metric; neural-level incongruent activity was not directly measured. The inferential gap between behavioral clustering and neural mechanism remains open.
- N = 10 seeds with fixed stimulus order; stimulus-order randomization needed to separate item difficulty from learning dynamics.
- Individual permutation p-values are uncorrected for multiple comparisons; the 4/10 significant seeds should be interpreted descriptively.
- The clustering onset analysis uses a threshold-based criterion that may be sensitive to sparse errors in later learning phases.
- Small circuit configuration; the full Picower circuit may show different dynamics.
- Consumer hardware replication; numerical precision differences relative to the original study are possible.
- Test-suite-based implementation, not a direct reproduction of original code.

## 5. Conclusion

Error clustering in a biomimetic corticostriatal circuit shows a reliable directional tendency across initial condition variation. Directional consistency across 9 of 10 independent seeds (sign test p = 0.011), combined with individually significant clustering in 4 seeds (uncorrected), shows that the tendency toward error persistence within this circuit architecture is robust to initial weight variation. Whether this behavioral pattern reflects the same incongruent neural mechanism reported by Pathak et al. (2026) remains an open question that requires neural-level analysis. These results complement the original model-to-animal validation with a model-to-model robustness assessment.

## References

Pathak, A., Brincat, S.L., Organtzidis, H. et al. Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications (2026). https://doi.org/10.1038/s41467-025-67076-x

## Data Availability

All data and analysis code: https://github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper7-neuroblox-replication

- `multi_seed_results.csv`: 7,000 trial-level records (10 seeds x 700 trials)
- `multi_seed_neville.jl`: Experiment code (Julia/Neuroblox)
- `analyze_multi_seed.py`: Analysis with permutation tests (Python)

## Acknowledgments

K. Yasukawa for experimental design guidance, statistical review, and critical feedback on all drafts. The Neuroblox team (Neuroblox, Inc.) for the open-source framework and reproducible test suite.
