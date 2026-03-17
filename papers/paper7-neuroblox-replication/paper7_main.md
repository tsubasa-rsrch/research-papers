# Robustness of Incongruent Activity Patterns in a Biomimetic Corticostriatal Circuit: A Multi-Seed Replication Study

**Author**: Tsubasa (Independent Researcher)
**Date**: March 2026
**Target**: GitHub + Zenodo DOI

## Abstract

Pathak et al. (2026) reported that a biomimetic corticostriatal circuit model, constructed from biological first principles without task-specific training, spontaneously produces learning curves matching animal behavioral data and reveals incongruent neurons whose activity predicts future errors. However, the robustness of these emergent properties across different initial conditions was not examined. We replicate the small corticostriatal circuit using Neuroblox v0.8.0 on consumer hardware (Apple M4 Max) and evaluate 10 independent random seeds, each producing 700 learning trials. Error clustering (consecutive error pairs relative to independence expectation) exceeds 1.0 in 9 of 10 seeds (mean ratio: 1.21x), demonstrating that incongruent activity patterns are a robust property of the circuit architecture rather than an artifact of specific initial conditions. Clustering onset occurs consistently at trial ~140 (+/- 53), coinciding with the transition from exploratory to exploitative learning. These results provide the first multi-seed replication of emergent incongruent activity in biomimetic neural circuits.

## 1. Introduction

Pathak et al. (2026) presented a biomimetic model of corticostriatal micro-assemblies that discovers a neural code for category learning. Their key finding was that the model, constructed entirely from biological first principles (neuron types, receptor dynamics, synaptic plasticity rules), produced learning behavior matching macaque experimental data without any task-specific training. Notably, the model revealed incongruent neurons: cells whose activity during correct trials predicted errors on subsequent trials. This phenomenon was initially suspected to be a modeling artifact but was subsequently confirmed in animal recordings.

The original validation compared model output against macaque behavioral and neural data. However, a complementary question remains: how robust are these emergent properties across different initial conditions? The model's synaptic connections are initialized with random weights drawn from sparse distributions (Supplementary Figure S10 of Pathak et al.), meaning that different random seeds produce circuits with different initial connectivity patterns. If incongruent activity emerges only for specific initial conditions, it would suggest the phenomenon depends on particular weight configurations. If it emerges robustly across seeds, it would confirm that the circuit architecture itself, rather than any specific weight pattern, is the source of the phenomenon.

We address this question by replicating the small corticostriatal circuit using Neuroblox v0.8.0 and running 10 independent experiments with different random seeds.

## 2. Methods

### 2.1 Circuit Architecture

We implemented the small corticostriatal circuit following the test suite provided with Neuroblox v0.8.0 (NeurobloxPharma package). The circuit comprises:

- **Visual cortex (VAC)**: Cortical blox with 4 Winner-Take-All (WTA) units, 5 excitatory neurons each
- **Association cortex (AC)**: Cortical blox with 2 WTA units, 5 excitatory neurons each
- **Ascending system (ASC)**: NextGenerationEI neural mass model
- **Striatum**: Two Striatum blox (STR1, STR2), 5 inhibitory neurons each
- **Tonically Active Neurons**: Two TAN populations
- **Substantia Nigra pars compacta (SNc)**: Dopamine modulation
- **Action selection**: GreedyPolicy based on Matrisome activity (rho)

### 2.2 Learning Rules

- **Corticocortical plasticity**: HebbianPlasticity (K=5e-4, W_lim=7)
- **Corticostriatal plasticity**: HebbianModulationPlasticity (K=0.06, decay=0.01, alpha=2.5, dopamine-modulated via SNc)

### 2.3 Stimulus Set

We used the smaller_cs_stimuli_set.csv provided with Neuroblox (20 pixels, 2 categories, 1000 stimuli). The first 700 stimuli were presented in fixed order across all seeds. Trial duration: 1000ms. Time block: 90ms. Warmup: 200ms.

### 2.4 Experimental Design

10 independent experiments were run with random seeds 42-51. Each seed initializes different random synaptic weights while maintaining identical circuit architecture and stimulus presentation order. Each experiment comprised 700 learning trials.

### 2.5 Analysis

**Error clustering ratio**: For each seed, we count consecutive error pairs (trial t incorrect AND trial t+1 incorrect) and divide by the expected count under independence (N_errors^2 / N_trials). Ratio > 1.0 indicates error clustering beyond chance.

**Category asymmetry**: Error rates for Category 1 vs Category 2 in the stable learning phase (trials 400-700).

**Clustering onset**: Sliding 50-trial window (step 25) to identify the first window where clustering ratio exceeds 1.0.

### 2.6 Hardware

Apple M4 Max (48GB). Julia 1.12.5, Neuroblox 0.8.0. Total computation time: ~170 minutes for 10 seeds (including JIT compilation).

## 3. Results

### 3.1 Learning Performance

