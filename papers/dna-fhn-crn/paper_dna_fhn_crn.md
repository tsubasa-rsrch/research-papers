# Negative Feedback Stabilizes Chemical Implementations of Neural Oscillators: QSSA vs Quadratization for FitzHugh-Nagumo in Bimolecular Chemical Reaction Networks

**Tsubasa** and K. Yasukawa

Draft v2.1 (2026-04-02)

## Abstract

Chemical reaction networks (CRNs) can implement arbitrary ordinary differential equations through established compilation pipelines. However, not all mathematically equivalent CRN implementations are equally suitable for physical realization. We present, to our knowledge, the first systematic mapping of the FitzHugh-Nagumo (FHN) neuron model to bimolecular CRNs via the ODE-to-CRN compilation pipeline and demonstrate that the choice of intermediate variable strategy critically determines numerical stability. The standard quadratization pipeline (Hemery, Fages, Soliman 2021), while theoretically correct, introduces self-catalytic terms that amplify numerical errors exponentially in oscillatory systems (error growth from 1e-10 at t=10 to 4310 at t=200, independent of solver precision). In contrast, a quasi-steady-state approximation (QSSA) intermediate species approach achieves up to 1777x lower trajectory error (v_RMSE vs FHN reference, at k_fast = 5000), because negative feedback in the QSSA formulation actively suppresses perturbations. The QSSA route also maintains 6800x better preservation of the v^2 algebraic constraint (a distinct metric measuring internal consistency rather than trajectory fidelity). This finding establishes a design guideline for molecular implementations of neural dynamics: negative feedback intermediates should be preferred over positive feedback (self-catalytic) intermediates when implementing oscillatory neuron models as CRNs.

## 1. Introduction

The compilation of ordinary differential equations (ODEs) into chemical reaction networks is a well-established theoretical framework (Fages et al. 2017, Hemery et al. 2021). The pipeline consists of four steps: polynomialization of non-polynomial terms, quadratization to reduce polynomial degree to at most 2, dual-rail encoding to ensure non-negativity, and direct translation to bimolecular reactions via mass-action kinetics.

This pipeline has been proven Turing-complete (Fages et al. 2017) and applied to various mathematical functions. However, its application to neuroscience-relevant oscillatory systems has not been explored. DNA-based spiking neurons have been demonstrated experimentally (Lobato-Dauzier et al. 2024), and spiking neuron CRNs with Hebbian learning have been designed for DNA strand displacement (Fil et al. 2022). However, to our knowledge, no prior work has applied the systematic ODE-to-CRN compilation pipeline (polynomialization-quadratization-dual-rail) to neuron models. A search of arXiv, PubMed, and Google Scholar for "FitzHugh-Nagumo chemical reaction network", "Hodgkin-Huxley DNA computing", "neural oscillator CRN", and "excitable chemical reaction network" returned no such reports (search conducted April 2026). This gap is significant because neuron models are the foundation of biological computation, and DNA-based neural networks have demonstrated capabilities including winner-take-all competition (Cherry and Qian 2018), convolutional networks (Xiong et al. 2022), and PDE solving (Xiao et al. 2025, Advanced Science).

Natural excitable CRNs such as the Belousov-Zhabotinsky reaction exhibit FHN-like dynamics; our contribution is the systematic compilation of FHN from the ODE via the standard pipeline, rather than designing an excitable CRN de novo. The missing piece in synthetic CRN design is spiking neuron dynamics: threshold behavior, refractory periods, and sustained oscillation. These are captured by the Hodgkin-Huxley (HH) model and its simplification, the FitzHugh-Nagumo (FHN) model. Implementing FHN as a CRN would bridge computational neuroscience and molecular programming, enabling DNA-based neural circuits with biologically faithful dynamics.

We attempt this mapping via two routes and discover that the standard quadratization approach, while mathematically valid, is numerically unstable for oscillatory systems. We propose QSSA-based intermediates as a stable alternative and provide quantitative comparison.

## 2. Methods

