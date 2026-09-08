# Exponential Coordinates: Complete Paired-Chapter Review

Issue [#4275](https://github.com/D-sorganization/AffineDrift/issues/4275), epic #4009, corpus #4021, Geometry batch #4055. Branch `fix/4275-exponential-coordinate-rigor`, initially based on recursive PR #4276 head `a1ba6f3b8efbfe8a0305a7e1bf5275d6b5c7db36`. The complete original print chapter (8,720 inventory words), complete web companion (1,664 words), all 15 exercises and their numerical code were read. This is a complete paired-chapter correction; the remaining 405-source corpus is not complete. The immutable proximal-distal monograph remains untouched.

## Original Failures and Their Consequences

- The opening confused physical Euclidean space with the rotation manifold, called all matrix differences meaningless and implied a logarithm identifies motion history/speed. A chordal matrix residual is a legitimate cost; a relative orientation does not identify the path, duration, torque or intention.
- The history incorrectly placed Rodrigues after Lie. The 1840 primary publication metadata contradicts that chronology. Unsupported personal priority claims were removed.
- Unit axes, rotation vectors, skew matrices and the entire Lie algebra were conflated. Every tangent space is a vector space; left/right identification with the identity determines angular-velocity components.
- The Rodrigues power cycle and even-power series had inconsistent signs. The replacement derives K²=uuᵀ−I, K³=−K, K⁴=−K², K⁵=K, K⁶=K², K⁷=−K before collecting the series.
- The logarithm was called unique on the closed principal ball; it is only unique in the open ball, and antipodal boundary vectors coincide. A usual analytic principal matrix logarithm is not defined at the negative-real eigenvalues of a half turn. An application can instead choose a rotation-logarithm branch.
- Small-angle formulas lost the factor one-half and called approximations exact. The trace identity does not break down at pi; the skew-based axis formula does. The web near-pi routine incorrectly snapped angles and used an unnormalized contaminated axis.
- The SE(3) translation matrix omitted a time/angle factor and mixed unit-axis and integrated-coordinate conventions. Its inverse had the wrong small-angle coefficient. Printed `skew(...)**2` squared entries instead of matrices.
- Conditioning θ/sinθ was wrongly presented as an intrinsic logarithm condition number. The local angular differential has singular values 1 and 2|sin(θ/2)|/θ twice, so its condition number is finite at pi. Branch discontinuity at pi, axis normalization near zero and rank loss at nonzero full turns are distinct.
- BCH degrees and convergence were overstated. A local small-amplitude expansion is justified; the degree-three remainder is O(ε⁴), not a count of four nested brackets. Two perpendicular quarter turns differ by a diagonal 120-degree relative rotation, not a z-axis quarter turn.
- The geodesic proof falsely used a local-isometry claim. The corrected proof specifies the angle metric, derives the stationary equation by an energy variation and proves minimality separately with the quaternion lift. A continued geodesic need not minimize length globally.
- Body/spatial velocity, continuous SLERP versus sampling, quaternion double cover and dynamic optimality were conflated. A shortest rotation curve need not satisfy joint/contact constraints or minimize mechanical/metabolic cost.

The original executable reproduction is saved in `exponential-original-reproduction.log`. For (0,0,1,1,0,0), the printed code gave translation (1,0.61822671,0), versus independent SciPy matrix-exponential translation (0.84147098,0.45969769,0), with matrix Frobenius error 0.22419388331432302. Its own log(exp(x)) returned linear coordinates (1.45121205,0.34807556,0). For an axis (1,2,3)/sqrt(14) and angle pi−1e−5, the original web round-trip error was 1.7638342073755057e−5. Exact-pi success did not validate the near-pi branch.

## Derivations and Intertwined Interpretation

The convention is R_WB mapping body columns into world coordinates, with angular-first integrated coordinates ξ=(φ,ρ). A constant twist acting for time t supplies φ=tω and ρ=tv. Integrating the Cartesian translation ODE gives p=J_l(φ)ρ, with J_l=∫₀¹exp(sΦ)ds. Reducing matrix powers yields its closed form. Multiplying the proposed inverse by J_l and using Φ³=−θ²Φ gives the half-angle inverse coefficient [1−(θ/2)cot(θ/2)]/θ², with limit 1/12.

Independently, Dexp_Φ[δΦ]exp(−Φ)=∫₀¹exp(sΦ)δΦexp(−sΦ)ds. Rotation conjugacy gives spatial angular velocity J_l(φ)φdot and body velocity J_l(−φ)φdot. Decomposition into the axis and its perpendicular plane supplies the singular values and distinguishes the principal cut from differential singularity. The plotted pi-crossing uses a continuously tracked local vector for conditioning and a separately wrapped shortest vector for the discontinuity.

For the angle metric, tangent inner product is a·b=tr(hat(a)ᵀhat(b))/2. Varying energy gives omega_body_dot=0. A quaternion lift has half the angular speed; choosing the nearer endpoint lift supplies a lower length bound 2 arccos|q0·q1|, attained by the constant-axis curve. This is the global shortest-path argument that the original local-isometry claim could not establish. Anisotropic inertia changes the kinetic-energy metric: constant omega requires either a principal-axis condition or applied torque. SE(3) has no positive bi-invariant metric because translations can make the adjoint's linear twist component arbitrarily large.

Golf interpretation is derived from material geometry x=p+Rr and n=Rn_body, giving δx≈δp−[Rr]×δφ_world and δn≈−[n]×δφ_world. Coordinate covariance converts through J_l; frame covariance converts through R. A changed impact event adds ydot δt to a fixed-time observable variation. These identities connect pose, rates, uncertainty, contact geometry and timing, while leaving muscle forces, intention, energy attribution and counterfactual performance to their necessary dynamic/measurement models. Flexible shafts require additional coordinates. Two independent hand interpolations need not satisfy a common-club constraint.

## Primary Sources and Reading Boundaries

- Modern Robotics [rotation exponential transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-3-exponential-coordinates-of-rotation-part-2-of-2/) and [rigid-motion transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-3-exponential-coordinates-of-rigid-body-motion/): complete substantive transcripts read. Their constant-generator interpretation is not used as an inference of actual motion history.
- Solà, Deray and Atchuthan, [A Micro Lie Theory for State Estimation in Robotics](https://arxiv.org/abs/1812.01537), v9: abstract/introduction, relevant differential passages and Appendices B/D formulas read; the whole paper was not read. Translation-first six-vectors require block reordering. Formulas were independently derived here; the source is a convention cross-check.
- SciPy [expm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html), [Slerp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Slerp.html), and [Rotation.from_matrix](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_matrix.html): relevant API and algorithm notes read. The cited matrix-exponential research paper was not independently read in this slice. Input validation deliberately precedes SciPy's matrix-to-rotation conversion, which can otherwise project imperfect matrices.
- [NUMDAM's original Rodrigues publication record](https://www.numdam.org/item/JMPA_1840_1_5__380_0/): bibliographic metadata verified, not the complete 61-page French paper. The legacy bibliography key now points to this primary record instead of a search URL.
- Existing Murray/Lynch book references are retained as further reading; this slice does not claim newly reading those entire books.

## Exercise Solutions and Verification Targets

1. Let c=1/sqrt(2), d=(1−c)/3 and a=1/sqrt(6). R has diagonal c+d, cyclic off-diagonals d−a and d+a. Its action fixes u and rotates the perpendicular plane, proving orthogonality/determinant. The axis is in the declared reference frame.
2. φ=(0,0,pi/2), with hat entries (1,2)=−pi/2 and (2,1)=pi/2. Adding 2pi to the z coordinate gives a longer logarithm.
3. Trace(K)=0 and trace(K²)=−2 give 1+2cosθ. At pi, R+I=2uuᵀ; a normalized nonzero column gives either axis sign.
4. Triple-product identity gives K² and multiplying by K gives K³. The signs through K⁷ are recorded above and checked by parsed-source numerical products in both editions.
5. The error is θ²K²/2+O(θ³); (I+θK)ᵀ(I+θK)=I−θ²K², so a nonzero finite step is not orthogonal.
6. R=Rz(1), p=(sin1,1−cos1,0). The fixed axis is {(0,1,z)}; substituting that point in Rp+p_translation verifies it.
7. T(t) has identity rotation and translation (t,0,0). J_l(0)=I multiplies the integrated coordinate tv.
8. Exponential inversion always gives a compatible logarithm. A pure half turn equals its inverse, contradicting an unconditional odd single-valued nonzero logarithm.
9. The second-degree term is half the commutator, reversing sign when order reverses. Third-degree terms and all higher orders prevent quarter-turn extrapolation.
10. RᵀRdot=hat(φ_body)/τ and RdotRᵀ=hat(R0φ_body)/τ. Fixed-axis coordinates are a special case of the full Jacobian relation.
11. Angle distance is 2pi/3; the unnormalized Frobenius metric gives sqrt(2) times that length.
12. Frobenius error is sqrt(2[(cosθ−1)²+(sinθ−θ)²]), approximately 7.0710676e−7 at θ=.001. Leading term θ²/sqrt(2).
13. exp(tA) has Rz(pi/4) and zero translation, homogeneous last row. A is already a matrix generator.
14. R(s)=R0exp(s hat(φ_body)) has relative angle s||φ_body|| on 0≤s≤1. At pi choose either minimizing axis-sign branch consistently.
15. R=Rx(t), p=(0,sin t,1−cos t). At 0: identity/zero; at pi/4: (0,1/sqrt(2),1−1/sqrt(2)); at pi/2: (0,1,1). Axis {(x,0,1)} is fixed and pitch is zero.

## Implementation and Validation Checkpoint

Before production implementation, 43 numerical contracts were collected and the first failed with ModuleNotFoundError for the absent helper (14.27s; `exponential-tdd-red.log`). The minimal helper then passed all 43 plus the existing 22 screw cases: 65 passes in5.51s. It uses series for the left Jacobian near zero, SciPy rotation conversion and a linear solve for rho. The existing private rigid-transform validator was promoted to a public function and reused, avoiding duplicate validation. No callers outside that module used its former private name.

Additional independent checks exercise BCH error orders, exact quarter-turn matrices, Slerp versus expm in both frames, chordal/small-angle norms and material-point/normal sensitivity. The old Rodrigues regression checked only an obsolete notation-specific odd-power string and had missed other sign errors. Its replacement parses every published K⁴–K⁷ identity in both editions and checks direct matrix products. Full root, source quality, content, print and browser QA are pending at this checkpoint. Neither publication nor complete corpus review is claimed.

## Previous Recursive Publication Checkpoint

Recursive correction #4274 was committed as ab20c9af3a3c900316c04cb425b1476386ed3c08 and replayed onto protected main7d78f6b0 as a1ba6f3b8efbfe8a0305a7e1bf5275d6b5c7db36. Both trees equal fe1f61a8b0ba0c1a1bd9dcbd4f239f48d8313f10. A phantom handoff modification was resolved only after empty-diff and identical blob-hash verification, by refreshing the index. Pre-commit and pre-push checks passed, including unit and Bandit checks. PR #4276 is open with protected squash auto-merge enabled. Its Python tests and all compile/static lanes passed; full-site browser CI was still pending at last inspection. No local QA overlapped that commit/push. Its protected merge and deployment must still be recorded after completion.


Protected recursive PR #4276 passed all required checks and merged as4748e674db5c3f7d0c981282f6cf4a8ea9dd86ed. Deployment34199401123 is running; publication is not yet verified. Issue4274 is closed and no longer needs a lease.


Deployment34199401123 failed on one of956 page inspections: the unchanged Physics ch04 forces-and-torques page had one visible equation untypeset on mobile/dark, with HTTP200, zero overflow and no serious/critical axe violations across239 routes. The artifact was downloaded and inspected. A freshly rendered isolated-route probe is pending before deciding whether this is a transient typesetting failure or a reproducible defect. Do not claim successful publication.


Local validation: full root4686 passed,29 skipped,131 deselected,59 warnings in544.16s; coverage92.72784019975032%, new helper36/36 lines covered. Focused75, mypy84, static34, content130/four skips, title629 and SPEC check pass. All12 chapter pages112–123 plus contents8–9 and index/bibliography234–241 were visually inspected; final title/equation/event/bibliography repairs were separately inspected. Exactly60 section captures (20 headings in desktop/mobile/mobile-dark) were inspected. The14-view verifier passed with zero serious/critical axe findings. The targeted keyboard guard found two wide inline formulas; both became web displays, so print25/web27. Visual inspection caught smart-quote conversion corrupting triple-backtick fences; conversion now matches paired prose quotes only, and the generated source retains a real Python fence. The final code/keyboard/edge and citation/index checks remain pending.


## Final Local Verification, 2026-09-08

The final focused suite passes 77 cases, including two new regressions that extract and execute the actual Python example from each published edition. These caught and protect against the repaired code-fence conversion defect. The earlier full root run passed 4,686 tests, with 29 skips, 131 deselections and 59 warnings in 544.16 seconds; it predates those two presentation regressions and is not a claimed 4,688-test full run. Overall coverage is 92.72784019975032%; the new helper covers all 36 executable lines. Final content checks pass 130 with four skips, mypy passes 84 files, static checks pass 34, titles pass 629, and SPEC, Ruff, Black100 and custom quality checks pass.

All 60 initial section views and all 62 final target/keyboard images were visually inspected. The latter include 22 equation right edges, 35 title/figure/code/exercise/bibliography views and five keyboard views. The final responsive verifier passes 14/14 with zero serious/critical axe findings. All ten legacy content IDs occur exactly once. Keyboard scrolling reaches the figure's full 331px extent in phone light/dark modes, and no oversized inline formulas remain. Print has 25 displays and web has 27, after moving two wide inline formulas into displays. All 15 exercises and both ends of the code block are verified visually.

The final Volume 0 PDF has 241 pages; chapter pages 112–123, contents 8–9 and index/bibliography 234–241 were inspected, with subsequent changed pages inspected again. Index terms now point at their substantive sections. New bibliography entries use descriptive clickable print labels and single web addresses. The escaped underscore repair and prose-only smart-quote conversion are included. Inherited warnings in other chapters remain outside this correction.

All local test/build/render/browser QA ended before staging. Only the HTTP server/browser session remain available. The original checkout and immutable monograph source were not edited. Protected publication remains pending. Replay only #4275 commits after a1ba6f3b8efbfe8a0305a7e1bf5275d6b5c7db36 onto current protected main before the first push.


The freshly rendered isolated Forces and Torques probe passed all 14 responsive checks, with zero serious/critical axe findings. Deployment run 34199401123 attempt 1's single untypeset-equation failure remains recorded as adverse evidence; the failed job was rerun after this successful probe. Attempt 2 is in progress as of 08:11 UTC. This is not yet successful-publication evidence; a repeated failure requires diagnosis rather than repeated blind retries.


Recursive PR #4276 / protected squash 4748e674 is published. Deployment 34199401123 attempt 2 succeeded; downloaded live artifact 10047429024 passes all 956 checks across 239 routes, with zero failures, zero serious/critical axe violations and zero navigation retries. Attempt 1's adverse evidence remains retained.


## Exponential Publication Verified

Exponential PR #4279 passed protected checks and squash-merged as `439695c4753cd14f97a689605aa6c675374f0ddd` at 08:43:14UTC on 2026-09-08. Deployment 34206038396 succeeded. Downloaded exact-revision live artifact 10048902701 reports 956/956 passes across 239 routes, zero serious/critical axe violations, zero retries and zero transient responses. Issue #4275 is closed; no lease renewal is needed.
