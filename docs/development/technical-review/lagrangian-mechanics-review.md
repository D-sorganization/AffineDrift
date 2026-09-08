# Lagrangian Mechanics Technical Review — Issue #4261

## Scope and Authority

Epic #4009, corpus #4021 and Geometry batch #4055 govern this complete paired review. Both original sources were read in full, including all 16 exercises: Volume 0 ch11_lagrangian_mechanics.tex (8,868 inventory words) and its 964-word web companion. The initial print reading through line 330 was explicitly preliminary; subsequent reading covered the remaining source through the final exercise. Issue filing exemption was false; scoped duplicate search returned only unrelated linking issue #3900. Claim check was free; codex session technical-review-20260906 holds a lease until 2026-09-08T01:38:11.987196 UTC.

Branch fix/4261-lagrangian-mechanics-rigor starts after configuration PR #4262 metadata commit 1c845e87ad0a862419b6d846323a2fb0406dab1f. That PR has protected squash auto-merge enabled and is still checking. Replay only the new Lagrangian commits onto its eventual protected squash before first push; do not force-push or bypass protections. No commit or push may overlap any test, render or browser QA job. The original AffineDrift checkout and immutable upstream monograph remain untouched.

## Findings and Replacement Derivations

The opening presented Newtonian force balance as fatally flawed and suggested nature knows only energy. Generalized coordinates were equated with motors, all internal forces supposedly vanished, all constraints supposedly did no work, and the action principle was conflated with historical least-action formulations. The replacement states the actual classical model, local coordinates and ideal virtual-work assumptions. It derives the forced Euler–Lagrange equations from Lagrange–d'Alembert and separates stationarity from extremality and initial-value data. A corrected pendulum drawing connects the rod to the bob and distinguishes angular rate from tangential linear velocity.

For an autonomous natural Lagrangian, p=Mv and pdot=M vdot+Mdot v. The velocity bias is c=Mdot v−partial_q T, not Mdot v. First-kind symbols are gamma_ijk=(partial_k M_ij+partial_j M_ik−partial_i M_jk)/2; C_ij=sum_k gamma_ijk v_k and c_i=sum_jk gamma_ijk v_j v_k. Raising the first index with M inverse gives the second-kind connection. The original additional formula involving Mdot and inverse-entry derivatives was dimensionally and mathematically invalid.

Mass symmetry follows from the Hessian, not from the tautology that a scalar equals its transpose. The pullback sum J_i^T I_i J_i is positive-definite only if there is no nonzero coordinate velocity with zero kinetic energy. Redundant or massless variables and singular charts can violate that condition. Coordinate transformations change matrix entries and force components while preserving energy and power. Quaternion velocities are not blindly interchangeable with coordinate rates.

The correct skew identity is (Mdot−2C)_ij=sum_k(partial_i M_jk−partial_j M_ik)v_k. The original antisymmetry proof had incorrect indices and claimed that only the Christoffel factor could have the skew property. In three coordinates, adding K(v)=[v]_cross preserves both Cv and skew symmetry because Kv=0 and K is skew. A generic factor change need not preserve the matrix identity. A scalar power contraction alone does not establish the full matrix property because C depends on velocity.

G=partial_q V is the holding-force term on the left; applied gravity is −G. The general balance for E=v^T L_v−L is Edot=v^T Q−L_t. E equals T+V for the autonomous natural case; unactuated alone does not imply energy conservation. With x=q+a(t), the free-particle Lagrangian m(v+adot)^2/2 gives E=mv²/2−m adot²/2, distinct from laboratory kinetic energy. Damping yields nonincrease, not strictly negative power at rest.

The Legendre transform needs local velocity-Hessian invertibility, with stronger conditions for global invertibility. Hamiltonian flows preserve the canonical form even for explicit time dependence, while generic forced dynamics need not. Viscous damping pdot=−kq−bp/m has phase divergence −b/m. Energy, volume and symplecticity are separate properties.

For the tangent lift of a configuration symmetry, differentiating L(Phi(q),D Phi v,t)=L(q,v,t) gives L_q·xi+p·Dxi v=0. Along forced equations, d(p·xi)/dt=Q·xi. This proves conservation only when the projected force vanishes; constraints must admit the generator. Quasi-invariance by dF/dt gives charge p·xi−F. Time symmetry uses the separate energy identity. In uniform gravity, only horizontal momenta and vertical-axis angular momentum among the stated spatial symmetries are conserved; vertical momentum changes at −mg. A free particle in a uniformly rotating frame still has cyclic azimuth, with p_theta=mr²(theta_dot+Omega). Friction from a rotating table changes momentum through torque, not through coordinate change alone.

