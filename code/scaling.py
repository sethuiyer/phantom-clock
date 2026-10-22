#!/usr/bin/env python3
"""Experiment 5 supporting analysis: budget scaling, controls, and the
representation cost of chart legality.

Answers four questions that the single K = 64 headline number cannot:

  A. How does the DP-over-uniform improvement scale with the address budget K?
     (SSE matrix is built once per (seed, control) and reused for every K.)

  B. How much of the gain is specific to the released two-regime delay model,
     versus ordinary optimal nonuniform quantization of any curved function?
     Controls at the same budget:
       affine      Tg = A0 * theta          -> uniform bins should be optimal
       smooth      Tg = A0 * sin(2 theta)   -> single regime, NO slow/rapid split
       fast        Tg = A0 * sin(8 theta)   -> single fast regime
       released    the two-regime model of generate.py

  C. Is the 200,000-ray sample necessary? The released delay law is known in
     closed form, so the same DP can be run on an analytic quadrature grid
     (exact cell masses) with zero sampled rays. If that matches the sampled
     solution, the partition is a function of the delay law, not of the data.

  D. What does chart legality cost? The classical unconstrained optimum for a
     scalar observable is a Lloyd-Max (Max 1960; Lloyd 1982) quantizer of Tg.
     It reaches far lower distortion -- but its cells are contiguous in Tg, not
     in theta, so realizing them needs one address per theta-run. We report both
     the distortion and the number of runs, so the cost is stated in address
     structure rather than asserted as a moral.

Reproduce:
    python3 scaling.py --seeds 12 --out results_exp5_scaling.csv
"""
import argparse
import csv

import numpy as np

import generate as g
from partition import GRID, dp_partition, sse_matrix

N_TRAIN = 200_000
N_TOTAL = 300_000
K_LIST = [16, 32, 64, 128, 256]
K_HEADLINE = 64

CONTROLS = {
    "released": lambda t: g.delay(t),
    "smooth": lambda t: g.A0 * np.sin(2.0 * t),
    "fast": lambda t: g.A0 * np.sin(8.0 * t),
    "affine": lambda t: g.A0 * t,
}


def uniform_cells(k_cells):
    w = GRID // k_cells
    return [(i, i + w) for i in range(0, GRID, w)]


def analytic_dp(f, k_cells, n_grid=GRID):
    """Same grid and same DP as the sampled version, but cell masses are exact
    quadrature weights (interval widths) and the delay is evaluated at cell
    midpoints. No sampled rays."""
    edges = np.linspace(0.0, np.pi, n_grid + 1)
    d = f(edges[:-1] + 0.5 * np.pi / n_grid)
    w = np.full(n_grid, np.pi / n_grid)
    c, s1 = w, w * d
    s2 = w * d * d
    C = np.concatenate([[0.0], np.cumsum(c)])
    S1 = np.concatenate([[0.0], np.cumsum(s1)])
    S2 = np.concatenate([[0.0], np.cumsum(s2)])
    I = np.arange(n_grid + 1)[:, None]
    J = np.arange(n_grid + 1)[None, :]
    m = C[J] - C[I]
    s = S1[J] - S1[I]
    q = S2[J] - S2[I]
    with np.errstate(divide="ignore", invalid="ignore"):
        S = np.where(m > 0, q - s * s / m, 0.0)
    S[np.tril_indices(n_grid + 1)] = np.inf
    return dp_partition(S, k_cells), edges


def sampled_sweep(n_seeds):
    """A and B: rows of (control, K, uniform, dp, ratio) per seed."""
    rows = []
    for seed in range(n_seeds):
        th, br, _ = g.make_rays(N_TOTAL, seed)
        tr, te = g.split(th, br)
        th_tr = th[tr][:N_TRAIN]          # 200,000 of ~240,000 available
        th_te, n_te = th[te], int(te.sum())
        for name, f in CONTROLS.items():
            d_tr, d_te = f(th_tr), f(th_te)
            edges = np.linspace(0.0, np.pi, GRID + 1)
            S = sse_matrix(th_tr, d_tr, edges)
            for K in K_LIST:
                kc = K // 2
                from partition import distortion
                u = distortion(uniform_cells(kc), edges, th_te, d_te)
                dp = distortion(dp_partition(S, kc), edges, th_te, d_te)
                rows.append(dict(seed=seed, control=name, K=K, n_test=n_te,
                                 uniform=u, dp=dp, ratio=u / dp))
    return rows


