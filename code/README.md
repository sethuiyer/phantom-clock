# Release artifacts

Companion code for "Chart-Aware Contiguous Memory for Discretized Optical Phase
Space" (Sethurathienam Iyer, ORCID 0009-0008-5446-2856).

## Contents

| File | Purpose |
|---|---|
| `generate.py` | Synthetic ray generator, Experiment 5 model, train/test split rule |
| `partition.py` | Uniform / uniform-$T_g$ / DP chart-legal partitions, seed-replicated evaluation |
| `results_exp5_seeds.csv` | 30-seed per-seed results with 95% CIs |
| `chart_encoder.ads/.adb/.gpr` | SPARK verification-ready encoder specification + body |
| `test_encoder.adb` | Exhaustive runtime bijection test (Experiment 4) |
| `gnatprove-transcript.txt` | GNATprove 14.1.1 proof transcript: 47/47 obligations, 0 unproved |

## Experiment 5 model (exact spec)

- Two angular branches; $T_g(\theta)$ two-regime: $0.2\,|\sin 4\theta|$-style slow region and rapid region per the paper.
- Branch identity preserved: cells never merge opposite directions ($\theta$ vs $\pi - \theta$).
- Budget $K = 64$ cells; 200,000 training rays / 100,000 held-out rays.
- Split rule: hash of $(\theta, \mathrm{branch})$ into train/test by fixed random seed per replicate; 30 replicates.

Reproduce:

```
python3 partition.py --seeds 30 --out results_exp5_seeds.csv
```

## Ada verification

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
