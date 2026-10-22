# The Bullock Cart to the Riemann Hypothesis

### How an innocent optics problem led us through memory corruption, closed light rays, prime numbers, blackbody radiation, and the most notorious unsolved problem in mathematics

*An adventure in optical phase space, dynamical systems, quantum graphs, and the fine structure of the primes.*

---

## 1. It Started With a Clock That Wasn't Broken

Imagine building an instrument capable of measuring changes in the arrival time of light at the femtosecond scale.

One femtosecond is \(10^{-15}\) seconds. Light travels approximately 300 nanometres in that time.

At this scale, seemingly harmless computational decisions become consequential. An instrument might correctly detect a pulse, faithfully digitize its signal, and still report timing fluctuations that were never present in the underlying physical process.

The culprit could be something as mundane as a memory address.

Suppose two rays of light arrive at the same spatial position from different directions. A conventional three-dimensional indexing system records their positions as identical. If the rays have different optical histories, however, they may carry different accumulated group delays.

The memory system merges them.

The calibration algorithm subsequently treats their distinct delays as though they belonged to one physical state. When it subtracts a common correction, a residual appears.

The clock seems noisy.

But the clock is fine.

**The representation manufactured the apparent noise.**

This was the starting point of my optics research: the observation that memory representation cannot always be treated as a passive engineering detail. When the representation erases distinctions relevant to an observable, it becomes part of the measurement process itself.

The natural remedy is to represent not merely where a ray is, but also where it is going.

A ray in three-dimensional space requires three position coordinates and two independent direction coordinates:

\[
q=(x,y,z,\theta,\phi).
\]

That gives us a five-dimensional optical state space.

The original project investigated how to assign such states contiguous integer memory addresses while preserving ray-branch identity, maintaining chart ownership, respecting finite memory budgets, and minimizing measurement distortion.

The implementation used Ada/SPARK and GNATprove to check address-range and injectivity properties for a concrete encoder instance. The released prototype discharged 47 proof obligations.

An associated synthetic partitioning experiment found approximately a 1.746-fold reduction in timing distortion relative to uniform angular partitioning for a calibrated reference model.

That result was reproducible, although later auditing showed that much of the improvement reflected ordinary nonuniform quantization rather than an exclusively optical effect.

But neither the memory architecture nor the optimization result was the strangest part of the investigation.

The strangest part appeared when we asked what happens when light comes back.

## 2. The Ray That Returned Home With More Time

Imagine a ray travelling through an optical system containing a closed trajectory.

After completing one circuit, the ray returns to precisely the same position and propagation direction.

Its instantaneous five-dimensional state is unchanged:

\[
q(t_1)=q(t_2).
\]

But the ray has travelled some distance, and that journey has taken time.

Its accumulated group delay is

\[
T_g=\int_\gamma \frac{n_g(x,\omega)}{c}\,d\ell,
\]

where \(n_g\) is the group refractive index.

After one complete circuit, the accumulated delay has increased by

\[
G_\gamma=\oint_\gamma \frac{n_g}{c}\,d\ell.
\]

After two circuits, it has increased by \(2G_\gamma\).

After \(m\) circuits:

\[
\Delta T_g=mG_\gamma.
\]

Yet the instantaneous state can remain exactly the same.

This exposes a deeper limitation than the original caustic problem.

At a caustic, two different directions can occupy the same position. Moving from three coordinates to five can distinguish them.

But a closed orbit creates two different histories with the same position and direction.

No instantaneous five-dimensional address can distinguish the number of completed circuits unless additional history information is retained.

One may need a winding counter, an accumulated-delay variable, or another representation of the trajectory's history.

This was the first unexpected bridge to a different mathematical world.

Because mathematics has an entire language for studying closed trajectories, their repetitions, and the information encoded in their periods.

That language leads to dynamical zeta functions.

And dynamical zeta functions lead, rather surprisingly, toward prime numbers.

## 3. The Five-Dimensional Geometry Behind the Light

The optical system can be described using Hamiltonian mechanics.

At a fixed optical frequency \(\omega_0\), a dispersion relation constrains the momentum magnitude:

\[
|p|=\frac{n_p(x,\omega_0)}{c},
\]

where \(n_p\) is the phase refractive index.

The corresponding fixed-frequency manifold has five dimensions.

On the cotangent bundle of physical space, the canonical one-form is

\[
\lambda=p\cdot dx.
\]

Restricting it to the fixed-frequency manifold gives

\[
\alpha=\lambda|_{M_{\omega_0}}.
\]

Under the appropriate regularity and contact-type assumptions, this becomes a contact form.

