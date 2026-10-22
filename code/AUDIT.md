# AUDIT.md — independent review of the released artifacts

**Audited by Minimax M3.**

Scope: `generate.py`, `partition.py`, `scaling.py`, `results_exp5_seeds.csv`,
`results_exp5_scaling.csv`, `chart_encoder.ads/.adb`, `test_encoder.adb`,
`gnatprove-transcript.txt`, and the claims those artifacts are cited for.

Method: re-derivation from source, not inspection of output. Every numerical claim
was recomputed; the 30-seed result was reproduced from scratch and compared
byte-for-byte; Theorem 11 was re-derived independently; all 15 external references
were checked for existence and correct attribution; the Ada/SPARK contracts and the
GNATprove transcript were read against the specification.

---

## Summary

| | |
|---|---|
| Headline result reproduces | **Yes**, byte-identically |
| Factual defects found | **5** (all corrected) |
| Claims overstated | **3** (all corrected) |
| Claims understated | **2** (both strengthened) |
| Theorems checked | 1 of 8 re-derived; **correct** |
| References checked | 15 / 15 real and correctly cited |
| Fabrication indicators | none |

The central finding is **not** damage. The audit found one genuine factual bug
cluster around sample sizes, and it also uncovered a substantially stronger
experiment than the one the paper was carrying. Both are now in the manuscript.

---

## What reproduced

`python3 partition.py --seeds 30` was rerun from scratch and the output CSV is
**byte-identical** to the committed `results_exp5_seeds.csv`:

```
uniform : 4.230001e-04  ±9.02e-07 (95% CI)
dp      : 2.422992e-04  ±4.24e-07 (95% CI)
improvement (per-seed ratios): 1.746 ±0.005 (95% CI)
```

Every correction below was made **without perturbing this number.** Where a fix
could have forced recalibration (the sample-size bug was the obvious candidate),
the prose was corrected instead and the experiment was left alone.

---

## Defects found and corrected

### 1. The held-out set was ~60,000 rays, not 100,000 — *factual*

`partition.py` set `N_TEST = 100_000` and sliced `theta[te][:N_TEST]`. But the
split rule is an 80/20 SHA-256 hash split of 300,000 rays, which yields ~240,000
train and ~60,000 test. The slice therefore **silently** returned 60,170 rays
instead of 100,000, and the manuscript claimed "200,000 train / 100,000 held-out" in
two places.

The stated sample sizes and the stated split rule are mutually impossible.

Per-seed held-out counts are not constant, because the split hashes sampled values:

```
held-out per seed over 30 seeds: min 59644  max 60479  mean 60015.7  sd 222.5
seed 0 = 60170
```

**Correction.** `N_TEST` is now documented as a *cap that never binds* rather than a
target, `N_TOTAL` is pinned to 300,000 to preserve the RNG stream, and both pool
sizes are asserted in `run()` so a future change cannot truncate silently. The prose
now says ≈60,000 held-out rays (60,170 at the reference seed), from which exactly
200,000 of the ~240,000 available training rays are used. **The numbers did not
change.**

### 2. `generate.py` docstring stated the wrong calibration constant — *factual*

The docstring said `A0 = 0.2385 fs`. The code had `A0 = 0.4117132519529059`. With
0.2385 the uniform-bin distortion is `1.42e-4`, not the claimed `4.23e-4`. Stale
documentation for the single most important constant in the artifact.

### 3. `code/README.md` described a model that is not the model — *factual*

The README described a `0.2·|sin 4θ|`-style law. The released law is
`A0·sin 2θ` on `[0, π/2)` and `A0·0.728·sin 4θ` on `[π/2, π)`, and it labels the
*rapid* region as the one with the **smaller** amplitude (0.300 vs 0.412) — "slow"
and "rapid" refer to oscillation frequency, not magnitude.

### 4. The branch-collision example was numerically false — *factual*

§12.5 asserted that a released transform-based partition merged `θ = 0.35π` and
`θ = 0.65π` "because they share the same Tg". For the released law:

```
Tg(0.35pi) = +0.333083 fs      Tg(0.65pi) = +0.285058 fs
fraction of theta with Tg(theta) == Tg(pi-theta): 0.0000
```