For phi(q,t)=0, ideal reaction is A^T lambda, A=D_q phi. Velocity consistency is Av+phi_t=0; acceleration bias is b_a=v^T Dqq phi_a v+2Dqt phi_a v+phi_att. The saddle system uses rows [M,−A^T] and [A,0], RHS [Q−c−G,−b]. With independent constraints and SPD M, lambda=−(AM^-1 A^T)^-1(b+AM^-1 F). Consistent initial position and velocity are required; acceleration enforcement alone cannot fix drift. Reaction power is −lambda·phi_t, so a moving support or prescribed hand path can do work. Nonholonomic Lagrange–d'Alembert variations are not generally equivalent to vakonomic endpoint variations. Unilateral force signs and friction feasibility remain additional.

Geodesic motion uses the kinetic connection when potential is constant and external force zero. Geodesic deviation concerns neighboring trajectories and curvature. Flat Euclidean polar coordinates have nonzero connection coefficients but zero curvature. Therefore a Coriolis coefficient does not demonstrate curvature, and a kinetic metric does not automatically establish contraction of controlled state dynamics.

For two uniform rods with absolute angles alpha from downward vertical, center translation and I_C=m l²/12 rotation give M11=(m1/3+m2)l1², M22=m2 l2²/3, M12=k cos Delta, k=m2 l1 l2/2. Determinant is bounded below by l1² l2²(m1 m2/9+m2²/12)>0. C=k sin Delta [[0,alpha2dot],[-alpha1dot,0]], and M12dot=−k sin Delta(alpha1dot−alpha2dot). Potential is −(m1/2+m2)g l1 cos alpha1−m2 g l2 cos alpha2/2. Physical motors map to Q_alpha=(u1−u2,u2), with power u1 alpha1dot+u2(alpha2dot−alpha1dot). The original text used center point masses while describing rods; the code used yet another matrix, indefinite at aligned unit links: [[1.5,1],[1,.5]], determinant −.25 and kinetic energy −.25 for rates (1,−2). The replacement's aligned unit matrix is [[4/3,1/2],[1/2,1/3]], determinant 7/36.

For relative arm angles from horizontal, alpha=S q+(pi/2,pi/2), S=[[1,0],[1,1]]. M_q=S^T M_alpha S, C_q=S^T C_alpha S and G_q=S^T G_alpha. The correct off-diagonal distal inertia term is m2 l2²/3, not /6. The two descriptions agree on Cartesian motion and power while using different generalized-force components.

RNEA is inverse dynamics and ABA forward dynamics; both are linear for bounded-dimension tree joints in their respective tasks. Dense forward factorization is not an inherent requirement of Lagrangian mechanics. The unsupported hundredfold speedup and unequal-task comparison are removed.

General momentum-first symplectic Euler evaluates both H gradients at (q_n,p_next). Its generating function is q_n·p_next+hH(q_n,p_next). For H=e^-2q p²/2, the regular local solution is p_next=2p/(1+sqrt(1−4h e^-2q p)), followed by q_next=q+h e^-2q p_next. The positive discriminant is required. The original old-momentum first update has area determinant 1−6z²−4z³, z=h e^-2q p, rather than one. Explicit kick–drift Verlet needs separability. The harmonic oscillator symplectic Euler matrix [[1−h²,h],[-h,1]] has determinant one for any h, yet becomes unstable above h=2. For 0<h<2 it preserves (q²+p²−hqp)/2; at h=2 generic Jordan growth remains possible. Backward error analysis is qualified by small fixed steps, regularity and boundedness; it does not guarantee an exactly conserved globally convergent modified Hamiltonian forever.

The golf synthesis relates geometry, kinetic inertia, actuator/contact maps, dynamics, mechanical power and event-specific delivery. Ground reaction can change momentum at a stationary zero-power contact. Moving hands can do work on a club subsystem. Equal/opposite interface wrenches cancel total power only with matched interface velocities; relative slip or deformation needs its own dissipation/storage accounting. Coordinate-specific C terms cannot by themselves identify an energy channel, muscle cause, optimum swing or stability proof.

## Exercise Solutions and Checks

All 16 original topics remain with corrected premises:

