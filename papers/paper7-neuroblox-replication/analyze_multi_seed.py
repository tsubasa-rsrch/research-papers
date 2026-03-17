#!/usr/bin/env python3
"""
Multi-seed Neville analysis — Statistical analysis of 10 seeds
Run after multi_seed_neville.jl completes
"""
import pandas as pd
import numpy as np
from pathlib import Path

data_path = Path(__file__).parent / "multi_seed_results.csv"
if not data_path.exists():
    print(f"Waiting for {data_path}...")
    exit(0)

df = pd.read_csv(data_path)
seeds = sorted(df['seed'].unique())
N_trials = 700
stable_start = 400

print(f"=== Multi-Seed Neville Analysis ({len(seeds)} seeds × {N_trials} trials) ===\n")

# === Per-seed summary ===
print("=== Per-Seed Accuracy ===")
for seed in seeds:
    sd = df[df['seed'] == seed]
    acc = sd['correct'].mean() * 100
    first50 = sd.iloc[:50]['correct'].mean() * 100
    last50 = sd.iloc[-50:]['correct'].mean() * 100
    print(f"  Seed {seed}: {acc:.1f}% (first50: {first50:.0f}% → last50: {last50:.0f}%)")

# === Error clustering across seeds ===
print("\n=== Error Clustering (Neville persistence) ===")
cluster_ratios = []
for seed in seeds:
    sd = df[df['seed'] == seed]
    errors = np.where(~sd['correct'].values)[0]
    pairs = sum(1 for i in range(len(errors)-1) if errors[i+1] == errors[i]+1)
    expected = len(errors)**2 / N_trials
    ratio = pairs / max(expected, 0.1)
    cluster_ratios.append(ratio)
    print(f"  Seed {seed}: {pairs} pairs / {expected:.1f} expected = {ratio:.2f}x")

mean_ratio = np.mean(cluster_ratios)
above_1 = sum(1 for r in cluster_ratios if r > 1.0)
print(f"\n  Mean clustering ratio: {mean_ratio:.2f}x")
print(f"  Seeds with ratio > 1.0: {above_1}/{len(seeds)}")
if above_1 >= len(seeds) * 0.8:
    print("  → 🧙 NEVILLE CONFIRMED across seeds! Error clustering is a circuit property!")
elif above_1 >= len(seeds) * 0.5:
    print("  → 🧙 Neville trend: majority of seeds show clustering")
else:
    print("  → Neville effect is seed-dependent (not a robust circuit property)")

# === Category asymmetry ===
print("\n=== Category Asymmetry ===")
cat_diffs = []
for seed in seeds:
    sd = df[(df['seed'] == seed) & (df['trial'] >= stable_start)]
    cat1 = sd[sd['category'] == 1]
    cat2 = sd[sd['category'] == 2]
    cat1_err = 1 - cat1['correct'].mean()
    cat2_err = 1 - cat2['correct'].mean()
    diff = cat2_err - cat1_err
    cat_diffs.append(diff)
    print(f"  Seed {seed}: Cat1 err={cat1_err*100:.1f}% Cat2 err={cat2_err*100:.1f}% (diff={diff*100:+.1f}%)")

# Is the asymmetry consistently in the same direction?
same_direction = sum(1 for d in cat_diffs if d > 0)
print(f"\n  Cat2 > Cat1 error: {same_direction}/{len(seeds)} seeds")
if same_direction >= len(seeds) * 0.8:
    print("  → Structural bias confirmed! Circuit consistently struggles with one category")
else:
    print("  → Asymmetry varies by seed (initial weight dependent)")

# === DA prediction ===
print("\n=== DA Prediction of Errors ===")
da_diffs = []
for seed in seeds:
    sd = df[(df['seed'] == seed) & (df['trial'] >= stable_start)].reset_index(drop=True)
    before_err = []
    before_cor = []
    for i in range(len(sd)-1):
        if not sd.loc[i+1, 'correct']:
            before_err.append(sd.loc[i, 'DA'])
        else:
            before_cor.append(sd.loc[i, 'DA'])
    if before_err and before_cor:
        diff = np.mean(before_err) - np.mean(before_cor)
        da_diffs.append(diff)
        print(f"  Seed {seed}: DA before err={np.mean(before_err):.3f} before cor={np.mean(before_cor):.3f} diff={diff:+.4f}")

