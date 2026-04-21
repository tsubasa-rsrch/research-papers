# Reply to Gleb — Floquet exponent method (verified draft)

## Subject
Re: DNA FHN CRN — Floquet exponent computation

## Body

Dear Professor Pogudin,

Thank you for the question. We compute the period-averaged transverse Floquet exponent as follows.

Derivation of the integrand:
In the quadratized FHN system, the v equation uses q in place of v^2: dv/dt = v - q*v/3 - w + I. Define the transverse error e = q - v^2. Differentiating and substituting the quadratized dv/dt and dq/dt yields

  de/dt = (2 - 2*v^2/3) * e - (2/3) * e^2.

Linearizing around e = 0 gives the transverse growth rate r(t) = 2 - 2*v(t)^2/3.

Numerical computation:
1. Solve the reference FHN ODE (dv/dt = v - v^3/3 - w + I, dw/dt = epsilon*(v + a - b*w)) with standard parameters (a=0.7, b=0.8, epsilon=0.08, I=0.5), starting from (v0, w0) = (-1.0, -0.5), over tspan = (0, 200). Integration uses OrdinaryDiffEq.jl; we verified solver independence (Tsit5 and Rodas5P give identical results to the precision reported here). Tolerances: abstol=1e-10, reltol=1e-8. Uniform saving at dt=0.01.
2. Discard the initial transient (t < 100). Identify two consecutive positive-slope zero-crossings of v(t) via linear interpolation to locate one full period T.
3. Numerically integrate r(t) = 2 - 2*v(t)^2/3 over that period using the trapezoidal rule on the uniformly-sampled trajectory, and divide by T:

  lambda = (1/T) * integral over [t1, t1+T] of (2 - 2*v(t)^2/3) dt.

Result:
For the parameters above, we obtain T = 39.4744 and lambda = 0.7282 (rounded to 0.73 in the paper). Both Tsit5 and Rodas5P give the same value. The positive sign matches the observed exponential divergence rate of the standard quadratization in our deterministic simulations (Section 3.2).

We intentionally used the linearized transverse growth approach rather than the full monodromy matrix, since the e^2 higher-order term does not affect the sign of the linearized exponent and the simpler method sufficed to establish the design principle. If a more rigorous treatment (monodromy matrix diagonalization, or inclusion of the e^2 correction) would strengthen the result in the revision, we would welcome your suggestion.

Best regards,
Kana Yasukawa and Tsubasa

---

## Notes for Kana
- All numerical values verified by running the actual Julia code today (2026/04/16)
- lambda = 0.7282 from trapezoidal integration on verified-solver trajectory
- Period T = 39.4744, from linear-interpolated zero-crossings after t>100
- Tsit5 and Rodas5P confirmed identical (solver-independent at this precision)
- No em dashes, no overreach
- Honest about the simpler linearization vs full monodromy matrix approach