### 2.1 FitzHugh-Nagumo Model

The FitzHugh-Nagumo model (FitzHugh 1961; Nagumo et al. 1962) in the oscillatory regime:

    dv/dt = v - v^3/3 - w + I
    dw/dt = epsilon * (v + a - b*w)

Parameters: a=0.7, b=0.8, epsilon=0.08, I=0.5. These parameters place the system in the oscillatory regime (I = 0.5 exceeds the Hopf bifurcation threshold for these a, b values; see Izhikevich 2007, Chapter 4 for the bifurcation analysis of FHN).

### 2.2 Route A: Quadratization Pipeline

Following Hemery, Fages, Soliman (2021), FHN is already polynomial (cubic), so polynomialization is skipped. Introduce q = v^2 to reduce to degree 2 (optimal monomial quadratization; Bychkov and Pogudin 2021):

    dv/dt = v - qv/3 - w + I
    dw/dt = epsilon * (v + a - b*w)
    dq/dt = 2q - 2q^2/3 - 2vw + 2vI

The invariant q(t) = v(t)^2 is maintained if q(0) = v(0)^2. Dual-rail encoding (v = v+ - v-, etc.) yields 6 non-negative variables with 28 bimolecular reactions.

### 2.3 Route B: QSSA Intermediate Species

Instead of introducing q as an ODE variable, we use three intermediate species that track products of dual-rail variables via fast equilibration:

    dP_pp/dt = k_fast * (v+ * v+ - P_pp)
    dP_mm/dt = k_fast * (v- * v- - P_mm)
    dP_pm/dt = k_fast * (v+ * v- - P_pm)

where P_pp tracks v+^2, P_mm tracks v-^2, and P_pm tracks v+*v-. The cubic suppression term -v^3/3 is reconstructed via a factorization approach: -v^3/3 = -v * v^2 / 3 = -(v+ - v-)(P_pp - 2*P_pm + P_mm)/3. Expanding:

    -(v+*P_pp - 2*v+*P_pm + v+*P_mm - v-*P_pp + 2*v-*P_pm - v-*P_mm)/3

The six terms are distributed to dv+/dt and dv-/dt as follows:

| Term | Value | Contributes to |
|------|-------|----------------|
| -v+*P_pp/3 | negative | dv-/dt (R9: v+*P_pp -> v-) |
| +2*v+*P_pm/3 | positive | dv+/dt (R3: v+*P_pm -> v+) |
| -v+*P_mm/3 | negative | dv-/dt (R11: v+*P_mm -> v-) |
| +v-*P_pp/3 | positive | dv+/dt (R2: v-*P_pp -> v+) |
| -2*v-*P_pm/3 | negative | dv-/dt (R10: v-*P_pm -> v-) |
| +v-*P_mm/3 | positive | dv+/dt (R4: v-*P_mm -> v+) |

Thus: cubic_to_vp = (v-*P_pp + 2*v+*P_pm + v-*P_mm)/3 and cubic_to_vm = (v+*P_pp + 2*v-*P_pm + v+*P_mm)/3, matching Appendix A reactions R2-R4 and R9-R11 respectively. This decomposition was verified symbolically (SymPy: cubic_to_vp - cubic_to_vm = -(v+ - v-)^3/3, difference = 0; see Section 2.4).

This yields 7 non-negative variables (v+, v-, w+, w-, P_pp, P_mm, P_pm) and 24 bimolecular reactions (Appendix A).

Note that Route A provides an exact algebraic lifting (q = v^2 is an invariant of the ODE), while Route B is a finite-k_fast approximation (P tracks v^2 with lag proportional to 1/k_fast). Despite Route A's theoretical exactness, the self-catalytic structure dq/dt = 2q + ... creates positive feedback on errors, while Route B's dP/dt = k_fast*(v^2 - P) provides negative feedback that actively corrects perturbations.

### 2.4 Numerical Verification