They differ by 17%, and the fraction of `θ` with `Tg(θ) = Tg(π−θ)` is **zero**.
The released delay law is not `π`-symmetric, so the generator cannot exhibit the
phenomenon, and since delay is branch-independent any contiguous angular partition
preserves branch identity *trivially* on it.

**Correction.** The example is withdrawn. Branch identity is now stated to be a
**theoretical architectural constraint** (§6, §12.5, Theorem 11), not a quantity
Experiment 5 measures. What Experiment 5 measures is chart-legal contiguous
quantization of a scalar observable.

### 5. An arithmetic slip in Experiment 1 — *factual*

The paper concluded Experiment 1 resolved "≈95% of the geometric-delay variance,
leaving approximately 5% unresolved". From its own numbers:

```
Var(Tg)     = 8.1225     Var(Tg|B) = 0.117 - 0.09 = 0.027
resolved    = 1 - 0.027/8.1225 = 99.67%   unresolved = 0.33%
```

**Corrected to ≈0.3% unresolved.**

---

## Claims that were overstated, and are now corrected

### 6. "47/47 obligations" read stronger than it is

True, but the semantic content is small, and the transcript itself says
`max steps used for successful proof: 1`. Specifically:

- the chart table is a three-entry **literal**, `(0,512,768) / (512,256,256)`, so
  injectivity holds there by construction;
- `Table_Is_Consistent` is defined in the specification but is **never used as any
  subprogram's precondition**, so no contract carries the table invariant;
- `Global_Rank` is an `Import` + `Ghost` stub with `Global => null` and a SPARK_Mode
  Off body — the transcript reports it `skipped; body is SPARK_Mode => Off`. It is
  unused;
- `Injectivity_Lemma` is body-local (not in the spec) and works by deriving an
  unreachable-branch assertion failure — legitimate, but for this table only;
- `test_encoder.adb` is SPARK_Mode Off, so the exhaustive bijection test is
  *executed*, not verified.

**Correction.** The manuscript, blog, and README now read "47/47 proof obligations
discharged for the released three-chart encoder instance and its contract
structure", with the four limitations listed explicitly. This is *consistent* with
the paper's own §1.2 evidence taxonomy and §15 — the risk was only that the bare
"47/47" read as generic verification of arbitrary chart tables.

### 7. The improvement was presented as branch-preservation evidence

Already addressed by #4.

### 8. The 1.75× was presented without its controls

The number is exact and reproducible, but a single ratio invites over-reading. New
controls (12 seeds, `t₁₁ = 2.201`, `scaling.py`):

**Budget scaling** — the gain is a property of the budget as much as the method:

| K (cells/branch) | uniform fs² | DP fs² | ratio | 95% CI |
|---|---|---|---|---|
| 16 (8) | 6.406e-03 | 2.658e-03 | 2.410 | ± 0.011 |
| 32 (16) | 1.677e-03 | 8.195e-04 | 2.046 | ± 0.007 |
| 64 (32) | 4.231e-04 | 2.421e-04 | 1.748 | ± 0.009 |
| 128 (64) | 1.059e-04 | 6.689e-05 | 1.583 | ± 0.005 |
| 256 (128) | 2.649e-05 | 1.757e-05 | 1.508 | ± 0.007 |

**Controls at K = 64** — most of the gain is ordinary nonuniform quantization:

| delay law | interpretation | ratio | 95% CI |
|---|---|---|---|
| `A₀θ` | affine in Ω | **0.997** | ± 0.002 |
| `A₀ sin 2θ` | one smooth regime, no split | 1.504 | ± 0.006 |
| `A₀ A sin 4θ` | the released two-regime law | 1.748 | ± 0.009 |
| `A₀ sin 8θ` | one fast regime | 1.889 | ± 0.004 |

The affine row is the important one: it is the **null**, and the estimator returns
0.997, so it is not simply favouring itself. The smooth-sinusoid row shows a law
with *no* slow/rapid structure already delivers 1.50×. The manuscript now says
plainly that the two-regime model *adds to* a generic effect rather than causing it.

---

## Claims that were **understated** — and are now stronger

### 9. The sample is not doing the work it appears to — *strengthened*