1. qddot−q=0, q=sinh(t)/sinh(T). The second variation is 2 integral(eta²+eta_dot²), strictly positive for nonzero admissible eta.
2. m l² theta_ddot+m g l sin theta=u−b theta_dot; Edot=u theta_dot−b theta_dot².
3. Rotating-frame p_theta=mr²(theta_dot+Omega); its derivative is the applied azimuthal generalized torque.
4. In the horizontal torque-free three-link arm, global base rotation is cyclic; its momentum is total angular momentum about the fixed base, generally a coupled expression. Relative shape momenta need not be conserved. Vertical-plane gravity generally breaks this symmetry.
5. The pullback proof needs injectivity on kinetic directions. T=(v1+v2)²/2 supplies a redundant two-coordinate semidefinite counterexample.
6. Verify Mdot, not M. The nonzero skew cross-product addition demonstrates nonuniqueness.
7. Conservation holds for any consistent initial velocity in the declared unforced autonomous model, not only release from rest.
8. p=m xdot, H=p²/(2m)+kx², pdot=−2kx, frequency sqrt(2k/m).
9. The parabola gives M=m(1+4a²x²), c=4ma²x xdot², G=2mga x, hence M xddot+c+G=0.
10. From r·rddot=−v·v, lambda=−(m v·v+r·F)/(2R²). Require r²=R² and r·v=0 initially; reaction power 2lambda r·v vanishes.
11. Direct COM and center-rotation energy agrees with the S transformation and the /3 off-diagonal distal coefficient.
12. D_alpha=[[b1+b2,−b2],[-b2,b2]], with Edot=−b1 alpha1dot²−b2(alpha2dot−alpha1dot)². Strictly negative only when a positive damper has nonzero relative rate.
13. Polar first-kind nonzero entries gamma_r theta theta=−r, gamma_theta r theta=gamma_theta theta r=r. Raising gives Gamma^r_theta theta=−r and Gamma^theta_r theta=Gamma^theta_theta r=1/r. Straight Cartesian motion satisfies the resulting equations without curvature.
14. Horizontal momenta, vertical angular momentum and total energy are conserved under the stated uniform-gravity assumptions; p_zdot=−mg.
15. Barrier 2mgl above bottom, threshold bottom speed 2sqrt(g/l). At exactly that lossless energy the upward trajectory approaches the unstable top asymptotically; finite-time crossing requires greater energy. Actuation/losses/final velocity change the problem.
16. Compare coordinate descriptions with transformed states and forces, sampled energy-minus-work residuals at two tolerances, and an independent Jacobian/area check for symplecticity.

## Primary Reading Boundaries

Read Tedrake's author-hosted multibody notes through the manipulator equations, velocity-coordinate distinction and bilateral-constraint derivations (web lines 13–60), with additional returned contact passages through line 97. The replacement does not copy the notes' expressions uncritically; its signs, dimensions and rod model are derived independently. The notes' example uses endpoint point masses, unlike this chapter's uniform rods.

Read Hairer's author-hosted Challenges in Geometric Numerical Integration, sections 1–2 and the start of section 3 through its oscillator step-size discussion (PDF physical pages 1–6). The source supports the implicit-momentum formula and qualified small-step energy reasoning. This is not a claim to have read the entire cited monograph. Cambridge Tong HTML/PDF fetches timed out and were not read or cited. Existing Goldstein, Arnold, Marsden, Murray, Featherstone and control texts remain broader references without a claimed fresh full-book reading. New supplement entries use precise URLs and access dates; publication years are not invented.

## Validation and Review Failures

TDD first produced 24 missing-module errors and three independently passing counterexample checks. The first implementation gave 26 passes and one failure: I used the wrong sign in the constant angle offset when converting the absolute pendulum to the horizontal arm. The independent gravity formula caught the sign reversal; correcting the offset to +pi/2 gave all 27 passes. Seven further public-boundary and symplectic-stability cases bring the suite to 34 passing cases in 5.73 seconds.

Ruff initially caught a loop-variable closure in the integration test; it is now bound explicitly. The custom quality checker caught a missing initialization docstring and a gravity literal in the test; these now use a docstring and the shared gravity constant. The title audit requires “With” in the figure caption; that caption is corrected. Ruff, Black and the custom quality check now pass; full-root validation is still pending.

The published five-second DOP853 example runs at relative tolerances 1e-9 and 1e-11, with absolute tolerances 100 times smaller. Maximum sampled energy-minus-work residuals are 3.3737493e-9 and 1.1606005e-10 J for zero torque, and 2.5002853e-9 and 9.5331631e-11 J for constant motors (0.2,−0.1). The variable-mass step from (0.2,0.4) with h=.1 gives (0.22757308,0.41134196). These are finite-horizon numerical checks, not exact conservation or human validation.