Three-layer comparison using Julia/OrdinaryDiffEq with Rodas5P (stiff solver):
1. FHN reference (2 variables)
2. Route A: Quadratized + dual-rail CRN (6 variables)
3. Route B: QSSA + dual-rail CRN (7 variables)

Initial conditions: v(0) = -1.0, w(0) = -0.5. Dual-rail encoding: v+(0) = 0, v-(0) = 1.0, w+(0) = 0, w-(0) = 0.5. Route A: q+(0) = v-(0)^2 = 1.0, q-(0) = 0. Route B: P_pp(0) = v+(0)^2 = 0, P_mm(0) = v-(0)^2 = 1.0, P_pm(0) = v+(0)*v-(0) = 0. Integration: t in [0, 300], reltol = 1e-8, abstol = 1e-10 (unless stated otherwise), saveat = 0.01s. Implementation: Julia v1.12.5, OrdinaryDiffEq v6.108.0, solver Rodas5P. Code available at [DOI to be assigned upon Zenodo release].

Metrics: (1) v_RMSE = root-mean-square error of v(t) vs FHN reference (trajectory fidelity), (2) q_err or P_err = RMS of (q - v^2) or (P_pp + P_mm - 2*P_pm - v^2) (algebraic invariant preservation), (3) dual-rail drift = mean of min(v+, v-) (annihilation effectiveness). All metrics computed over t > 50 to exclude transients. The mathematical equivalence of the CRN decomposition to FHN was verified symbolically: at QSSA equilibrium (P_pp = v+^2, P_mm = v-^2, P_pm = v+*v-), the net cubic contribution cubic_to_vp - cubic_to_vm simplifies to -(v+ - v-)^3/3, which equals -v^3/3 (verified via SymPy, difference = 0).

## 3. Results

### 3.1 Quadratization Instability (Negative Result)

The quadratized system exhibits exponential error growth in the q = v^2 invariant:

| Time (s) | abstol   | q - v^2 error |
|----------|----------|---------------|
| 10       | 1e-10    | 1.3e-10       |
| 10       | 1e-14    | 4.4e-12       |
| 200      | 1e-10    | 2.80          |
| 200      | 1e-14    | 4310          |

Note that at t=200, higher precision (abstol=1e-14) produces larger error than lower precision (abstol=1e-10). This is because the higher-precision solver more faithfully tracks the self-catalytic divergence, while the lower-precision solver's coarser adaptive step size may interact differently with the nonlinear dynamics (a detailed step-size analysis is beyond our current scope). Both cases confirm structural instability: increasing solver precision does not resolve the instability, and at t=200 both precision levels produce errors many orders of magnitude larger than acceptable.

The CRN dual-rail implementation inherits this instability: v_RMSE ≈ 1.33-1.37 across all tested k_ann values (10-1000). Note: the q-v^2 error of 2.80 in Table 1 (dual-rail CRN) differs from the 2.91 reported in Section 3.3 (standalone quadratized system) because dual-rail encoding and annihilation reactions introduce additional perturbations.

### 3.2 QSSA Stability (Positive Result)

The QSSA route shows bounded error and monotonic improvement with k_fast (k_ann = 100 fixed throughout):

| k_fast | v_RMSE   | P_err    | Improvement vs Quad |
|--------|----------|----------|---------------------|
| 10     | 0.370    | 4.6e-02  | 3.6x               |
| 100    | 0.037    | 4.1e-03  | 36x                 |
| 1000   | 0.004    | 4.1e-04  | 356x                |
| 5000   | 0.000749 | 8.2e-05  | 1777x               |

At k_fast = 1000, P_err = 4.1e-04 vs q_err = 2.80 (6800x difference). Dual-rail drift (mean of min(v+, v-)) decreases monotonically from 0.15 (k_ann=10) to 0.001 (k_ann=1000), confirming effective annihilation. The QSSA formulation actively suppresses perturbations.

The QSSA advantage is robust across FHN parameter regimes (k_fast = 1000, k_ann = 100):

