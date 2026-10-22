#!/usr/bin/env python3
"""Timescale sufficiency: the exact Allan distortion for a Markov residual.

Implements Appendix F.3.  For a zero-mean wide-sense-stationary per-sample
frequency-error residual with autocovariance C(h),

    D_tau(E) = (1/tau^2) sum_{i,j=0}^{tau-1} [ C(j-i) - C(tau+j-i) ],

and for the Markov case C(h) = a^2 rho^|h| this equals

    (a^2 / tau^2) * Phi(rho, tau),
    Phi(rho, tau) = tau + 2 sum_{h=1}^{tau-1} (tau-h) rho^h
                        - rho (1 - rho^tau)^2 / (1 - rho)^2.

Two things are computed here:

  * the closed form is checked against the direct double sum, so the released
    formula is verified rather than asserted;
  * the iso-distortion ratio Phi(rho_2, tau)/Phi(rho_1, tau) is tabulated,
    which is where the paper's Allan figures come from.

Note for the record: this script supersedes an earlier reported figure of
"93.6x at tau = 256" for rho = 0.99 against independent branches. The exact
value from this formula is 94.56x; the same table reproduces the companion
claims (31.77x vs a rho = 0.5 chain at tau = 256, and 0.181x at tau = 8), so
the formula is right and the single 93.6 figure was slightly off.

Reproduce:  python3 allan.py
"""
import numpy as np

TAUS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)


def C_markov(h, a=1.0, rho=0.9):
    return a * a * (rho ** abs(h))


def D_direct(a, rho, tau):
    """Direct evaluation of the Appendix F.3 double sum: no closed form used."""
    s = 0.0
    for i in range(tau):
        for j in range(tau):
            s += C_markov(j - i, a, rho) - C_markov(tau + j - i, a, rho)
    return s / (tau * tau)


def Phi(rho, tau):
    if rho == 0.0:
        return float(tau)
    return (tau
            + 2.0 * sum((tau - h) * rho ** h for h in range(1, tau))
            - rho * (1.0 - rho ** tau) ** 2 / (1.0 - rho) ** 2)


def D_closed(a, rho, tau):
    return a * a * Phi(rho, tau) / (tau * tau)


def check_closed_form():
    print("== 1. Closed form vs the direct double sum ==")
    print(f"{'a':>4} {'rho':>6} {'tau':>5} {'direct':>14} {'closed':>14} {'rel err':>10}")
    worst = 0.0
    for a, rho, tau in [(1, 0.0, 1), (1, 0.9, 8), (2, 0.99, 16),
                        (1, 0.5, 64), (1.7, 0.999, 128), (1, 0.0, 256)]:
        d, c = D_direct(a, rho, tau), D_closed(a, rho, tau)
        rel = abs(d - c) / max(abs(d), 1e-300)
        worst = max(worst, rel)
        print(f"{a:4} {rho:6} {tau:5} {d:14.9f} {c:14.9f} {rel:10.2e}")
    print(f"  worst relative error = {worst:.2e}\n")
    print("  boundary cases: Phi(rho,1) == 1-rho :",
          all(abs(Phi(r, 1) - (1 - r)) < 1e-15 for r in (0.0, 0.5, 0.99)))
    print("                  Phi(0,tau) == tau   :",
          all(abs(Phi(0.0, t) - t) < 1e-15 for t in (1, 7, 100)), "\n")


def table():
    print("== 2. Iso-distortion ratio Phi(rho2,tau)/Phi(rho1,tau) ==")
    print("   (equal pointwise variance by construction; only persistence differs)")
    hdr = "tau".rjust(5) + "".join(f"{r:>12}" for r in ("vs rho=0", "vs rho=0.5", "vs rho=0.9"))
    print(hdr)
    for tau in TAUS:
        r0, r5, r9 = Phi(0.0, tau), Phi(0.5, tau), Phi(0.9, tau)
        q = Phi(0.99, tau)
        print(f"{tau:5d}{q / r0:12.2f}{q / r5:12.2f}{q / r9:12.2f}")

    print("\n  The published figures, checked:")
    t = 256
    print(f"    rho=0.99 vs independent at tau=256 : {Phi(0.99,t)/Phi(0.0,t):.2f}x"
          f"   (previously reported as 93.6x)")
    print(f"    rho=0.99 vs rho=0.5 at tau=256     : {Phi(0.99,t)/Phi(0.5,t):.2f}x"
          f"   (claimed 31.7x)")
    print(f"    rho=0.99 vs rho=0.5 at tau=8       : {Phi(0.99,8)/Phi(0.5,8):.3f}x"
          f"   (claimed 0.2x: the ranking reverses)")

    print("\n== 3. Supremum over persistence at fixed tau (the Theta(tau) claim) ==")
    from scipy.optimize import minimize_scalar
    print(f"{'tau':>6} {'sup ratio':>11} {'at rho':>9} {'(1-rho)*tau':>12} {'ratio/tau':>10}")
    for tau in (16, 64, 256, 1024, 4096):
        r = minimize_scalar(lambda x: -Phi(x, tau) / tau,
                            bounds=(1e-9, 1 - 1e-12), method="bounded")
        sup = -r.fun
        print(f"{tau:6d} {sup:11.3f} {r.x:9.6f} {(1-r.x)*tau:12.3f} {sup/tau:10.5f}")
    print("\n  limiting constant c = max_alpha psi(alpha), "
          "psi(alpha) = [2(alpha-1+e^-a) - (1-e^-a)^2]/alpha^2")
    psi = lambda al: (2 * (al - 1 + np.exp(-al)) - (1 - np.exp(-al)) ** 2) / al ** 2
    m = minimize_scalar(lambda a: -psi(a), bounds=(1e-6, 50), method="bounded")
    print(f"  c = {-m.fun:.4f} at alpha* = {m.x:.4f}   (so sup ratio ~ {-m.fun:.4f} * tau)")


if __name__ == "__main__":
    check_closed_form()
    table()