Contact geometry is an odd-dimensional relative of symplectic geometry. It naturally describes constrained Hamiltonian dynamics, including optical rays on suitable energy surfaces.

Associated with a contact form is a distinguished vector field called the Reeb vector field, defined by

\[
\alpha(R_\alpha)=1,
\]

and

\[
\iota_{R_\alpha}d\alpha=0.
\]

In our optical setting, the Reeb trajectories follow the characteristic rays, up to a change of parameter.

Now consider a closed Reeb orbit \(\gamma\).

Because \(\alpha(R_\alpha)=1\), its Reeb period is

\[
T_\gamma^{(p)}=\oint_\gamma\alpha.
\]

For the optical momentum,

\[
p=\frac{n_p}{c}\hat{\mathbf t},
\]

this becomes

\[
\boxed{
T_\gamma^{(p)}
=
\oint_\gamma\frac{n_p}{c}\,d\ell.
}
\]

That is the closed-orbit phase travel time.

The group delay is a related but distinct quantity:

\[
\boxed{
G_\gamma=
\oint_\gamma\frac{n_g}{c}\,d\ell.
}
\]

The distinction matters. Phase propagation determines the ray dynamics; group delay describes the observable accumulated along the ray.

Writing

\[
r(q)=\frac{n_g(q)}{n_p(q)},
\]

we obtain

\[
G_\gamma
=
\int_0^{T_\gamma^{(p)}}r(\phi^tq)\,dt.
\]

Thus group delay is a weighted period of the underlying Reeb flow.

We now possess two related spectra of closed-ray quantities: phase actions and group-delay periods.

The original memory problem had unexpectedly produced the raw material for periodic-orbit spectral theory.

## 4. A Zeta Function Made From Light

Let \(\mathcal P\) denote the set of primitive closed optical trajectories.

A primitive orbit is one that is not merely several repetitions of a shorter orbit.

For every \(\gamma\in\mathcal P\), let \(G_\gamma\) be its positive group-delay period.

Introduce a reference time \(T_*\), and define the formal Euler product

\[
\boxed{
Z_{\mathrm{opt}}(s)
=
\prod_{\gamma\in\mathcal P}
\left(1-e^{-sG_\gamma/T_*}\right)^{-1}.
}
\]

For suitable dynamical systems, such products converge in a right half-plane and may admit further analytic continuation. For a general optical Reeb flow, those analytic properties must be established rather than assumed.

Why use this particular expression?

Because it automatically records repetitions.

Taking logarithms,

\[
\log Z_{\mathrm{opt}}(s)
=
\sum_{\gamma\in\mathcal P}
\sum_{m=1}^{\infty}
\frac{e^{-smG_\gamma/T_*}}{m}.
\]

The index \(m\) counts how many times a primitive orbit has been traversed.

The logarithmic derivative gives