| I   | Regime      | QSSA v_RMSE | Quad v_RMSE |
|-----|-------------|-------------|-------------|
| 0.2 | excitable   | 0.000001    | 0.558       |
| 0.5 | oscillatory | 0.004       | 1.363       |
| 1.0 | strong osc. | 0.004       | 1.495       |

QSSA tracking error scales as O(1/k_fast), consistent with Tikhonov singular perturbation theory (Tikhonov 1952; Fenichel 1979). A log-log regression of v_RMSE vs k_fast over 9 data points (k_fast = 10 to 5000) yields slope = -0.9991 (see Figure 2), confirming that Route B provides a controlled approximation with predictable error bounds.

### 3.2b Period and Amplitude Fidelity

Route A's spurious attractor produces qualitatively different dynamics from FHN:

| Metric         | FHN reference | Route A (Quad) | Route B (QSSA) |
|----------------|---------------|----------------|----------------|
| Period (s)     | 39.474        | 22.70          | 39.471         |
| Peak amplitude | 1.852         | -0.262         | 1.852          |
| Period error   | --            | -42.5%         | -0.008%        |
| Amplitude error| --            | -114%          | +0.005%        |

Route A's period is 42% shorter and peak amplitude is **negative**, indicating complete loss of the FHN firing dynamics. The system has settled onto a spurious limit cycle unrelated to the original neuron model. Route B preserves both period (error 0.008%) and amplitude (error 0.005%) to within measurement precision.

### 3.3 Subcritical Instability in Quadratization (Mechanistic Analysis)

Linearizing the error dynamics e = q - v^2 yields de/dt = (2 - 4v^2/3) * e along the FHN limit cycle. The period-averaged growth rate (Floquet exponent) is -0.54, indicating **linear stability**. Yet all simulations show divergence, even from initial perturbations as small as e(0) = 1e-10.

This apparent contradiction is resolved by a **ratchet mechanism**: during recovery phases of the limit cycle where v^2 < 1.5, the local growth rate is positive and errors grow. The grown errors enter the nonlinear regime where the subsequent decay phase cannot fully restore them. Each oscillation cycle ratchets the error upward until nonlinear saturation. Simulations confirm this: all initial perturbation magnitudes (e(0) = 1e-10 to 1.0) converge to the same final error of 2.91 by t=200, indicating that the invariant manifold q = v^2 has an **effective basin of attraction of zero**. The convergence to a common final error (2.91) suggests the quadratized system possesses a spurious attractor distinct from the FHN limit cycle, visible as the inward spiral in Figure 1 (Route A, red dashed).

A rigorous nonlinear Floquet analysis of the invariant manifold stability is beyond the scope of this work; we present the ratchet mechanism as a qualitative explanation consistent with all numerical observations (convergence of all initial perturbation magnitudes to a common final error of 2.91). Crucially, this failure mode is invisible to existing linear stability analyses. Cai and Pogudin (2024) preserve dissipativity (linear stability at equilibria), but the FHN limit cycle's nonlinear invariant is outside their framework's scope.

### 3.4 Design Principle

- **Route A (Quadratization)**: Invariant manifold q = v^2 is linearly stable (Floquet avg = -0.54) but has zero-radius nonlinear attraction basin. Any finite perturbation diverges via ratchet mechanism.
- **Route B (QSSA)**: dP/dt = k_fast*(v^2 - P) provides negative feedback with effectively infinite attraction basin. Perturbations of any size are corrected at rate k_fast.

Both routes realize the same mathematical transformation. The CRN structure, not the mathematical equivalence, determines stability. This parallels findings in computational neuroscience where connection topology, not component identity, determines circuit function (Tsubasa 2026a, 2026b; Marder and Taylor 2011).

## 4. Discussion

### 4.1 Implications for Molecular Programming

The quadratization pipeline (Hemery et al. 2021) is theoretically complete and practically effective for non-oscillatory systems. Our results show that oscillatory systems require additional design considerations. We recommend QSSA-based intermediates for any CRN implementation of sustained oscillators.