def lloyd_max_runs(f, k_cells, n=1_000_000):
    """Classical unconstrained optimal scalar quantizer of Tg, plus the number
    of theta-runs its cells induce (the address structure it would cost)."""
    d = np.sort(f(np.linspace(0.0, np.pi, n, endpoint=False)))
    qs = np.quantile(d, np.linspace(0, 1, k_cells + 1))
    qs[0], qs[-1] = d[0] - 1, d[-1] + 1
    b, cen = qs.copy(), None
    for _ in range(500):
        lab = np.clip(np.searchsorted(b, d, "right") - 1, 0, k_cells - 1)
        cen = np.array([d[lab == c].mean() if np.any(lab == c) else b[c]
                        for c in range(k_cells)])
        nb = np.concatenate([[b[0]], 0.5 * (cen[1:] + cen[:-1]), [b[-1]]])
        if np.allclose(nb, b, atol=1e-15):
            break
        b = nb
    lab = np.clip(np.searchsorted(b, d, "right") - 1, 0, k_cells - 1)
    sse = float(((d - cen[lab]) ** 2).mean())
    th = np.linspace(0.0, np.pi, 400_000, endpoint=False)
    lt = np.clip(np.searchsorted(b, f(th), "right") - 1, 0, k_cells - 1)
    runs = 1 + int(np.sum(np.diff(lt) != 0))
    return sse, runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--out", default="results_exp5_scaling.csv")
    a = ap.parse_args()

    rows = sampled_sweep(a.seeds)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    tcrit = {12: 2.201, 30: 2.045}.get(a.seeds, 1.96)

    print(f"held-out rays per seed: mean "
          f"{np.mean([r['n_test'] for r in rows if r['seed'] == 0]):.0f} "
          f"(seed 0); split is the deterministic SHA-256 80/20 rule\n")
    print("== A. Budget scaling (released two-regime model) ==")
    print(f"{'K':>6} {'cells/branch':>13} {'uniform':>12} {'dp':>12} {'ratio':>9}")
    for K in K_LIST:
        sel = [r for r in rows if r["control"] == "released" and r["K"] == K]
        u = np.array([r["uniform"] for r in sel])
        d = np.array([r["dp"] for r in sel])
        rt = u / d
        print(f"{K:6d} {K // 2:13d} {u.mean():12.4e} {d.mean():12.4e} "
              f"{rt.mean():6.3f} +- {tcrit * rt.std(ddof=1) / np.sqrt(len(rt)):.3f}")

    print("\n== B. Controls at K = 64: how much is generic nonuniform quantization? ==")
    print(f"{'control':>10} {'uniform':>12} {'dp':>12} {'ratio':>9}")
    for name in CONTROLS:
        sel = [r for r in rows if r["control"] == name and r["K"] == K_HEADLINE]
        u = np.array([r["uniform"] for r in sel])
        d = np.array([r["dp"] for r in sel])
        rt = u / d
        print(f"{name:>10} {u.mean():12.4e} {d.mean():12.4e} "
              f"{rt.mean():6.3f} +- {tcrit * rt.std(ddof=1) / np.sqrt(len(rt)):.3f}")

    print("\n== C. Sample-estimated vs analytic partition (K = 64, cells/branch = 32) ==")
    f = CONTROLS["released"]
    ana_cells, ana_edges = analytic_dp(f, K_HEADLINE // 2)
    from partition import distortion
    pop_th = np.linspace(0.0, np.pi, 2_000_000, endpoint=False)
    pop_d = f(pop_th)
    d_ana = distortion(ana_cells, ana_edges, pop_th, pop_d)
    sel = [r for r in rows if r["control"] == "released" and r["K"] == K_HEADLINE]
    d_smp = np.array([r["dp"] for r in sel])
    print(f"  analytic quadrature DP (0 sampled rays) : {d_ana:.6e} fs^2")
    print(f"  sample-estimated DP ({a.seeds} seeds)     : {d_smp.mean():.6e} fs^2")
    print("  -> the delay law is known in closed form, so the partition is a")
    print("     function of the law; sampling estimates it and adds a little noise.")

    print("\n== D. What chart legality costs (K = 64) ==")
    sse, runs = lloyd_max_runs(f, K_HEADLINE // 2)
    u = np.array([r["uniform"] for r in sel])
    print(f"  unconstrained Lloyd-Max of Tg (32 scalar cells): {sse:.4e} fs^2"
          f"  = {u.mean() / sse:.1f}x better than uniform")
    print(f"  ...but those 32 cells form {runs} runs in theta,")
    print(f"     i.e. ~{runs / (K_HEADLINE // 2):.1f}x the address structure.")
    print(f"  chart-legal contiguous DP at the same budget  : {d_smp.mean():.4e} fs^2")
    print(f"  runs per cell at K=256 would be the honest next experiment.")


if __name__ == "__main__":
    main()