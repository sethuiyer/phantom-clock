#!/usr/bin/env python3
"""Experiment 1: a caustic can manufacture timing structure.

Model, stated explicitly because the paper's description leaves the delay law
free. Rays converge on a common spatial point; each carries a distinct
direction parameter U and a direction-dependent group delay

    T_g(U) = A sin(2U),        U ~ Uniform[0, pi),

so E[T_g] = 0 and Var(T_g) = A^2/2. The amplitude is the single calibrated
constant: A is chosen to give std(T_g) = 2.85 fs, the value the paper quotes,
so A = 2.85 * sqrt(2). Detector noise eps ~ N(0, sigma^2) with sigma = 0.30 fs.

Then:
  * a SPATIAL-only representation merges all directions at the focus, so the
    residual is T_g(U) - E[T_g] + eps and has variance Var(T_g) + sigma^2;
  * a LIFTED representation bins the direction into K cells and subtracts the
    per-cell mean, leaving residual variance sigma^2 + E[Var(T_g | bin)].

What the code reports is the second quantity as a *prediction*: only A is
calibrated, so the resolved fraction is not fitted and the agreement (or not)
with the paper is genuine information.

Reproduce:  python3 exp1_caustic.py
"""
import numpy as np

N_RAYS = 20_000
SIGMA = 0.30            # fs, detector noise
TARGET_STD = 2.85       # fs, quoted std of T_g(U)
K_BINS = 128
SEED = 0


def delay(u, A):
    return A * np.sin(2.0 * u)


def main():
    A = TARGET_STD * np.sqrt(2.0)
    rng = np.random.default_rng(SEED)
    u = rng.uniform(0.0, np.pi, N_RAYS)
    tg = delay(u, A)
    eps = rng.normal(0.0, SIGMA, N_RAYS)
    y = tg + eps

    print(f"A calibrated so std(T_g) = {TARGET_STD} fs  ->  A = {A:.4f} fs")
    print(f"empirical std(T_g)      = {tg.std(ddof=1):.4f} fs")
    print(f"Var(T_g)                = {tg.var(ddof=1):.4f} fs^2")

    # --- spatial-only: one mean subtracted for the whole focus -------------
    merged = y - tg.mean()
    print(f"\nSPATIAL-ONLY (merged) residual:")
    print(f"  var = {merged.var(ddof=1):.4f} fs^2   std = {merged.std(ddof=1):.4f} fs")
    print(f"  paper: var = 8.21 fs^2, std = 2.87 fs")
    ratio = merged.std(ddof=1) / SIGMA
    print(f"  std / sigma = {ratio:.3f}x   (paper: 9.55x)")
    print(f"  var / sigma^2 = {ratio**2:.1f}x   (paper: 91x)")
    print(f"  skew = {float(((merged - merged.mean())**3).mean() / merged.std()**3):.3f}"
          f"   (paper: 0.42)")
    kurt = float(((merged - merged.mean())**4).mean() / merged.var()**2) - 3.0
    print(f"  excess kurtosis = {kurt:.3f}   (paper: -0.85)")

    # --- lifted: per-bin mean subtracted ----------------------------------
    edges = np.linspace(0.0, np.pi, K_BINS + 1)
    idx = np.clip(np.searchsorted(edges, u, side="right") - 1, 0, K_BINS - 1)
    within = np.zeros(N_RAYS)
    for k in range(K_BINS):
        sel = idx == k
        if sel.any():
            within[sel] = tg[sel] - tg[sel].mean()
    lifted = y - (tg - within)

    print(f"\nLIFTED with K = {K_BINS} bins:")
    print(f"  var = {lifted.var(ddof=1):.4f} fs^2   std = {lifted.std(ddof=1):.4f} fs")
    print(f"  paper: var = 0.117 fs^2, std = 0.34 fs")
    var_within = float(within.var(ddof=1))
    resolved = 1.0 - var_within / tg.var(ddof=1)
    print(f"  Var(T_g | bin) = {var_within:.6f} fs^2")
    print(f"  resolved fraction = {resolved:.4%}   (unresolved {1 - resolved:.4%})")
    print(f"  paper (corrected): 99.67% resolved, 0.33% unresolved")

    print("\nReading: the merged-residual quantities are arithmetic consequences of")
    print("(std T_g, sigma) and reproduce the paper. The lifted variance is the")
    print("one genuine prediction, and it depends on the delay law, which the")
    print("paper does not state. If the two disagree, the paper's 0.117 fs^2 is")
    print("a property of an unstated model rather than of the released one.")


if __name__ == "__main__":
    main()