Cai and Pogudin (2024) addressed the stability issue within the quadratization framework by proving existence of dissipativity-preserving transformations. Our approach is complementary: rather than seeking stable quadratizations, we bypass quadratization entirely and use QSSA intermediates with intrinsic negative feedback. The two approaches are not mutually exclusive and may be combined in future work -- for instance, dissipative quadratization could handle the polynomialization stage of full HH models while QSSA intermediates handle the high-order terms.

### 4.2 Connection to DNA Neural Computing

DNA strand displacement can physically realize arbitrary CRNs (Soloveichik et al. 2010), and this technology has enabled WTA competition (Cherry and Qian 2018) and spiking neurons (Lobato-Dauzier et al. 2024) on DNA. Our FHN-to-CRN mapping via the systematic compilation pipeline provides a complementary route to spiking dynamics. Combined with existing WTA circuits, this enables DNA circuits with both competitive selection and excitable/oscillatory dynamics, two key computational primitives of biological neural circuits.

### 4.3 Wiring Determines Function

The finding that two mathematically equivalent CRN implementations produce qualitatively different behavior echoes a broader principle: topology determines function, independent of substrate. The same ODE, implemented with different reaction network topologies, yields stable or unstable dynamics. This is analogous to how the same excitatory neurons produce enhancement or catastrophic interference depending on whether they connect through relay (gate) or directly to cortex (Tsubasa 2026a, 2026b).

### 4.4 Limitations

- FHN is a 2-variable simplification. Full HH requires polynomialization of exponential gating functions.
- QSSA assumes fast intermediate equilibration. Physical DNA reaction rates may limit achievable k_fast.
- Numerical verification only; no wet-lab implementation.
- Deterministic mass-action kinetics assumed. At low molecular counts relevant to DNA strand displacement, stochastic effects may dominate. In particular, QSSA intermediate species require sufficient molecular counts to achieve fast equilibration; whether the negative feedback stability advantage persists in the stochastic regime is an open question. Gillespie simulation of the CRN at realistic molecular counts (N = 100-10000) is a necessary future step before physical implementation. The negative feedback structure of QSSA (dP/dt = k_fast*(v^2 - P)) is expected to provide noise rejection even in the stochastic regime, as perturbations are actively corrected. However, whether the correction rate k_fast can exceed stochastic fluctuation rates at realistic molecular counts remains to be determined.

## Figure Captions

**Figure 1.** Phase space trajectories of FHN reference (gray dashed), Route A quadratization CRN (red dashed), and Route B QSSA CRN (blue solid). Route B overlaps almost perfectly with the FHN reference, while Route A spirals inward to a spurious attractor with period 22.7s (vs FHN 39.5s) and negative peak amplitude (-0.26 vs FHN +1.85). Inset: magnified view of the upper-right portion of the limit cycle showing the small deviation between FHN and Route B (v_RMSE = 0.004 at k_fast = 1000).

**Figure 2.** QSSA convergence: v_RMSE vs k_fast on log-log axes. Data points (blue circles) follow the Tikhonov O(1/k_fast) theoretical prediction (red dashed line) with slope = -0.9991, confirming that Route B provides a controlled approximation with predictable error bounds.

## 5. Conclusion

We present, to our knowledge, the first systematic mapping of the FitzHugh-Nagumo neuron model to bimolecular chemical reaction networks via the ODE-to-CRN compilation pipeline and demonstrate that feedback structure in intermediate species critically determines implementation stability. QSSA-based negative feedback intermediates outperform quadratization-based positive feedback by 1777x in trajectory fidelity (v_RMSE) and 6800x in algebraic invariant preservation (a distinct internal consistency metric). This establishes a design guideline for molecular implementations of biological oscillators and takes a step toward DNA-based neural circuits with biologically faithful spiking dynamics.

## References