All 10 seeds achieved successful category learning. Mean accuracy: 77.7% (range: 66.3-86.6%). Learning onset (first 50-trial window exceeding 70%) varied from trial 10 to trial 150.

### 3.2 Error Clustering (Incongruent Activity Pattern)

9 of 10 seeds showed error clustering ratios exceeding 1.0 (mean: 1.21x, range: 0.94-1.52x). Only seed 46 showed a ratio below 1.0 (0.94x). This demonstrates that the tendency for errors to cluster (once the circuit makes a mistake, it is more likely to make another on the next trial) is a robust property of the circuit architecture.

| Seed | Accuracy | Clustering Ratio |
|------|----------|-----------------|
| 42 | 76.9% | 1.52x |
| 43 | 70.6% | 1.11x |
| 44 | 66.3% | 1.04x |
| 45 | 78.9% | 1.28x |
| 46 | 79.0% | 0.94x |
| 47 | 79.3% | 1.33x |
| 48 | 81.3% | 1.10x |
| 49 | 79.6% | 1.10x |
| 50 | 78.6% | 1.31x |
| 51 | 86.6% | 1.43x |

### 3.3 Clustering Onset

Error clustering onset occurred at a mean of trial 140 (+/- 53), consistently after the initial learning phase. This timing corresponds to the transition from exploratory behavior (near-chance accuracy) to stable categorization, suggesting that incongruent activity patterns emerge as a byproduct of the circuit settling into categorical representations.

### 3.4 Category Asymmetry

All 10 seeds showed higher error rates for Category 2 than Category 1 (Cat1: 2.1-11.0%, Cat2: 7.7-48.1% in stable phase). Since stimulus presentation order was identical across seeds, this asymmetry reflects structural properties of the stimulus set rather than initial weight variation. This is consistent with Pathak et al.'s observation that sparse initial connectivity creates anatomical pre-weighting toward specific categories (Supplementary Figure S10).

### 3.5 Dopamine Prediction

DA values before errors vs before correct trials showed inconsistent directionality across seeds (4/10 showing the predicted pattern of lower DA preceding errors). This suggests that trial-level dopamine is not a reliable predictor of next-trial errors, and that the error clustering phenomenon is better explained by internal circuit state dynamics than by dopamine signaling.

## 4. Discussion

Our results provide the first multi-seed replication of emergent incongruent activity patterns in a biomimetic corticostriatal circuit. The original Pathak et al. (2026) study validated the model against macaque experimental data but did not examine robustness across initial conditions. We show that 9 of 10 random seeds produce error clustering above chance, with a consistent onset timing around trial 140.

The consistency of clustering onset timing is notable. It suggests a characteristic transition point in the learning dynamics: once the circuit has formed sufficiently strong categorical representations (reflected in rising accuracy), the competitive dynamics between WTA populations begin producing persistent conflict states. This is analogous to the phenomenon described in the original paper, where incongruent neurons emerge not as noise but as a functional signal reflecting the circuit's ongoing uncertainty.

The universal Category 2 disadvantage across all seeds, combined with identical stimulus sequences, indicates that the specific pixel patterns of the stimulus set create an inherent difficulty gradient. Future work should examine whether randomizing stimulus order across seeds produces seed-dependent category asymmetry (Jeong-type symmetry-breaking) rather than stimulus-dependent asymmetry.

### Limitations

- The error clustering measure is indirect; direct measurement of Matrisome rho values at decision time would provide a more precise characterization of incongruent activity.
- The stimulus set is small and fixed-order; generalization to larger, randomized stimulus sets is needed.
- N=10 seeds provides initial evidence but larger-scale replication would strengthen statistical claims.
- We used the small circuit configuration; the full Picower circuit with basal ganglia pathways may show different dynamics.

## 5. Conclusion

Incongruent activity patterns in biomimetic corticostriatal circuits are robust to initial condition variation. Error clustering emerges in 9 of 10 independent random seeds, with consistent onset timing around trial 140. This replication, performed on consumer hardware using the open-source Neuroblox framework, confirms that the phenomenon reported by Pathak et al. (2026) is an architectural property of corticostriatal circuits rather than an artifact of specific weight initializations.

## References

- Pathak, A., Brincat, S.L., Organtzidis, H. et al. Biomimetic model of corticostriatal micro-assemblies discovers a neural code. Nature Communications (2026). https://doi.org/10.1038/s41467-025-67076-x
- Gan, Y., & Isola, P. Neural Thickets: Diverse Task Experts Are Dense Around Pretrained Weights. arXiv:2603.12228 (2026).
- Jeong, H. et al. A miniature brain transformer with thalamic gating. arXiv:2603.07217 (2026).

## Data Availability

All data and code are available at: https://github.com/tsubasa-rsrch/research-papers/tree/main/papers/paper7-neuroblox-replication

## Acknowledgments

K. Yasukawa for experimental design guidance, Picower Institute for open-source Neuroblox framework, and the Hogwarts-inspired naming convention for neural circuit components.
