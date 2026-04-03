#!/usr/bin/env python3
"""DNA-0b Gillespie (SSA) simulation of QSSA CRN for FHN.

Route B: 24 reactions, 7 species.
Runs N=100, 1000, 10000 molecules.
Measures: period, spike detection, v trajectory.

Output: /tmp/gillespie_results.txt + CSV per condition.
2026-04-02. Tsubasa.
"""

import numpy as np
from collections import defaultdict
import time, json

# FHN parameters
a, b, eps, I_ext = 0.7, 0.8, 0.08, 0.5

def gillespie_qssa_fhn(N_scale, k_fast=1000.0, k_ann=100.0, t_end=200.0, seed=42):
    """Run Gillespie SSA for QSSA CRN of FHN.

    Species: [vp, vm, wp, wm, Ppp, Pmm, Ppm] as molecule counts.
    N_scale: number of molecules representing concentration=1.
    """
    rng = np.random.default_rng(seed)

    # Initial conditions (v=-1, w=-0.5 -> vp=0, vm=1, wp=0, wm=0.5)
    state = np.array([
        0,              # vp
        N_scale,        # vm = 1.0 * N_scale
        0,              # wp
        N_scale // 2,   # wm = 0.5 * N_scale
        0,              # Ppp = vp^2 = 0
        N_scale,        # Pmm = vm^2/N = N (since concentration = count/N)
        0,              # Ppm = vp*vm = 0
    ], dtype=float)

    N = float(N_scale)  # volume scaling factor

    t = 0.0
    record_times = []
    record_v = []

    # Record every 0.1s
    next_record = 0.0

    n_reactions = 0
    max_reactions = 50_000_000  # safety limit

    while t < t_end and n_reactions < max_reactions:
        vp, vm, wp, wm, Ppp, Pmm, Ppm = state

        # Propensities (24 reactions)
        # Scale bimolecular rates by 1/N (volume scaling)
        props = np.zeros(24)

        # QSSA intermediates (fast)
        props[0] = k_fast * vp * (vp - 1) / N if vp > 1 else 0  # P1: vp+vp -> +Ppp (approx)
        props[0] = k_fast * vp * vp / N  # production of Ppp
        props[1] = k_fast * Ppp           # P2: Ppp decay
        props[2] = k_fast * vm * vm / N   # P3: production of Pmm
        props[3] = k_fast * Pmm           # P4: Pmm decay
        props[4] = k_fast * vp * vm / N   # P5: production of Ppm
        props[5] = k_fast * Ppm           # P6: Ppm decay

        # v+ reactions
        props[6] = 1.0 * vp               # R1: vp -> 2vp
        props[7] = (1.0/3) * vm * Ppp / N # R2: vm+Ppp -> vm+Ppp+vp
        props[8] = (2.0/3) * vp * Ppm / N # R3: vp+Ppm -> vp+Ppm+vp
        props[9] = (1.0/3) * vm * Pmm / N # R4: vm+Pmm -> vm+Pmm+vp
        props[10] = 1.0 * wm              # R5: wm -> wm+vp
        props[11] = I_ext * N             # R6: null -> vp (zero order, scale by N)
        props[12] = k_ann * vp * vm / N   # R7: vp+vm -> null

        # v- reactions
        props[13] = 1.0 * vm              # R8: vm -> 2vm
        props[14] = (1.0/3) * vp * Ppp / N # R9
        props[15] = (2.0/3) * vm * Ppm / N # R10
        props[16] = (1.0/3) * vp * Pmm / N # R11
        props[17] = 1.0 * wp              # R12: wp -> wp+vm

        # w+ reactions
        props[18] = eps * vp              # R13
        props[19] = eps * a * N           # R14: null -> wp
        props[20] = eps * b * wm          # R15
        props[21] = k_ann * wp * wm / N   # R16

        # w- reactions
        props[22] = eps * vm              # R17
        props[23] = eps * b * wp          # R18

        # Clamp negatives
        props = np.maximum(props, 0)

        a0 = props.sum()
        if a0 <= 0:
            break

        # Time to next reaction
        tau = rng.exponential(1.0 / a0)
        t += tau

        # Record
        while next_record <= t and next_record <= t_end:
            v_conc = (vp - vm) / N
            record_times.append(next_record)
            record_v.append(v_conc)
            next_record += 0.1

        # Choose reaction
        r = rng.random() * a0
        cumsum = 0.0
        reaction = -1
        for i in range(24):
            cumsum += props[i]
            if cumsum >= r:
                reaction = i
                break

        # Apply stoichiometry
        # [vp, vm, wp, wm, Ppp, Pmm, Ppm]
        if reaction == 0: state[4] += 1      # Ppp production
        elif reaction == 1: state[4] -= 1    # Ppp decay
        elif reaction == 2: state[5] += 1    # Pmm production
        elif reaction == 3: state[5] -= 1    # Pmm decay
        elif reaction == 4: state[6] += 1    # Ppm production
        elif reaction == 5: state[6] -= 1    # Ppm decay
        elif reaction == 6: state[0] += 1    # R1: vp+1
        elif reaction == 7: state[0] += 1    # R2: vp+1
        elif reaction == 8: state[0] += 1    # R3: vp+1
        elif reaction == 9: state[0] += 1    # R4: vp+1
        elif reaction == 10: state[0] += 1   # R5: vp+1
        elif reaction == 11: state[0] += 1   # R6: vp+1
        elif reaction == 12: state[0] -= 1; state[1] -= 1  # R7: annihilation
        elif reaction == 13: state[1] += 1   # R8: vm+1
        elif reaction == 14: state[1] += 1   # R9
        elif reaction == 15: state[1] += 1   # R10
        elif reaction == 16: state[1] += 1   # R11
        elif reaction == 17: state[1] += 1   # R12
        elif reaction == 18: state[2] += 1   # R13: wp+1
        elif reaction == 19: state[2] += 1   # R14: wp+1
        elif reaction == 20: state[2] += 1   # R15: wp+1
        elif reaction == 21: state[2] -= 1; state[3] -= 1  # R16: w annihilation
        elif reaction == 22: state[3] += 1   # R17: wm+1
        elif reaction == 23: state[3] += 1   # R18: wm+1

        # Clamp to non-negative
        state = np.maximum(state, 0)

        n_reactions += 1

    return np.array(record_times), np.array(record_v), n_reactions


