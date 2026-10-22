#!/usr/bin/env python3
"""Experiment 3: phase delay and group delay are not interchangeable.

The paper's claim is that conflating the phase index n_p with the group index
n_g injects a systematic ~40 fs error over a 1 m dispersive path. That claim
has exactly one free constant: the dispersion contrast (n_g - n_p), which the
paper never states. This script makes it explicit, so the number is a stated
assumption rather than a magic result.

    n_g = n_p + omega * d n_p / d omega,      T_g - T_p = (n_g - n_p) L / c.

We invert the claim to report the contrast it requires, and we show what a
realistic fused-silica dispersion delivers over the same length for comparison.
This is a scale-setting check, not a materials calculation: no Sellmeier
coefficients are used, so the "realistic" row is illustrative only.

Reproduce:  python3 exp3_dispersion.py
"""
C = 299_792_458.0          # m / s
CLAIM_FS = 40.0
CLAIM_LENGTH_M = 1.0


def contrast_for(delta_t_s, length_m):
    """(n_g - n_p) needed to produce delta_t over length_m."""
    return delta_t_s * C / length_m


def delay_s(contrast, length_m):
    return contrast * length_m / C


def group_index(n_p, omega, dn_p_domega):
    """n_g = n_p + omega dn_p/domega."""
    return n_p + omega * dn_p_domega


def main():
    dt = CLAIM_FS * 1e-15
    dn = contrast_for(dt, CLAIM_LENGTH_M)
    print("Inverting the published claim:")
    print(f"  target        : {CLAIM_FS:.1f} fs over {CLAIM_LENGTH_M:.1f} m")
    print(f"  requires      : (n_g - n_p) = {dn:.4e}")
    print(f"  check         : {delay_s(dn, CLAIM_LENGTH_M) * 1e15:.2f} fs")
    print(f"  scale-free    : (n_g - n_p) L = {dn * CLAIM_LENGTH_M:.4e} m, "
          f"i.e. {dt:.2e} s x c\n")

    print("The same contrast at other lengths (the error is linear in L):")
    for L in (0.1, 1.0, 10.0):
        print(f"  L = {L:5.1f} m  ->  {delay_s(dn, L) * 1e15:8.1f} fs")

    print("\nWhat a group index looks like, from the definition:")
    # Illustrative dispersion pair: n_p = 1.45 with modest normal dispersion.
    n_p = 1.45
    for label, dn_domega in (("weak", 5.0e-21), ("required", 5.1e-21), ("strong", 2.0e-20)):
        for lam_nm in (800.0, 1550.0):
            omega = 2.0 * 3.141592653589793 * C / (lam_nm * 1e-9)
            n_g = group_index(n_p, omega, dn_domega)
            print(f"  {label:8s} lambda={lam_nm:6.0f} nm  omega={omega:9.3e}  "
                  f"n_g - n_p = {n_g - n_p:.3e}  ->  "
                  f"{delay_s(n_g - n_p, 1.0) * 1e15:8.2f} fs over 1 m")

    print("\nReading: the 40 fs figure pins (n_g - n_p) ~ 1.2e-5. That is the")
    print("only content of the claim; whether a given glass reaches it depends on")
    print("the operating wavelength and bandwidth, which the paper does not fix.")
    print("The released artifact therefore reports the required contrast rather")
    print("than asserting a materials result it cannot support.")


if __name__ == "__main__":
    main()