\[
-\frac{Z'_{\mathrm{opt}}(s)}
{Z_{\mathrm{opt}}(s)}
=
\sum_{\gamma\in\mathcal P}
\sum_{m=1}^{\infty}
\frac{G_\gamma}{T_*}
e^{-smG_\gamma/T_*}.
\]

Now define the periodic-orbit delay distribution

\[
\Theta_{\mathrm{opt}}(t)
=
\sum_{\gamma\in\mathcal P}
\sum_{m=1}^{\infty}
G_\gamma\,
\delta(t-mG_\gamma).
\]

Its Laplace transform satisfies

\[
\boxed{
\mathcal L\Theta_{\mathrm{opt}}(s)
=
-T_*\frac{Z'_{\mathrm{opt}}(sT_*)}
{Z_{\mathrm{opt}}(sT_*)}.
}
\]

This is an exact identity wherever the sums and products converge appropriately.

The zeta function packages the closed-ray delays. Its logarithmic derivative recovers the distribution of primitive orbits and their repetitions.

Notice the conceptual reversal.

Our original memory architecture struggled because the instantaneous state forgot how many circuits had occurred.

The dynamical zeta function is explicitly organized around that repetition information.

The same missing historical distinction that caused trouble for the memory representation is central to the periodic-orbit description.

Then we noticed something familiar about the Euler product.

## 5. The Prime Numbers Enter the Room

For \(\Re(s)>1\), the Riemann zeta function has the Euler product

\[
\boxed{
\zeta(s)
=
\prod_{p\ \mathrm{prime}}
(1-p^{-s})^{-1}.
}
\]

Its logarithmic derivative is

\[
-\frac{\zeta'(s)}{\zeta(s)}
=
\sum_p\sum_{m=1}^{\infty}
(\log p)p^{-ms}.
\]

Compare this with our optical construction:

\[
-\frac{Z'_{\mathrm{opt}}(s)}
{Z_{\mathrm{opt}}(s)}
=
\sum_\gamma\sum_{m=1}^{\infty}
\frac{G_\gamma}{T_*}
e^{-smG_\gamma/T_*}.
\]

The structures are nearly identical.

The dictionary is

| Optical dynamics | Arithmetic |
|---|---|
| Primitive closed orbit \(\gamma\) | Prime \(p\) |
| Repeated orbit \(\gamma^m\) | Prime power \(p^m\) |
| Dimensionless period \(G_\gamma/T_*\) | \(\log p\) |
| Optical Euler product | Riemann Euler product |

If a closed optical orbit has

\[
G_{\gamma_p}=T_*\log p,
\]

then its Euler factor is exactly

\[
(1-p^{-s})^{-1}.
\]

This is the first precise connection.

Not that rays mysteriously *are* primes.

Rather, primitive periodic orbits and prime numbers occupy corresponding positions in two Euler-product constructions.

This analogy is well established in dynamical systems, Selberg theory, and quantum chaos.

The interesting question is whether it can be made into a useful mathematical or physical model.

So we decided to build one.

## 6. The First Bullock Cart: One Optical Loop Per Prime

Begin with the easiest possible construction.

Assign one optical loop to each prime number.

Let the loop associated with \(p\) have length

\[
L_p=\frac{cT_*}{n_g}\log p.
\]

Its group-delay period is then

\[
G_p=\frac{n_gL_p}{c}=T_*\log p.
\]

For \(T_*=1\) nanosecond and \(n_g=1.5\), the first few lengths are approximately:

| Prime | Loop length |
|---|---:|
| 2 | 13.85 cm |
| 3 | 21.96 cm |
| 5 | 32.17 cm |
| 7 | 38.89 cm |
| 11 | 47.92 cm |
| 13 | 51.26 cm |

The corresponding optical Euler product is

\[
Z_N(s)
=
\prod_{p\le p_N}(1-p^{-s})^{-1}.
\]

Exactly the truncated Riemann Euler product.

This looks exciting for approximately five seconds.

Then the obvious problem appears.

We manually encoded the primes into the loop lengths.

The optical system did not discover prime numbers. It was handed them.

Moreover, a finite Euler product cannot reproduce the nontrivial zeros of the analytically continued Riemann zeta function.

So this construction demonstrates the dictionary, but not a path to proving the Riemann Hypothesis.

The next challenge was to remove the explicit one-loop-per-prime encoding.

Could a small optical network generate many prime-like orbit lengths automatically?

## 7. A Three-Loop Machine for Generating Orbits

Consider a bouquet graph: one junction connected to three loops.

Call their lengths

\[
\ell_1,\ell_2,\ell_3.
\]

A trajectory travelling through the junction can follow symbolic sequences such as

\[
a,\quad b,\quad ab,\quad abc,\quad aab,\quad abac.
\]

A closed word has total length

\[
L(w)=n_1(w)\ell_1+n_2(w)\ell_2+n_3(w)\ell_3.
\]

We identify cyclic rotations of a word, and exclude words that are repetitions of shorter words.

The resulting primitive cyclic words provide a combinatorial model of primitive periodic orbits.

Crucially, three loop lengths generate infinitely many periodic words.

We no longer need to build a separate loop for every prime.

But there is a mathematical obstruction.

All orbit lengths lie in the additive group generated by the three fundamental lengths:

\[
\Lambda=\mathbb Z\ell_1+\mathbb Z\ell_2+\mathbb Z\ell_3.
\]

By contrast, the logarithms of distinct primes are linearly independent over the rationals.

To see why, suppose

\[
\sum_{j=1}^{N}q_j\log p_j=0
\]

for rational coefficients \(q_j\).

Clear the denominators and exponentiate:

\[
\prod_{j=1}^{N}p_j^{m_j}=1.
\]

Unique prime factorization forces every \(m_j=0\).

Therefore every \(q_j=0\).

A finite-rank additive length system cannot exactly contain the logarithms of arbitrarily many distinct primes.

So an exact infinite prime-length spectrum is impossible for this ordinary finite graph model.

But finite-window approximation remains possible.

And that is what we tested.

## 8. Fitting the First Fifty Prime Logarithms

We considered the primitive cyclic-word spectrum of a three-symbol bouquet and optimized its three lengths against the first fifty values

\[
\log2,\log3,\log5,\ldots.
\]

The exploratory fit produced approximately

\[
\boxed{
\ell_1=0.71745,\qquad
\ell_2=1.13196,\qquad
\ell_3=1.66210.
}
\]

The reported root-mean-square relative error was approximately 1.48%, with a worst-case relative error around 4.96%.

These are dimensionless optical lengths, and the fit is specific to the chosen finite-window model and orbit enumeration.

The result does not demonstrate a unique or natural connection to primes. It is an inverse-design fit.

But the next observation explained why such a fit could work at all.

For a three-symbol suspension flow, the topological entropy \(h\) is determined by

\[
e^{-h\ell_1}+e^{-h\ell_2}+e^{-h\ell_3}=1.
\]

The fitted lengths gave approximately

\[
h\approx1.00013.
\]

That is remarkably close to one.

Why does one matter?

Because prime numbers and primitive periodic orbits have analogous counting laws.

## 9. The Prime Number Theorem Hiding in Orbit Growth

The prime number theorem says

\[
\pi(x)\sim\frac{x}{\log x},
\]

where \(\pi(x)\) counts primes up to \(x\).

Substitute

\[
x=e^T.
\]

Then

\[
\pi(e^T)\sim\frac{e^T}{T}.
\]

For suitable hyperbolic dynamical systems, the prime-orbit theorem gives

\[
N_{\mathrm{orb}}(T)
\sim
\frac{e^{hT}}{hT}.
\]

The resemblance is immediate.

When

\[
h=1,
\]

both leading counting laws become

\[
\boxed{
N(T)\sim\frac{e^T}{T}.
}
\]

This is the real explanation for the success of the finite-window length fit.

The number of primitive symbolic orbits grows exponentially with the available period, with a correction arising from identifying cyclic repetitions.

The number of primes below \(e^T\) follows an analogous asymptotic law.

Inverting these counting functions produces approximately logarithmic growth for the ordered orbit periods and the logarithms of successive primes.

The two sequences have compatible large-scale structure.

This is not a new discovery about prime numbers. The prime-orbit theorem is a classical result, and the analogy with the prime number theorem is part of its motivation.

What our experiment did was make the analogy computationally tangible.

A tiny three-loop model could imitate the coarse growth of prime logarithms.

But that left a much harder question.

Does it imitate the fluctuations?

## 10. Where the Prime-Like Machine Broke

Matching a smooth counting law is not the same as matching the arithmetic structure of primes.

To test the difference, we compared two counting residuals.

For the prime numbers:

\[
R_{\mathrm{prime}}(T)
=
\pi(e^T)-\operatorname{Li}(e^T).
\]

For the optical graph:

\[
R_{\mathrm{orb}}(T)
=
N_{\mathrm{orb}}(T)-\operatorname{Li}(e^T).
\]

The graph lengths were normalized so that the entropy was exactly one.

Primitive cyclic-word counts were computed using combinatorial necklace enumeration, rather than relying on a brute-force list of every word.

At the exploratory endpoint \(T=11.8\), the reported values were approximately:

| Quantity | Value |
|---|---:|
| \(e^T\) | 133,252 |
| Prime count | 12,434 |
| Primitive orbit count | 12,496 |
| \(\operatorname{Li}(e^T)\) | 12,481 |

The leading counts were close.

But the residual fluctuations were not.

The reported correlations were approximately:

| Comparison | Correlation |
|---|---:|
| Raw counting residuals | 0.24 |
| Normalized residuals | 0.23 |
| First-differenced residuals | −0.023 |
| Log-power spectral profiles | 0.15 |

The first-difference correlation was essentially zero.

The graph reproduced the coarse prime-like growth but not the detailed arithmetic fluctuations.

This is an important negative result.

It separates two different phenomena:

\[
\boxed{
\text{Exponential orbit growth}
\neq
\text{Riemann-zero arithmetic structure}.
}
\]

Topological entropy controls the leading proliferation of periodic orbits.

It does not automatically produce the delicate correlations encoded by the nontrivial zeros of the Riemann zeta function.

In fact, the arithmetic fluctuations are where the deepest part of the Riemann Hypothesis enters.

The Riemann Hypothesis is not simply a statement that primes grow at approximately the right rate.

It is a statement about the locations of the nontrivial zeros of \(\zeta(s)\), with powerful consequences for the error terms in prime counting.

Our three-loop machine had reached the prime number theorem's neighborhood.

It had not reached the Riemann Hypothesis.

That was exactly the distinction the experiment needed to expose.

## 11. From Optical Orbits to a Wave Spectrum

So far, we had been studying classical closed paths.

But optics is a wave phenomenon.

Could the periodic-orbit structure survive when we moved from classical trajectories to actual wave eigenmodes?

Quantum graphs provide a useful setting for answering this.

A quantum graph is a metric graph equipped with a differential operator, usually a graph Laplacian, and boundary conditions at its vertices.

For a self-adjoint graph Laplacian, its wave numbers are real.

The spectrum is determined by a secular equation of the form

\[
\det(I-U(k))=0,
\]

where \(U(k)\) combines propagation phases along graph bonds with vertex scattering amplitudes.

The important feature is that quantum graphs possess exact periodic-orbit trace formulas.

Their spectral density can be decomposed into a smooth Weyl contribution and an oscillatory contribution from periodic trajectories:

\[
\rho(k)=\bar\rho(k)+\delta\rho(k).
\]

Schematically,

\[
\delta\rho(k)
=
\frac1\pi\operatorname{Re}
\sum_{\gamma}
\sum_{m\ge1}
L_\gamma A_\gamma^m
e^{imkL_\gamma}.
\]

The amplitudes \(A_\gamma\) depend on scattering at the graph vertices.

This is an actual connection between the classical orbit structure and the wave spectrum.

We tested a three-loop graph using Kirchhoff–Neumann vertex conditions.

For the fitted loop lengths, the exploratory calculation reported 1,340 resonances below \(k=1200\), compared with a leading Weyl estimate of approximately 1,341.30.

The agreement supported the basic spectral-counting implementation.

After subtracting the smooth Weyl density and Fourier-transforming the spectral residual, peaks appeared in the length domain.

The first twenty prime-log targets were reported to lie within approximately 1.94% RMS of detected peaks.

The primitive-orbit support comparison for the first thirty prime logs gave approximately 1.74% RMS error.

A control study using 500 random entropy-one three-loop length sets reported a median error of approximately 5.66%, with none outperforming the tuned graph under that comparison.

These are exploratory numerical results, not evidence of the Riemann Hypothesis. The lengths were optimized using prime information, and nearest-peak matching can be affected by spectral crowding, degeneracies, resolution, and the chosen objective.

Nevertheless, the wave experiment answered one useful question.

**The designed classical orbit-length structure left an observable fingerprint in the quantum-graph spectrum.**

That is precisely the kind of classical-to-wave correspondence needed for a meaningful optical experiment.

And then came a strange association.

Blackbody radiation.

## 12. Why Blackbody Radiation Suddenly Made Sense

A blackbody is a system in thermal equilibrium that emits radiation with a spectrum governed by temperature.

The familiar Planck law is often written as a smooth function of frequency.

But underneath that smooth spectrum lies a count of electromagnetic modes.

For a general cavity, the thermal energy per mode is

\[
\bar E(\omega,T)
=
\frac{\hbar\omega}
{e^{\hbar\omega/(k_BT)}-1},
\]

excluding the zero-point contribution.

If the cavity has density of states \(\rho(\omega)\), then its thermal spectral energy can be written schematically as

\[
u(\omega,T)
=
\bar E(\omega,T)\rho(\omega).
\]

Now decompose the density of states:

\[
\rho(\omega)
=
\bar\rho_{\mathrm{Weyl}}(\omega)
+
\delta\rho_{\mathrm{orbit}}(\omega).
\]

The thermal spectrum becomes

\[
\boxed{
u(\omega,T)
=
u_{\mathrm{smooth}}(\omega,T)
+
\bar E(\omega,T)
\delta\rho_{\mathrm{orbit}}(\omega).
}
\]

The smooth part reflects the average mode density.

The correction contains geometry-dependent spectral structure.

This is the connection to periodic orbits.

A cavity's classical closed trajectories influence its wave spectrum. Its wave spectrum, in turn, influences its equilibrium thermal energy distribution.

The thermal spectrum can therefore carry information about the geometry of closed rays.

This is not a claim that ordinary blackbody radiation contains the Riemann zeros.

It is a statement that thermal spectroscopy can, in principle, provide another readout of a system's mode density.

Our numerical experiment used dimensionless thermal units and broadened the graph's discrete resonances with Gaussian profiles.

The thermal occupation factor was

\[
\frac{\omega}{e^{\omega/T}-1}.
\]

For an illustrative temperature \(T=55\) and linewidth \(\sigma=0.45\), the reported RMS thermal residual was about 43.3% of the smooth thermal component.

That percentage is not a universal physical prediction. It depends strongly on the arbitrary broadening, temperature, spectral window, coupling assumptions, and normalization.

A real thermal-emission measurement would additionally require accounting for emissivity, losses, port coupling, detector response, and the electromagnetic environment.

But the conceptual result survives those qualifications:

**A thermal spectrum can inherit the periodic-orbit fingerprint of the underlying wave system.**

This is why the blackbody connection is more than a poetic association.

There is a common architecture:

A smooth counting law.

A discrete underlying spectrum.

And corrections carrying information about geometry or arithmetic.

For the cavity, the smooth law is Weyl-like mode counting and the corrections arise from periodic trajectories.

For primes, the smooth law is logarithmic-integral counting and the corrections are governed by the zeros of the zeta function.

These are analogous decompositions, not identical physical laws.

The next question is whether the analogy can be sharpened at the operator level.

## 13. The Ihara–Bass Detour

Graphs possess another important zeta function: the Ihara zeta function.

For a finite graph, it can be defined through a product over primitive, non-backtracking closed cycles.

A remarkable identity converts that product into a determinant.

For a suitable graph with adjacency matrix \(A\), degree matrix \(D\), \(n\) vertices, and \(m\) edges, the Ihara–Bass identity takes the form

\[
\boxed{
Z_G(u)^{-1}
=
(1-u^2)^{m-n}
\det(I-uA+u^2(D-I)).
}
\]

There is also a formulation using the non-backtracking Hashimoto matrix \(B\):

\[
Z_G(u)^{-1}=\det(I-uB).
\]

An infinite-looking product over primitive cycles becomes a finite-dimensional determinant.

This is exactly the kind of transformation one would want in an orbit-to-spectrum program.

It replaces explicit enumeration of closed trajectories with a spectral object.

For a \((q+1)\)-regular graph, the Ihara zeta function has a well-known analogue of the Riemann Hypothesis.

In the Ramanujan case, the relevant nontrivial poles lie on

\[
|u|=q^{-1/2}.
\]

Under the substitution

\[
u=q^{-s},
\]

that circle becomes

\[
\boxed{\Re(s)=\frac12}.
\]

A critical line appears.

But there is an essential distinction.

The graph-theoretic critical-line statement depends on a specific spectral bound, closely related to the Ramanujan property.

It does not follow merely because a scattering matrix is unitary.

Likewise, the secular determinant of a self-adjoint quantum graph and the Ihara–Bass determinant are related members of a broad spectral-graph family, but they are not interchangeable formulas.

This distinction prevents us from accidentally manufacturing a proof of RH by changing variables.

The graph analogue has its own theorem, hypotheses, and spectrum.

The classical Riemann Hypothesis concerns the analytic continuation of the arithmetic zeta function.

To bridge them, one needs a genuine identity between the relevant spectral objects, not simply a shared critical-line notation.

Still, the detour revealed another promising mathematical feature.

The factor \(1/2\) can arise naturally from multiplicative orbit weights.

## 14. The Mysterious One-Half

Suppose a periodic orbit has length \(L_\gamma\), and its amplitude satisfies

\[
|A_\gamma|=e^{-L_\gamma/2}.
\]

If its length happens to equal \(\log p\), then

\[
|A_\gamma|=p^{-1/2}.
\]

Add an oscillatory phase:

\[
A_\gamma e^{-itL_\gamma}.
\]

Ignoring any additional orbit-dependent phase, this becomes

\[
e^{-(1/2+it)L_\gamma}.
\]

For \(L_\gamma=\log p\),

\[
\boxed{
A_\gamma e^{-itL_\gamma}
=
p^{-1/2-it}.
}
\]

That is precisely the arithmetic exponent appearing when a prime Euler factor is evaluated formally along the critical line

\[
s=\frac12+it.
\]

Could a graph generate the attenuation automatically?

If every edge traversal contributes a magnitude

\[
|a_e|=e^{-\ell_e/2},
\]

then an orbit traversing several edges has

\[
|A_\gamma|
=
\prod_{e\in\gamma}|a_e|
=
e^{-\frac12\sum_e\ell_e}
=
e^{-L_\gamma/2}.
\]

The factor \(1/2\) would emerge from multiplicative propagation.

This is mathematically straightforward to engineer in a weighted or attenuating transfer model.

It is not automatically compatible with arbitrary unitary quantum-graph scattering.

Unitarity imposes constraints on the full scattering matrix, and individual orbit amplitudes are products of its entries. Their magnitudes cannot simply be specified independently without checking those constraints.

More importantly, inserting a factor \(e^{-L/2}\) does not prove that the zeros of a resulting determinant lie on the Riemann critical line.

It reproduces one formal piece of the desired arithmetic weighting.

That is useful, but it is not the whole problem.

We now have three separate engineering objectives:

1. Generate appropriate primitive orbit lengths.
2. Generate appropriate orbit amplitudes and phases.
3. Construct a spectral determinant with the required analytic and self-adjoint structure.

The first two are inverse-design problems.

The third is where the Riemann Hypothesis becomes genuinely formidable.

## 15. Why Hilbert–Pólya Is Still a Mountain

The Hilbert–Pólya idea asks whether the nontrivial zeros of the Riemann zeta function can be interpreted through the spectrum of a self-adjoint operator.

If an operator \(H\) had eigenvalues corresponding exactly to the imaginary parts of the nontrivial zeros,

\[
H\psi_n=\gamma_n\psi_n,
\]

and if the construction established that every nontrivial zero had the form

\[
\rho_n=\frac12+i\gamma_n,
\]

then self-adjointness would force the \(\gamma_n\) to be real.

That would prove RH.

The difficulty is not merely finding a self-adjoint operator with an interesting spectrum.

Many such operators exist.

The difficulty is establishing the exact correspondence with **all** nontrivial Riemann zeros, with the correct multiplicities and no unwanted spectral objects.

Our optical graph has a self-adjoint Laplacian.

It has real eigenvalues.

It has a periodic-orbit trace formula.

It has a dynamical zeta function.

And we can tune its classical orbit lengths to resemble prime logarithms over a finite range.

But none of those facts identifies its spectral determinant with the completed Riemann zeta function.

The prime-log counting experiment made this limitation visible.

We could match the leading growth remarkably well.

Yet the residual fluctuations failed to match.

That is a miniature demonstration of the difference between reproducing a prime-number-theorem-like asymptotic and reproducing the arithmetic information associated with the Riemann zeros.

The latter requires far more rigidity.

In particular, the actual explicit formula involves precise prime-power weights, zero contributions, analytic continuation, functional-equation structure, and correction terms.

A generic graph trace formula does not acquire those features simply because its periodic orbits are numerous or its entropy equals one.

Our toy model is a useful laboratory for understanding the missing structure.

It is not a disguised proof.

## 16. What the Experiments Actually Established

It is worth separating the mathematical facts from the exploratory numerical observations.

The established mathematical ingredients include the canonical contact description of suitable optical ray systems, additive periods along closed trajectories, periodic-orbit Euler products, prime-orbit counting laws, quantum-graph trace formulas, and the Ihara–Bass determinant identity.

The exact finite-rank obstruction also follows immediately from the rational independence of logarithms of distinct primes.

The numerical experiments then investigated a particular three-loop symbolic and quantum-graph model.

They suggested that three fitted loop lengths can approximate a finite sequence of prime logarithms, that entropy normalization explains the leading counting agreement, and that the corresponding wave spectrum retains periodic-orbit information.

They also showed that the model's counting residuals did not meaningfully reproduce prime-counting fluctuations.

The thermal experiment illustrated how spectral geometry could modulate a thermal envelope, but it was not a physical blackbody measurement.

The broader RH connection remains an analogy and a research direction.

That distinction is important because the most useful result of the project was not an apparent triumph.

It was discovering exactly where a simple construction stopped working.

A model that matches the prime number theorem's leading behavior but fails on arithmetic fluctuations tells us that exponential orbit proliferation is insufficient.

A model whose finite edge-length module cannot contain every prime logarithm tells us that exact arithmetic encoding cannot emerge from that restricted additive architecture.

A weighted graph that reproduces \(p^{-1/2-it}\) formally still needs an operator-theoretic explanation for its zeros.

Each obstruction narrows the search.

That is productive mathematics.

## 17. The Next Experiments

The next stage should not optimize the three loop lengths against more prime logarithms.

That would mostly improve a finite-window fit.

Instead, the objective should move from orbit locations to spectral structure.

A useful next experiment would construct a quantum graph with tunable vertex scattering matrices and optimize a trace-formula residual, not merely a length mismatch.

The loss function could include terms measuring differences between selected arithmetic explicit-formula contributions and the graph's weighted periodic-orbit contributions.

Schematically,

\[
\mathcal J
=
\lambda_L\mathcal E_{\rm lengths}
+
\lambda_A\mathcal E_{\rm amplitudes}
+
\lambda_\phi\mathcal E_{\rm phases}
+
\lambda_S\mathcal E_{\rm spectrum}.
\]

The experiment should impose actual scattering constraints rather than treating all orbit amplitudes as independent variables.

It should also penalize unwanted short orbits, because matching a few desired periodic trajectories is meaningless if the graph produces a much larger population of unmatched ones.

A second direction would examine hyperbolic surfaces and their geodesic flows.

These have a deeper established connection between closed trajectories, trace formulas, and zeta functions than our small bouquet graph.

The Selberg trace formula and Selberg zeta function provide a rigorous example of geometry and spectral theory interacting through primitive closed geodesics.

A third direction would return to optics.

Instead of building an abstract quantum graph, we could construct a refractive-index field supporting a controlled family of closed rays, compute their phase actions and group delays, and study the resulting wave resonances.

That would reconnect the RH-adjacent mathematics to the original instrumentation problem.

A fourth direction would examine the thermodynamic readout.

Rather than using an arbitrarily broadened spectrum, a physical microwave network could be modeled with measured scattering losses and realistic coupling to a detector.

One could then compare its frequency-domain response, length spectrum, and thermal-noise spectrum.

The first goal would be to recover the known periodic-orbit fingerprints.

Only then would an arithmetic tuning experiment become meaningful.

The important point is that all these experiments have clear failure conditions.

A useful research program must be capable of producing an unambiguous negative result.

Our three-loop residual experiment already did.

## 18. The Unexpected Return to Memory

After all this mathematics, the strangest realization is that we have returned to the original problem.

We began with a memory architecture that could lose physical information.

At a caustic, different ray directions occupied the same spatial position.

On a closed orbit, different traversal histories occupied the same instantaneous optical state.

Both failures arose because the chosen representation identified objects that the measurement needed to distinguish.

The solution was not simply to increase numerical precision.

It was to preserve the correct state distinctions.

The periodic-orbit viewpoint reveals the same principle in another language.

A primitive orbit and its repetitions are not interchangeable.

The distinction between

\[
\gamma,\gamma^2,\gamma^3,\ldots
\]

is precisely what the Euler product organizes.

Likewise, prime numbers and their powers play distinct roles in the logarithmic derivative of the Riemann zeta function.

The analogy does not make optical rays arithmetic objects.

But it highlights a shared structural principle:

**The identities and repetitions of fundamental objects matter, and a representation that collapses them loses information that cannot necessarily be reconstructed afterward.**

In the optical instrument, that loss can appear as false timing noise.

In a periodic-orbit calculation, it can destroy the correct orbit spectrum.

In a spectral determinant, incorrect multiplicities or weights can produce an entirely different analytic function.

The mathematics is different in each setting, but the representation problem is recognizable.

What information must be retained so that the observable remains faithful to the underlying system?

That question was present in the original optics paper.

It survived the detour through contact geometry.

And it remains relevant even when the destination is as distant as the Riemann Hypothesis.

## 19. The Bullock Cart Stops for Lunch

Did we prove the Riemann Hypothesis?

No.

Did we accidentally discover that blackbody radiation encodes the primes?

No.

Did we construct a self-adjoint optical operator whose spectrum is exactly the set of nontrivial Riemann zeros?

Also no.

What we did was follow a legitimate chain of mathematical connections:

\[
\text{Optical phase space}
\]

\[
\downarrow
\]

\[
\text{Closed Hamiltonian/Reeb trajectories}
\]

\[
\downarrow
\]

\[
\text{Primitive orbit periods}
\]

\[
\downarrow
\]

\[
\text{Dynamical zeta functions}
\]

\[
\downarrow
\]

\[
\text{Prime-orbit counting laws}
\]

\[
\downarrow
\]

\[
\text{Quantum-graph trace formulas}
\]

\[
\downarrow
\]

\[
\text{Wave and thermal spectral fingerprints}
\]

\[
\downarrow
\]

\[
\text{Ihara–Bass determinants and spectral bounds}
\]

\[
\downarrow
\]

\[
\text{Hilbert–Pólya territory}.
\]

Along the way, we encountered an exact impossibility theorem for finite additive length spectra, an entropy-one explanation for prime-like orbit counting, a quantum-graph spectral experiment, and a negative result showing that the arithmetic fluctuations were not reproduced.

That last result is especially valuable.

It prevents a seductive but false conclusion.

Matching the number of primitive orbits to the number of primes is not the same as matching the primes themselves.

Matching prime-log lengths over a finite interval is not the same as deriving the Riemann explicit formula.

And creating a critical-line parametrization is not the same as proving that the zeros of the arithmetic zeta function lie on that line.

But the journey still has a worthwhile conclusion.

The original optics problem taught us that a data representation can create apparent physical phenomena when it forgets distinctions that matter.

The periodic-orbit investigation taught us that geometry, dynamics, and spectral theory also depend on preserving the correct distinctions among fundamental objects and their repetitions.

And the Riemann Hypothesis reminded us that matching a smooth law is often the easy part.

The hard part is explaining the fluctuations.

So the bullock cart has not reached the summit.

It has reached a point where the mountain is visible, the road behind us is mathematically legitimate, and the next obstruction is sharply defined.

That is enough for one lunch break.

**The clock was never broken. The memory was. And somehow, while fixing the memory, we ended up staring at the primes.**

---

*Technical note: The three-loop fits, spectral counts, residual correlations, and thermal-modulation values described here are exploratory numerical results from the discussed toy models. They are not independent experimental confirmations, and the RH-related constructions are not proofs or claims of new results about the nontrivial zeros of the Riemann zeta function.*