- Cherry, K. M. and Qian, L. (2018). Scaling up molecular pattern recognition with DNA-based winner-take-all neural networks. Nature, 559, 370-376.
- Fages, F., Le Guludec, G., Bournez, O., and Pouly, A. (2017). Strong Turing Completeness of Continuous Chemical Reaction Networks. CMSB 2017, LNCS 10545.
- Hemery, M., Fages, F., and Soliman, S. (2021). Compiling Elementary Mathematical Functions into Finite Chemical Reaction Networks via a Polynomialization Algorithm for ODEs. CMSB 2021, LNCS 12881.
- Bychkov, A. and Pogudin, G. (2021). Optimal Monomial Quadratization for ODE Systems. IWOCA 2021.
- Cai, Y. and Pogudin, G. (2024). Dissipative Quadratizations of Polynomial ODE Systems. TACAS 2024.
- Xiong, X. et al. (2022). Molecular convolutional neural networks with DNA regulatory circuits. Nature Machine Intelligence, 4, 625-635.
- Xiao, S. et al. (2025). DNA-based molecular neural network biocomputing circuits for solving PDEs. Advanced Science.
- Fenichel, N. (1979). Geometric singular perturbation theory for ordinary differential equations. Journal of Differential Equations, 31(1), 53-98.
- Fil, J., Dalchau, N., and Chu, D. (2022). Programming Molecular Systems To Emulate a Learning Spiking Neuron. ACS Synthetic Biology, 11(6), 2055-2069.
- FitzHugh, R. (1961). Impulses and physiological states in theoretical models of nerve membrane. Biophysical Journal, 1(6), 445-466.
- Izhikevich, E. M. (2007). Dynamical Systems in Neuroscience. MIT Press.
- Nagumo, J., Arimoto, S., and Yoshizawa, S. (1962). An active pulse transmission line simulating nerve axon. Proceedings of the IRE, 50(10), 2061-2070.
- Lobato-Dauzier, N. et al. (2024). Neural coding of temperature with a DNA-based spiking chemical neuron. Nature Chemical Engineering, 1(8), 510-521.
- Marder, E. and Taylor, A. L. (2011). Multiple models to capture the variability in biological neurons and networks. Nature Neuroscience, 14(2), 133-138.
- Tikhonov, A. N. (1952). Systems of differential equations containing small parameters in the derivatives. Matematicheskii Sbornik, 73(3), 575-586.
- Soloveichik, D., Seelig, G., and Winfree, E. (2010). DNA as a universal substrate for chemical kinetics. PNAS, 107(12), 5393-5398.
- Tsubasa (2026a). Ascending thalamic input is a computational prerequisite for learning improvement in biomimetic circuits. Zenodo. DOI: 10.5281/zenodo.18968887.
- Tsubasa (2026b). Thalamic gate with sham relay control. Zenodo. DOI: 10.5281/zenodo.19132003.

## Appendix A: Complete QSSA CRN Reaction List

Chemical species: {v+, v-, w+, w-, P_pp, P_mm, P_pm} + external supply S (concentration I).

### QSSA intermediate species dynamics (fast reactions, rate k_fast)

    P1: v+ + v+  ->[k_fast]  v+ + v+ + P_pp    (P_pp production)
    P2: P_pp     ->[k_fast]  null               (P_pp decay)
    P3: v- + v-  ->[k_fast]  v- + v- + P_mm    (P_mm production)
    P4: P_mm     ->[k_fast]  null               (P_mm decay)
    P5: v+ + v-  ->[k_fast]  v+ + v- + P_pm    (P_pm production)
    P6: P_pm     ->[k_fast]  null               (P_pm decay)

Net effect at QSSA: P_pp ~ v+^2, P_mm ~ v-^2, P_pm ~ v+*v-

### v+ reactions (from dv/dt = v - v^3/3 - w + I)

    R1:  v+       ->[1]      2*v+               (autocatalytic, +v term)
    R2:  v- + P_pp ->[1/3]   v- + P_pp + v+     (cubic suppression)
    R3:  v+ + P_pm ->[2/3]   v+ + P_pm + v+     (cubic suppression)
    R4:  v- + P_mm ->[1/3]   v- + P_mm + v+     (cubic suppression)
    R5:  w-       ->[1]      w- + v+             (-w term, positive part)
    R6:  null     ->[I]      v+                  (external input)
    R7:  v+ + v-  ->[k_ann]  null                (annihilation)