The first print build succeeded at 262 pages but exposed two overfull headings and two long inline expressions. Headings were shortened; the forced variational statement and motor-work expression are now display equations. Bibliography and subsequent print passes, HTML render and full visual review are in progress. An inherited duplicate figure.11.1 PDF destination warning remains; it is not claimed fixed. The new web companion preserves nine original reader IDs and presently has 45 displays.

The first attempt to write the long draft in one Windows shell command exceeded the process command-line limit; the draft was instead written with apply_patch. A scratch conversion helper had a syntax typo, fixed before it produced canonical output. These failures did not establish successful publication.

### Final Typesetting and Independent Checks

The final numerical return from `numpy.linalg.solve` needed an explicit float64 array conversion to satisfy the repository's strict type checker; the full 82-source mypy pass then succeeded. The 34 focused cases pass again after that change (1.89 seconds). Ruff, Black at 100 columns and the custom quality checker pass. All 34 static CI contracts pass. Content checks give 128 passes, four skips and 4,482 deselections in 26.60 seconds; the title audit passes for all 625 publishable sources.

The first full-root run, with benchmark timing disabled, reached the unchanged proximal–distal technical-monograph PDF extraction and exceeded its configured timeout. No immutable monograph file was changed. A full rerun with a 300-second per-test limit and coverage enabled is pending; a timeout is not counted as a passed suite.

The initial complete browser review inspected 84 section views (28 headings in desktop light, phone light and phone dark), then 52 targeted views of the title, golf synthesis, figure, both code edges, references and every exercise, plus 17 equation edges. A separate width scan found four inline formulas wider than the phone text column: the multiplier solution, the rod skew matrix, the arm endpoint and the generating function. These became display equations in both editions, bringing the total to 49. Three further headings were shortened, the audit-process sentence was removed from reader-facing further reading, and the long-time integration wording was clarified.

After rebuilding, all 72 targeted repaired views and 19 equation right-edge views were inspected. No oversized inline formula remains; every tested equation edge is reachable at a 17.78-pixel math font. The pendulum region accepts keyboard focus and ArrowRight scrolling in phone light and dark modes; all four edge views were inspected. Both 14-view verification runs pass with no serious or critical accessibility findings. The final print build has 263 pages; every chapter page (physical 217–232), contents pages 12–13, index pages 258–260 and bibliography pages 261–263 was visually inspected. Existing whole-book duplicate destinations are not claimed repaired.

The print-URL addition exposed duplicate web URLs because Pandoc maps BibTeX `howpublished` to CSL `publisher`. This final bibliography-only presentation repair remains pending; the primary sources and technical argument have not changed. A scratch punctuation replacement also failed on Python replacement-string escaping before writing; the corrected literal replacement was applied and both editions rebuilt successfully.


## Completed Validation and Publication Preparation

The complete root suite passes 4,501 tests, with 29 skips, 129 deselections and 59 warnings in 885.85 seconds. It uses a 300-second per-test limit after the prior unchanged PDF extraction timeout; the passing extraction took 86.72 seconds. Benchmark timing is disabled, with correctness paths still executed. Source coverage is 92.67871170463472%, and the new Lagrangian module covers all 70 statements (100%).

All 24 original explicit print labels, 11 index terms, four generated box aliases and nine original web entry IDs are retained. The paired editions contain 49 display equations and all 16 corrected exercises. The complete print and browser evidence above has been inspected. Bibliography URL storage was moved into the BibTeX note for print while retaining the dedicated URL field for web citation processing, avoiding the duplicate CSL publisher link. This change does not alter the scientific sources or their reading boundaries. Final bibliography views and the post-render content pass are being checked before staging.

Configuration PR #4262 passed protected checks and merged as 0d3db9107ab89f612c0cf73d02402eb5d577ee73. Deployment 34172069718 completed successfully. The issue is closed and needs no lease renewal.


Final bibliography-only QA passes: all five web views and both changed print bibliography pages were inspected, with one source URL per web entry. Post-render static checks pass 34/34; content checks pass 128 with four skips and 4,482 deselections in 37.89 seconds. The SPEC changelog and 625-source title checks pass. All local test, render and browser QA jobs finished before staging.


Lagrangian PR #4263 is pushed at 4ad9bc7ec2d79cd670e5e0f44614ea85e1142465. The one correction commit fbc65f64 was replayed onto protected configuration squash 0d3db910 before first push; the full tree remained 01616c1e0ee4ed0467f6fb5adfd9b9151cbe16ba. Pre-commit and pre-push hooks, including isolated mypy and unit tests, passed. No force push or protection bypass was used. Protected checks and publication are pending.