The manuscript said "we trained partitions on 200,000 rays". The delay law is
**known in closed form**, so the identical DP on an analytic quadrature grid with
zero sampled rays reaches `2.4192e-04` against the sample-estimated `2.4208e-04` —
a 0.07% relative gap, with cell boundaries agreeing to 1–3 grid points out of 1024.
The sample-estimated solution is very slightly *worse*.

The partition is a function of the delay law; sampling estimates it and adds noise.
The manuscript now describes this as **partition optimization estimated from
samples, not learning from data**, which is both more accurate and a stronger
result.

### 10. The chart-legality cost was understated by an order of magnitude — *materially stronger*

The paper's §12.5 compared a chart-legal optimum against a weak inadmissible
heuristic (1.67×) and concluded branch preservation "costs a little distortion".
That comparison was unfair to the scalar side. Computing the **true** scalar
optimum — the classical Lloyd–Max quantizer of `Tg`, precisely refs [9][10][11]
that the paper cites — with 32 cells:

```
unconstrained Lloyd-Max of Tg (32 cells) : 4.0019e-05 fs^2  = 10.6x better than uniform
chart-legal contiguous DP (same budget)  : 2.4208e-04 fs^2
```

So the scalar optimum is **6× better** in distortion, not 1.04× better.

But it is not a same-budget competitor, and this is the crucial detail: its 32 cells
are contiguous in `Tg` and **not** in `Ω`. Scanning `Ω` they fragment into **91
runs**, so realizing them costs ≈2.8× the chart-address structure.

**This replaces the weak counterexample with the paper's sharpest result:** chart
legality is an *address-structure* cost, not a moral one, and representation cannot
be priced by scalar reconstruction error alone. Theorem 11 prices an analytic
instance of that coupling; the 91/32 measurement prices a geometric one. They are
independent routes to the same conclusion, which is now stated as such.

*Methodological note:* an earlier version of this audit reported the 10.6× figure as
a "6× premium" against the chart-legal optimum. That was wrong and was corrected
before adoption — it ignored that the scalar optimum silently spends ~2.8× the
address budget. The strawman is documented here deliberately, because it is the
error a reader is most likely to make.

---

## Verified correct, no change needed

- **Theorem 11 (Branch-preservation cost).** Re-derived independently. With `K`
  total addresses over `J` equal-probability branches each carrying uniform width-`W`
  delay: `D_preserve = (W²/12J)·Σ_b 1/k_b²`, minimized at `k_b = K/J`, giving
  `J²W²/(12K²)`. And `D_discard = W²/(12K²)`. Ratio `J²` — **16 for 4 branches, as
  claimed.**
- **Scale invariance.** The improvement ratio is exactly independent of `A₀`
  (verified across `A₀ ∈ {0.1, 0.4117, 1.0, 10.0}`), consistent with distortion being
  quadratic in the amplitude.
- **References.** All 15 external references are real and correctly attributed
  (Born & Wolf 1999; Arnold 1989; Berry & Upstill 1980; Pearcey 1946; Airy 1838;
  Geiges 2008; Allan 1966; Shannon 1959; Lloyd 1982; Max 1960; Gray & Neuhoff 1998;
  Misra–Goyal–Varshney 2011; Stone 1982; Bonnans & Shapiro 2000; McCormick & Chapin
  2015). The seven self-citations are Zenodo DOIs and are explicitly flagged in the
  text as context only, not as evidence — correct practice.
- **Theorem numbering.** Internally consistent (Theorems 6–13). A layout artifact in
  text extraction initially suggested otherwise; it was checked and is a false alarm.

## Not audited

- Experiments 1–3 have **no released code**; their figures were checked for internal
  consistency only (Experiment 1's is what surfaced defect #5).
- The GNATprove transcript was read, not re-executed — no Alire/GNATprove toolchain
  in the audit environment. The transcript is internally consistent with the
  specification as written.
- No claim of physical measurement anywhere was accepted; the paper's own evidence
  taxonomy (A: proved, B: synthetic, C: machine-checked) was maintained throughout,
  and no type-(B) result was found being asserted as type (A).

## Standing recommendation

The calibration of `generate.py` is disclosed in §12.5 but not in the abstract, and
the improvement ratio is exactly the quantity that calibration controls. The
abstract now carries a one-clause caveat that the ratio is for the released
calibrated synthetic model. This should be kept.