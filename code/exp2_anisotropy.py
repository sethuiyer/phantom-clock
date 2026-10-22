#!/usr/bin/env python3
"""Experiment 2: uniform shell indices are not uniform physical sampling.

Pure calculus on the released parametrization of Sec. 3,

    x = rho (1 + alpha rho^2) u_x,   y = rho u_y,   z = rho (1 - beta rho^2) u_z,

with alpha, beta > 0 and beta < 1/3 (so dz/drho > 0 at rho = 1).

No calibration constants are fitted here; every number is a closed-form
derivative of the stated parametrization, so this script either reproduces the
paper exactly or the paper is wrong.

Reproduce:  python3 exp2_anisotropy.py
"""
ALPHA = 0.2
BETA = 0.2


def dx_drho(rho, alpha=ALPHA):
    """d/drho [ rho + alpha rho^3 ] = 1 + 3 alpha rho^2."""
    return 1.0 + 3.0 * alpha * rho * rho


def dz_drho(rho, beta=BETA):
    """d/drho [ rho - beta rho^3 ] = 1 - 3 beta rho^2."""
    return 1.0 - 3.0 * beta * rho * rho


def main():
    print(f"alpha = {ALPHA}, beta = {BETA}")
    print(f"beta < 1/3 keeps dz/drho > 0 at the boundary: "
          f"{1.0 - 3.0 * BETA:.3f} > 0\n")

    print(f"{'rho':>5} {'dx/drho':>9} {'dz/drho':>9} {'ratio':>7}")
    for rho in (0.0, 0.25, 0.5, 0.72, 0.9, 1.0):
        a, c = dx_drho(rho), dz_drho(rho)
        print(f"{rho:5.2f} {a:9.4f} {c:9.4f} {a / c:7.3f}")

    print("\nBoundary values and the two published claims:")
    a1, c1 = dx_drho(1.0), dz_drho(1.0)
    print(f"  dx/drho(1) = 1 + 3*alpha = {a1:.3f}   (paper: 1.6)")
    print(f"  dz/drho(1) = 1 - 3*beta  = {c1:.3f}   (paper: 0.4)")
    print(f"  ratio                    = {a1 / c1:.3f}:1   (paper: 4:1)")
    print(f"  excess displacement near boundary vs centre, x-axis: "
          f"{a1 / dx_drho(0.0) - 1.0:.0%}   (paper: ~60%)")

    # The ratio is bounded: as rho -> 1 with beta -> 1/3 the denominator
    # vanishes, so the disparity is not merely 4:1 for every admissible
    # (alpha, beta) -- worth stating, since the paper quotes one parameter pair.
    print("\nSensitivity (the 4:1 figure is the quoted parameter pair, not a bound):")
    for alpha, beta in ((0.2, 0.2), (0.5, 0.2), (0.2, 0.3), (1.0, 0.32)):
        a, c = 1.0 + 3.0 * alpha, 1.0 - 3.0 * beta
        print(f"  alpha={alpha:4.2f} beta={beta:4.2f}  ->  ratio {a / c:7.2f}:1")


if __name__ == "__main__":
    main()
