# Release artifacts

Companion code for "Chart-Aware Contiguous Memory for Discretized Optical Phase
Space" (Sethurathienam Iyer, ORCID 0009-0008-5446-2856).

## Contents

| File | Purpose |
|---|---|
| `generate.py` | Synthetic ray generator, Experiment 5 model, train/test split rule |
| `partition.py` | Uniform / uniform-$T_g$ / DP chart-legal partitions, seed-replicated evaluation |
| `results_exp5_seeds.csv` | 30-seed per-seed results with 95% CIs |
| `scaling.py` | Budget scaling, controls, analytic partition, chart-legality cost |
| `results_exp5_scaling.csv` | Per-seed results behind the scaling and control tables |
| `chart_encoder.ads/.adb/.gpr` | SPARK verification-ready encoder specification + body |
| `test_encoder.adb` | Exhaustive runtime bijection test (Experiment 4) |
| `gnatprove-transcript.txt` | GNATprove 14.1.1 proof transcript: 47/47 obligations, 0 unproved |
| `AUDIT.md` | Third-party audit of the released artifacts (see Scope below) |
| `verified/` | **Parameterized** encoder: injectivity proved for ALL consistent tables, not one instance |
| `verified/gnatprove-general-transcript.txt` | GNATprove run: 97 obligations, 93 proved, 0 unproved |

## Experiment 5 model (exact spec)

- Two angular regimes; $T_g(\theta)$ two-regime: $A_0\sin 2\theta$ for
  $\theta<\pi/2$ (slow) and $A_0A\sin 4\theta$ for $\theta\ge\pi/2$ (rapid).
  Note "slow"/"rapid" label the oscillation *frequency*, not the amplitude:
  the slow regime's peak is $A_0=0.4117$ fs, the rapid regime's peak is
  $A_0A=0.2997$ fs.
- Delay is branch-independent, and $T_g(\theta)\neq T_g(\pi-\theta)$ except at
  $\theta=\pi/2$. So branch identity is preserved trivially by *any* contiguous
  angular partition here; it is a theoretical architectural constraint
  (Sec. 6, 12.5, Theorem 11), **not** something Experiment 5 measures.
  Experiment 5 measures chart-legal contiguous quantisation of a scalar.
- Budget $K = 64$ cells; two branches, $K/2=32$ contiguous angular cells each.
- 300,000 rays per seed under a deterministic SHA-256 80/20 split, giving
  $\sim240{,}000$ train / $\sim60{,}000$ test. Experiment 5 uses the first
  200,000 training rays and all held-out rays. Held-out count over the 30
  released seeds: $60{,}016\pm223$ (min 59,644, max 60,479; seed 0 = 60,170).
- 30 replicates.

Reproduce:

```
python3 partition.py --seeds 30 --out results_exp5_seeds.csv   # headline 1.746 +- 0.005
python3 scaling.py    --seeds 12 --out results_exp5_scaling.csv
```

## What the headline number does and does not depend on

`scaling.py` exists because the single $K=64$ ratio is not the interesting
quantity. It reports:

- **Budget scaling** — the improvement falls from $2.41\times$ at $K=16$ to
  $1.51\times$ at $K=256$. The headline is a property of the budget, not only
  of the method.
- **Controls** — a single smooth sinusoid $A_0\sin2\theta$, with no slow/rapid
  structure at all, already gives $1.50\times$; an affine law gives $0.997\times$
  (uniform bins are optimal, as they should be). Most of the gain is ordinary
  optimal nonuniform quantisation; the two-regime model adds to it.
- **Sample vs analytic** — because the delay law is known in closed form, the
  same DP on an analytic quadrature grid reaches $2.4192\times10^{-4}$ with zero
  sampled rays, matching the sample-estimated $2.4208\times10^{-4}$. The
  partition is a function of the law; sampling estimates it and adds a little
  noise. This is "partition optimisation estimated from samples", not learning.
- **Chart legality** — an unconstrained Lloyd-Max quantiser of $T_g$ reaches
  $4.0019\times10^{-5}\,\mathrm{fs}^2$ ($10.6\times$ better than uniform), but
  its 32 scalar cells fragment into **91** angular runs, i.e. $\approx2.8\times$
  the address structure. Chart legality costs address structure, not merely
  distortion; Theorem 11 prices the analogous trade analytically.

## Ada verification

Two packages are released:

* `chart_encoder.*` — the original **instance**: a three-entry literal table
  `(0,512,768)/(512,256,256)`. 47 obligations, 44 proved, 0 unproved. The proof holds
  because the table is a constant, so injectivity is true there by construction.
* `verified/general_chart_encoder.*` — the **class**: the table is a discriminated record
  passed as a value, so the contracts quantify over every consistent table up to
  `Max_Charts x Max_Arena`. 97 obligations, 93 proved, 0 unproved.

Three defects had to be fixed to get from the first to the second: the adjacency
condition cannot use a range ending at `K_Max - 1` (that underflows the index subtype at
`K_Max = 0`); the ghost lemmas need bodies, since a specification alone proves nothing;
and the monotonicity lemma is load-bearing — gutting it leaves its own postcondition
unproved and makes injectivity rest on an unproved callee contract.

```
export PATH=<gnatprove>/libexec/spark/bin:<gnatprove>/bin:$PATH
# instance
cd code && gprbuild -P chart_encoder.gpr && ./test_encoder && gnatprove -P chart_encoder.gpr --level=2
# class
cd code/verified && gprbuild -P general_chart_encoder.gpr && ./test_general \
  && gnatprove -P general_chart_encoder.gpr --level=2
```

The runtime driver in `verified/test_general.adb` checks bijectivity, arena coverage and
decode round trips on four table shapes — including the degenerate single-chart
`K_Max = 0` the instance form cannot express — plus five negative controls.

### Original instance notes



```
export PATH=<alire>/gnat_native_14.2.1/bin:<alire>/gprbuild_22.0.1/bin:<gnatprove>/bin:$PATH
gprbuild -P chart_encoder.gpr && ./test_encoder
gnatprove -P chart_encoder.gpr --level=2
```

GNATprove proves all range, initialization, and functional-contract obligations,
including the ghost injectivity lemma establishing that distinct (chart, rank) pairs
never alias. The Decode round trip closes Tier 1 (representation correctness).
This establishes claims for THIS chart table and contract structure; the general
theorem is proved mathematically in the paper (Theorem 1).

Scope of the transcript, stated plainly: the chart table is a three-entry literal
`(0,512,768) / (512,256,256)`, so injectivity holds there by construction.
`Table_Is_Consistent` is defined in the specification but is not used as any
subprogram's precondition, `Global_Rank` is an unimplemented `Import`+`Ghost`
stub (SPARK_Mode Off, so GNATprove skips it), and `test_encoder.adb` is
SPARK_Mode Off, so the exhaustive bijection test is *executed* rather than
verified. "47/47" means 47/47 obligations discharged for this encoder instance
and this contract structure — it is not verification of arbitrary chart tables.
