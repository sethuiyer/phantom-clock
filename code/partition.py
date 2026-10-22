#!/usr/bin/env python3
"""Experiment 5 reproduction: uniform vs chart-legal DP, 30 seeds.

Setup (matches the paper):
  K = 64 addresses total; branch identity must be encoded in the address, so
  each branch receives K/2 = 32 contiguous angular cells. Delay is
  branch-independent, so both branches share the optimal angular partition;
  the reported distortions are conditional on the ray's branch (E[Var(T|B)]).

  Uniform baseline : 32 equal-width theta cells per branch.
  Chart-legal DP   : 32 contiguous theta cells per branch minimizing
                     sum of within-cell squared error (exact DP on a
                     1024-point boundary grid).

Held-out distortion is evaluated on the deterministic 20% test split of
100k rays (see generate.py). Replicated over 30 independent sampling seeds;
reported: per-seed values, mean, 95% CI (t-interval), and the DP improvement
ratio with its delta-method CI.
"""
import argparse
import csv

import numpy as np

from generate import make_rays, split

K = 64
N_TRAIN, N_TEST = 200_000, 100_000
GRID = 1024


def sse_matrix(t, d, edges):
    """SSE[i, j] for interval [edges[i], edges[j]) via grid prefix sums."""
    idx = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
    n = len(edges) - 1
    c = np.bincount(idx, minlength=n).astype(float)
    s1 = np.bincount(idx, weights=d, minlength=n)
    s2 = np.bincount(idx, weights=d * d, minlength=n)
    C = np.concatenate([[0.0], np.cumsum(c)])
    S1 = np.concatenate([[0.0], np.cumsum(s1)])
    S2 = np.concatenate([[0.0], np.cumsum(s2)])
    I = np.arange(n + 1)[:, None]
    J = np.arange(n + 1)[None, :]
    m = C[J] - C[I]
    s = S1[J] - S1[I]
    q = S2[J] - S2[I]
    with np.errstate(divide="ignore", invalid="ignore"):
        S = np.where(m > 0, q - s * s / m, 0.0)
    S[np.tril_indices(n + 1)] = np.inf
    return S


def dp_partition(S, k_cells):
    n = S.shape[0] - 1
    INF = np.inf
    dp = np.full((k_cells + 1, n + 1), INF)
    arg = np.zeros((k_cells + 1, n + 1), dtype=int)
    dp[0, 0] = 0.0
    for k in range(1, k_cells + 1):
        prev = dp[k - 1]
        for j in range(k, n + 1):
            vals = prev[k - 1:j] + S[k - 1:j, j]
            i = int(np.argmin(vals)) + (k - 1)
            dp[k, j] = vals[i - (k - 1)]
            arg[k, j] = i
    cells, j = [], n
    for k in range(k_cells, 0, -1):
        i = arg[k, j]
        cells.append((i, j))
        j = i
    return sorted(cells)


def distortion(cells, edges, t, d):
    idx = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
    err = n = 0
    for (i, j) in cells:
        sel = (idx >= i) & (idx < j)
        m = sel.sum()
        if m == 0:
            continue
        err += ((d[sel] - d[sel].mean()) ** 2).sum()
        n += m
    return err / max(n, 1)


def run(seed):
    theta, branch, dly = make_rays(N_TRAIN + N_TEST, seed)
    tr, te = split(theta, branch)
    th_tr, d_tr = theta[tr][:N_TRAIN], dly[tr][:N_TRAIN]
    th_te, d_te = theta[te][:N_TEST], dly[te][:N_TEST]

    edges = np.linspace(0.0, np.pi, GRID + 1)
    S = sse_matrix(th_tr, d_tr, edges)
    cells_u = [(i, i + GRID // (K // 2)) for i in range(0, GRID, GRID // (K // 2))]
    cells_dp = dp_partition(S, K // 2)
    return {"uniform": distortion(cells_u, edges, th_te, d_te),
            "dp": distortion(cells_dp, edges, th_te, d_te)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--out", default="results_exp5_seeds.csv")
    a = ap.parse_args()

    rows = [dict(seed=s, **run(s)) for s in range(a.seeds)]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "uniform", "dp"])
        w.writeheader()
        w.writerows(rows)

    u = np.array([r["uniform"] for r in rows])
    d = np.array([r["dp"] for r in rows])
    n = len(rows)
    tu = 2.045 if n == 30 else 1.96  # t_{0.975, 29}
    print(f"seeds={n}")
    print(f"uniform : {u.mean():.6e}  ±{tu*u.std(ddof=1)/np.sqrt(n):.2e} (95% CI)")
    print(f"dp      : {d.mean():.6e}  ±{tu*d.std(ddof=1)/np.sqrt(n):.2e} (95% CI)")
    ratios = u / d
    half = tu * ratios.std(ddof=1) / np.sqrt(n)
    print(f"improvement (per-seed ratios): {ratios.mean():.3f} ±{half:.3f} (95% CI)")


if __name__ == "__main__":
    main()
