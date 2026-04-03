#!/usr/bin/env python3
"""Gillespie SSA for QSSA CRN - N=100 only, with trajectory CSV + individual period SD.
Based on dna0b_gillespie.py v2 (k_fast/N scaling).
Purpose: Get cycle-to-cycle period SD for paper Section 3.5.
"""

import numpy as np
import time

a, b, eps, I_ext = 0.7, 0.8, 0.08, 0.5

def gillespie_qssa_fhn(N_scale, k_fast, k_ann=100.0, t_end=200.0, seed=42):
    rng = np.random.default_rng(seed)
    state = np.array([0, N_scale, 0, N_scale // 2, 0, N_scale, 0], dtype=float)
    N = float(N_scale)
    t = 0.0
    record_times, record_v = [], []
    next_record = 0.0
    n_reactions = 0
    max_reactions = 200_000_000  # increased from 50M

    while t < t_end and n_reactions < max_reactions:
        vp, vm, wp, wm, Ppp, Pmm, Ppm = state
        props = np.zeros(24)
        props[0] = k_fast * vp * vp / N
        props[1] = k_fast * Ppp
        props[2] = k_fast * vm * vm / N
        props[3] = k_fast * Pmm
        props[4] = k_fast * vp * vm / N
        props[5] = k_fast * Ppm
        props[6] = 1.0 * vp
        props[7] = (1.0/3) * vm * Ppp / N
        props[8] = (2.0/3) * vp * Ppm / N
        props[9] = (1.0/3) * vm * Pmm / N
        props[10] = 1.0 * wm
        props[11] = I_ext * N
        props[12] = k_ann * vp * vm / N
        props[13] = 1.0 * vm
        props[14] = (1.0/3) * vp * Ppp / N
        props[15] = (2.0/3) * vm * Ppm / N
        props[16] = (1.0/3) * vp * Pmm / N
        props[17] = 1.0 * wp
        props[18] = eps * vp
        props[19] = eps * a * N
        props[20] = eps * b * wm
        props[21] = k_ann * wp * wm / N
        props[22] = eps * vm
        props[23] = eps * b * wp
        props = np.maximum(props, 0)
        a0 = props.sum()
        if a0 <= 0:
            break
        tau = rng.exponential(1.0 / a0)
        t += tau
        while next_record <= t and next_record <= t_end:
            v_conc = (vp - vm) / N
            record_times.append(next_record)
            record_v.append(v_conc)
            next_record += 0.1
        r = rng.random() * a0
        cumsum = 0.0
        reaction = -1
        for i in range(24):
            cumsum += props[i]
            if cumsum >= r:
                reaction = i
                break
        stoich = {
            0: (4, 1), 1: (4, -1), 2: (5, 1), 3: (5, -1), 4: (6, 1), 5: (6, -1),
            6: (0, 1), 7: (0, 1), 8: (0, 1), 9: (0, 1), 10: (0, 1), 11: (0, 1),
            13: (1, 1), 14: (1, 1), 15: (1, 1), 16: (1, 1), 17: (1, 1),
            18: (2, 1), 19: (2, 1), 20: (2, 1),
            22: (3, 1), 23: (3, 1),
        }
        if reaction == 12:
            state[0] -= 1; state[1] -= 1
        elif reaction == 21:
            state[2] -= 1; state[3] -= 1
        elif reaction in stoich:
            idx, delta = stoich[reaction]
            state[idx] += delta
        state = np.maximum(state, 0)
        n_reactions += 1

    return np.array(record_times), np.array(record_v), n_reactions


if __name__ == "__main__":
    N = 100
    k_fast = 1000  # k_fast/N scaling: N=100 -> k_fast=1000

    print(f"Gillespie SSA: N={N}, k_fast={k_fast}")
    t0 = time.time()
    ts, vs, n_rxn = gillespie_qssa_fhn(N, k_fast=k_fast, t_end=200.0)
    elapsed = time.time() - t0

    print(f"  Reactions: {n_rxn:,}, Time: {elapsed:.1f}s, Points: {len(ts)}")

    # Save trajectory CSV
    outpath = "/Users/tsubasa/Documents/TsubasaWorkspace/neuroblox_bench/gillespie_N100_trajectory.csv"
    np.savetxt(outpath, np.column_stack([ts, vs]), delimiter=",", header="t,v", comments="")
    print(f"  Saved: {outpath}")

    # Detect individual periods
    mask = ts > 50
    t_m, v_m = ts[mask], vs[mask]
    crossings = []
    for i in range(1, len(v_m)):
        if v_m[i-1] < 0 and v_m[i] >= 0:
            crossings.append(t_m[i])

    periods = np.diff(crossings)
    print(f"\n  Zero crossings: {[f'{c:.1f}' for c in crossings]}")
    print(f"  Individual periods: {[f'{p:.2f}' for p in periods]}")
    if len(periods) > 1:
        print(f"  Mean: {np.mean(periods):.2f}s, SD: {np.std(periods, ddof=1):.2f}s (n={len(periods)})")
    elif len(periods) == 1:
        print(f"  Only 1 period: {periods[0]:.2f}s (need more cycles for SD)")
    else:
        print(f"  No oscillation detected")