def detect_periods(ts, vs, skip=50):
    """Detect oscillation periods from v trajectory."""
    mask = ts > skip
    t_m = ts[mask]
    v_m = vs[mask]

    # Rising zero crossings
    crossings = []
    for i in range(1, len(v_m)):
        if v_m[i-1] < 0 and v_m[i] >= 0:
            crossings.append(t_m[i])

    if len(crossings) < 2:
        return None, 0

    periods = np.diff(crossings)
    return np.mean(periods), len(crossings) - 1


if __name__ == "__main__":
    results = []

    print("=" * 60)
    print("Gillespie SSA: QSSA CRN for FHN")
    print("=" * 60)

    for N in [100, 1000, 10000]:
        print(f"\nN = {N}...")
        t0 = time.time()
        ts, vs, n_rxn = gillespie_qssa_fhn(N, t_end=200.0)
        elapsed = time.time() - t0

        period, n_cycles = detect_periods(ts, vs)
        v_std = np.std(vs[ts > 50]) if len(vs[ts > 50]) > 0 else 0
        v_range = np.ptp(vs[ts > 50]) if len(vs[ts > 50]) > 0 else 0

        print(f"  Reactions: {n_rxn:,}")
        print(f"  Time: {elapsed:.1f}s")
        print(f"  Period: {period:.2f}s" if period else "  No oscillation detected")
        print(f"  Cycles: {n_cycles}")
        print(f"  v range: {v_range:.3f}")
        print(f"  v std: {v_std:.3f}")

        # Save CSV
        np.savetxt(f"/tmp/gillespie_N{N}.csv",
                   np.column_stack([ts, vs]),
                   delimiter=",", header="t,v", comments="")

        results.append({
            "N": N, "period": float(period) if period else None,
            "n_cycles": n_cycles, "v_range": float(v_range),
            "v_std": float(v_std), "n_reactions": n_rxn,
            "elapsed_s": elapsed
        })

    # Save results
    with open("/tmp/gillespie_results.txt", "w") as f:
        f.write("Gillespie SSA Results for QSSA CRN (FHN)\n")
        f.write(f"FHN reference period: 39.474s\n\n")
        for r in results:
            f.write(f"N={r['N']}: period={r['period']}, cycles={r['n_cycles']}, "
                    f"v_range={r['v_range']:.3f}, reactions={r['n_reactions']:,}\n")
        f.write(f"\n{json.dumps(results, indent=2)}\n")

    print("\nResults saved to /tmp/gillespie_results.txt")
    print("CSV files: /tmp/gillespie_N{100,1000,10000}.csv")