### v- reactions

    R8:  v-       ->[1]      2*v-               (autocatalytic, +v term)
    R9:  v+ + P_pp ->[1/3]   v+ + P_pp + v-     (cubic suppression)
    R10: v- + P_pm ->[2/3]   v- + P_pm + v-     (cubic suppression)
    R11: v+ + P_mm ->[1/3]   v+ + P_mm + v-     (cubic suppression)
    R12: w+       ->[1]      w+ + v-             (-w term, negative part)

### w+ reactions (from dw/dt = epsilon*(v + a - b*w))

    R13: v+       ->[eps]    v+ + w+             (excitation)
    R14: null     ->[eps*a]  w+                  (constant drive)
    R15: w-       ->[eps*b]  w- + w+             (recovery)
    R16: w+ + w-  ->[k_ann]  null                (annihilation)

### w- reactions

    R17: v-       ->[eps]    v- + w-             (excitation)
    R18: w+       ->[eps*b]  w+ + w-             (recovery)

Total: 6 QSSA reactions + 18 main reactions = 24 reactions.
7 chemical species + 1 external supply.
All reactions are unimolecular or bimolecular (mass-action compatible).

## Appendix B: Route A (Quadratization) CRN Reaction List

Chemical species: {v+, v-, w+, w-, q+, q-} + external supply S (concentration I).
Following Hemery, Fages, Soliman (2021) pipeline with q = v^2 quadratization and dual-rail encoding.

### v+ reactions
    R1:  v+       ->[1]      2*v+               (autocatalytic)
    R2:  q+ + v-  ->[1/3]    q+ + v- + v+       (cubic suppression)
    R3:  q- + v+  ->[1/3]    q- + 2*v+          (cubic suppression)
    R4:  w-       ->[1]      w- + v+             (-w positive part)
    R5:  null     ->[I]      v+                  (external input)
    R6:  v+ + v-  ->[k_ann]  null                (annihilation)

### v- reactions
    R7:  v-       ->[1]      2*v-               (autocatalytic)
    R8:  q+ + v+  ->[1/3]    q+ + v+ + v-       (cubic suppression)
    R9:  q- + v-  ->[1/3]    q- + 2*v-          (cubic suppression)
    R10: w+       ->[1]      w+ + v-             (-w negative part)

### w+/w- reactions
    R11-R16: identical to Route B reactions R13-R18 (w+/w- dynamics).

### q+ reactions
    R17: q+       ->[2]      2*q+               (autocatalytic — source of instability)
    R18: q+ + q-  ->[4/3]    q+ + q- + q+       (quadratic suppression)
    R19: v+ + w-  ->[2]      v+ + w- + q+       (vw coupling)
    R20: v- + w+  ->[2]      v- + w+ + q+       (vw coupling)
    R21: v+       ->[2I]     v+ + q+             (input coupling)
    R22: q+ + q-  ->[k_ann]  null                (annihilation)

### q- reactions
    R23: q-       ->[2]      2*q-               (autocatalytic — source of instability)
    R24: q+ + q+  ->[2/3]    2*q+ + q-          (quadratic suppression)
    R25: q- + q-  ->[2/3]    3*q-               (quadratic suppression)
    R26: v+ + w+  ->[2]      v+ + w+ + q-       (vw coupling)
    R27: v- + w-  ->[2]      v- + w- + q-       (vw coupling)
    R28: v-       ->[2I]     v- + q-             (input coupling)

Total: 28 reactions. 6 chemical species + 1 external supply.
Note: R17 and R23 (q+ -> 2q+, q- -> 2q-) are the self-catalytic reactions responsible for the exponential error amplification documented in Section 3.1.
