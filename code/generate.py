#!/usr/bin/env python3
"""Reference synthetic generator for Experiment 5 (released artifact).

Calibrated reference model
--------------------------
The original experiment script was not preserved; article.md's surviving text
specifies only that T_g(theta) "varied slowly over one part of the angular
domain and rapidly over another" and fixes K=64 cells and the held-out
distortions 0.000423 -> 0.000242 (1.746x over 30 seeds). This reference model
is the minimal two-regime function calibrated so that:

  * amplitude     A0 = 0.4117132519529059 fs  sets the uniform-bin distortion
                                           to 0.000423 fs^2;
  * heterogeneity A  = 0.728                  sets the DP/uniform ratio
                                           to 1.746.

Neither constant is derived from physics; both are documented calibration
parameters of the synthetic benchmark (evidence type B). The improvement ratio
is scale-invariant, so A0 sets only the absolute distortion scale; A is the
parameter the headline number actually depends on, and scaling.py reports the
ratio across A.

Model
-----
  theta ~ Uniform[0, pi)
  f(theta) = A0 * sin(2 theta)                 for theta <  pi/2   (slow regime)
           = A0 * A * sin(4 theta)             for theta >= pi/2   (rapid regime)
  branch b in {-1, +1} selects propagation direction Omega(theta) or -Omega(theta).

Note that "slow" and "rapid" label the oscillation frequency, not the
amplitude: the slow regime's peak is A0 = 0.4117 fs and the rapid regime's peak
is A0 * A = 0.2997 fs.

Delay T = f(theta) is branch-independent, and -- importantly -- f is NOT
pi-symmetric: T_g(theta) != T_g(pi - theta) except at theta = pi/2. So this
generator cannot exhibit the theta <-> pi-theta branch collision, and any
contiguous angular partition preserves branch identity trivially here. Branch
identity is therefore a THEORETICAL architectural constraint (Sec. 6, 12.5,
Theorem 11), not something Experiment 5 measures. The measured quantity is
chart-legal contiguous quantisation of a scalar observable.

Split rule (deterministic, seed-independent)
-------------------------------------------
  canonical identity string "%.17g|%d" % (theta, b); SHA-256; first 8 hex
  digits mod 5 == 0 -> test (20%), else train (80%).

Resulting split sizes, from 300,000 rays: ~240,000 train / ~60,000 test. The
per-seed counts are not constant because the split hashes sampled values: over
the 30 released seeds the held-out count is 60,016 +- 223 (min 59,644, max
60,479; seed 0 gives exactly 60,170). Experiment 5 uses the first 200,000 of
the ~240,000 available training rays and all ~60,000 held-out rays.
"""
import hashlib

import numpy as np

A0 = 0.4117132519529059
A_RAPID = 0.728


def delay(theta):
    """Group-delay function T_g(theta) in fs (branch-independent)."""
    t = np.asarray(theta, dtype=float)
    return np.where(t < 0.5 * np.pi,
                    A0 * np.sin(2.0 * t),
                    A0 * A_RAPID * np.sin(4.0 * t))


def make_rays(n, seed):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, np.pi, n)
    branch = rng.integers(0, 2, n) * 2 - 1
    return theta, branch, delay(theta)


def _is_test(theta, branch):
    s = "%.17g|%d" % (theta, branch)
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) % 5 == 0


def split(theta, branch):
    test = np.array([_is_test(t, b) for t, b in zip(theta, branch)], dtype=bool)
    return ~test, test