negative_count = sum(1 for d in da_diffs if d < 0)
print(f"\n  DA drops before errors: {negative_count}/{len(da_diffs)} seeds")
if negative_count >= len(da_diffs) * 0.7:
    print("  → 🧠 DA prediction confirmed! Lower DA precedes errors across seeds")
else:
    print("  → DA prediction is inconsistent across seeds")

# === Learning phase transition ===
print("\n=== Learning Phase Transition ===")
for seed in seeds:
    sd = df[df['seed'] == seed]
    # Find first 50-trial window with >70% accuracy
    for start in range(0, N_trials-49, 10):
        window_acc = sd.iloc[start:start+50]['correct'].mean()
        if window_acc >= 0.7:
            print(f"  Seed {seed}: Learning onset at trial ~{start} ({window_acc*100:.0f}%)")
            break
    else:
        print(f"  Seed {seed}: Never reached 70%")

# === Error clustering by phase ===
print("\n=== Error Clustering by Phase (mini phase-transition) ===")
for seed in seeds:
    sd = df[df['seed'] == seed]
    correct = sd['correct'].values
    # Early (1-200), Mid (201-400), Late (401-700)
    phases = [("Early", 0, 200), ("Mid", 200, 400), ("Late", 400, 700)]
    parts = []
    for name, s, e in phases:
        errors = np.where(~correct[s:e])[0]
        pairs = sum(1 for i in range(len(errors)-1) if errors[i+1] == errors[i]+1)
        expected = max(len(errors)**2 / (e-s), 0.1)
        ratio = pairs / expected
        parts.append(f"{name}:{ratio:.1f}x")
    print(f"  Seed {seed}: {' | '.join(parts)}")

# === Pattern classification (Kana's A/B/C) ===
print("\n=== Symmetry-Breaking Pattern Classification ===")
cat2_harder = sum(1 for d in cat_diffs if d > 0.05)  # Cat2 clearly harder
cat1_harder = sum(1 for d in cat_diffs if d < -0.05)  # Cat1 clearly harder
neither = len(cat_diffs) - cat2_harder - cat1_harder

print(f"  Cat2 harder: {cat2_harder}/{len(seeds)} seeds")
print(f"  Cat1 harder: {cat1_harder}/{len(seeds)} seeds")
print(f"  Neither: {neither}/{len(seeds)} seeds")

if cat2_harder >= len(seeds) * 0.8:
    print("  → Pattern A: Stimulus bias (Cat2 consistently harder)")
elif cat1_harder + cat2_harder >= len(seeds) * 0.6 and min(cat1_harder, cat2_harder) >= 2:
    print("  → Pattern B: Jeong-type symmetry-breaking! Category bias flips between seeds! 🧠✨")
else:
    print("  → Pattern C: Mixed (structural bias + initial weight effects)")

# === Clustering onset analysis ===
print("\n=== Error Clustering Onset (Mini Phase Transition) ===")
print("Trial at which 50-trial-window clustering ratio first exceeds 1.0:")
onset_trials = []
for seed in seeds:
    sd = df[df['seed'] == seed]
    correct = sd['correct'].values
    found = False
    for start in range(100, N_trials - 49, 25):
        window = correct[start:start+50]
        errors_in_window = np.where(~window)[0]
        pairs = sum(1 for i in range(len(errors_in_window)-1)
                    if errors_in_window[i+1] == errors_in_window[i]+1)
        expected = max(len(errors_in_window)**2 / 50, 0.1)
        if expected > 0.5 and pairs / expected > 1.0:
            onset_trials.append(start)
            print(f"  Seed {seed}: onset at trial {start} (ratio={pairs/expected:.2f}x)")
            found = True
            break
    if not found:
        print(f"  Seed {seed}: no clustering onset found")
        onset_trials.append(None)

valid_onsets = [t for t in onset_trials if t is not None]
if len(valid_onsets) >= 3:
    print(f"\n  Mean onset: trial {np.mean(valid_onsets):.0f} ± {np.std(valid_onsets):.0f}")
    print(f"  Range: {min(valid_onsets)}-{max(valid_onsets)}")
    if np.std(valid_onsets) < 100:
        print("  → Consistent onset timing! Mini phase transition at a characteristic trial count")
    else:
        print("  → Variable onset timing (seed-dependent)")

print("\nDone! 🧠🔍")
