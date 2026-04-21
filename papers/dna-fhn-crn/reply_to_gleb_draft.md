# Reply to Prof Gleb — Draft (2026/04/15)

## Email draft

Dear Professor Gleb,

Thank you very much for your insightful suggestion. We tested the dissipative quadratization immediately.

### Result

Adding -kappa(q - v^2) with kappa = 3 to the third equation completely eliminates the q-v^2 drift:

| Model | q-v^2 max error | q-v^2 mean error | v RMSE vs FHN |
|-------|----------------|-----------------|---------------|
| Standard quadratization | 3.00 | 2.79 | 1.33 |
| Dissipative (kappa=3) | 5.3e-9 | 4.2e-10 | 0.0 |

The fix works perfectly: the invariant manifold q = v^2 becomes attracting rather than merely invariant.

### Theoretical connection to our Floquet analysis

In our paper (Section 3.4), we showed that the transverse Floquet exponent of the q = v^2 manifold is lambda = +0.73 (period-averaged over the FHN limit cycle). Your dissipative term modifies the error dynamics from

  de/dt = lambda * e  (unstable, lambda = +0.73)

to

  de/dt = (lambda - kappa) * e  (stable for kappa > 0.73)

With kappa = 3, the effective exponent is -2.27, making the manifold strongly attracting. Any kappa > 0.73 suffices for stability; kappa = 3 provides a comfortable margin.

### Next steps

1. **Dual-rail CRN translation**: We are working on translating -kappa(q - v^2) into bimolecular CRN reactions. In dual-rail encoding, this becomes reactions involving q+, q-, v+, v- species.

2. **Your generalization question**: "Can one find quadratizing variables but, instead of introducing them directly, create variables which will track them?" -- This is exactly what the dissipative term achieves. We believe this generalizes: for any quadratized system with unstable invariant manifold (positive transverse Floquet exponent), adding a dissipative tracking term -kappa(q - f(x)) where q = f(x) is the quadratizing relation should stabilize it, provided kappa exceeds the maximum transverse growth rate.

3. **Differential quadratic recast**: Thank you for the reference. We will study it and incorporate the connection.

We will update the paper with these results and share the revision.

Best regards,
Kana Yasukawa and Tsubasa

---

## Notes for Kana
- kappa > 0.73 is the theoretical minimum (our Floquet exponent)
- kappa = 3 gives 4x margin → robust
- The generalization question is really interesting: this could be a general method for stabilizing ANY quadratized oscillatory system
- The differential quadratic recast paper needs reading: https://www.sciencedirect.com/science/article/pii/S0020746224002592
- TODO: dual-rail CRN translation of the dissipative term
