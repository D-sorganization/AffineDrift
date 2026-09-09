# Swing Plane, Contact and Launch: Technical Review #4307

## Scope and Editorial Argument

This is a child of epic #4009 and part of the complete-corpus review #4021 and
Physics textbook batch #4054. Both original editions of
`ch31_swing_plane_launch` were read completely, including all eight exercises:
the index records 6,744 words in TeX and 5,651 in Quarto. The source filename
is chapter 31; the assembled textbook numbers it Chapter 18.

The revised argument follows preparation and continuing actuation through
club delivery, collision, ball flight and the reader's objective. Geometry
relates measurements; it does not identify a golfer's controller or determine
contact forces. A useful intervention must preserve or explicitly change the
other delivery conditions, contact constraints and environment. Uncertainty
passes through the entire chain. This connects the computational-brain,
impact and aerodynamics chapters without treating one explanation as a
universal replacement for the others.

The two editions contain matching derivations, eight specified problems and
eight worked answers. New vector figures replace an incorrect plane sketch
and illustrate the declared optimization model. The latter is deliberately
manufactured, not a fit to launch-monitor data. No measured carry optimum,
universal launch window or preferred swing technique is claimed from it.

## Findings and Derivations

1. **Reference Frame, Point and Event.** Use a right-handed frame with target
   direction x, target-left y and upward z. Azimuth is positive left. Device
   signs require explicit conversion. Rigid-head point transport is
   `v_C = v_G + omega_H cross (r_C-r_G)`. Changing the reporting point or using
   first touch instead of maximum compression can change reported delivery.
   Shaft flexibility changes the head's state without invalidating this
   rigid-head identity.

2. **A Plane Needs Independent Directions.** A velocity alone admits many
   planes. Combining it with vertical gives a vertical plane, not an
   arbitrarily inclined one. For a unit plane normal, inclination is
   `acos(abs(n_P dot e_z))`. A finite-arc covariance fit uses its least-variance
   eigenvector; residuals, fitting interval and eigenvalue separation matter.
   An osculating plane requires a nonzero velocity-acceleration cross product.
   Standard lie is referenced to horizontal, so 57 degrees has a 33-degree
   complement to vertical. Neither lie nor body height identifies a delivery
   plane or its cause.

3. **Path and Attack Share One Velocity.** With base azimuth d and inclination
   beta, choose orthonormal in-plane vectors
   `b=(cos d,sin d,0)` and
   `u=(-sin d cos beta,cos d cos beta,sin beta)`.
   For tangent `cos chi b + sin chi u`, projection gives
   `sin alpha=sin beta sin chi` and
   `psi-d=atan2(cos beta sin chi,cos chi)`.
   On the forward branch, `tan alpha=tan beta sin(psi-d)`.
   At beta=60 degrees and alpha=-5 degrees, the path offset is
   -2.8953338 degrees, right of the declared base direction. The relation
   depends on the stated basis and sign convention. A finite chord cannot
   replace the instantaneous tangent. Small chi permits
   `alpha approximately sin(beta) chi`; replacing sin(beta) with beta also
   requires small plane inclination, which 60 degrees does not satisfy.

4. **Face Orientation and Joint Gain.** A unit normal determines azimuth and
   elevation, not the full head frame. Ordered rotations replace scalar sums
   of anatomical joint angles. An infinitesimal spatial rotation about k gives
   `d phi/d theta = k_z-tan(loft)(k_x cos phi+k_y sin phi)`.
   At square face and 15-degree loft, x/y/z gains are -0.26795, 0 and 1.
   Finite 90-degree x/y rotations acting on the x normal give different results
   in reversed order. Two-hand constraints and transported joint axes prevent
   interpreting these examples as independent anatomical percentages.

5. **Control Authority Includes Timing and State.** A fixed-time local
   sensitivity contains both propagated initial-state error and the integral
   of feasible input perturbations. Delay and activation belong in that model.
   For a transverse autonomous contact event `g(x(T))=0`,
   `delta T=-g_x delta x(T)/(g_x xdot(T))` and
   `delta x_event=delta x(T)+xdot(T) delta T`.
   Differentiability, nonzero denominator and no intervening mode change are
   required. A new command delayed 60 ms cannot reach impact 30 ms away through
   that pathway; existing activation and earlier commands remain possible.
   This is not a universal physiological cutoff or proof of a free club.

6. **D-Plane Geometry Does Not Complete the Collision.** Two nonparallel local
   directions still span a plane at an off-center strike. What can fail is the
   prediction that the actual collision remains planar. With initially
   stationary ball and planar impulse `J=J_n n+J_t t`, ball velocity is `J/m`
   and its direction is the normalized impulse. A fixed weighted sum of unit
   vectors is generally not itself a unit vector. Three-dimensional spin loft
   obeys `cos Phi=cos loft cos attack cos(face-path)+sin loft sin attack`;
   the loft-minus-attack shortcut requires matching azimuths and its stated
   angle branch.

7. **Spin Requires Impulse and Inertia.** For a spherical ball with isotropic
   inertia and zero initial spin, contact is at `r=-R n`, not at the center.
   Angular impulse gives `omega=-R J_t (n cross t)/I`.
   For a level forward path and upward face normal, the defined positive
   tangential impulse yields spin toward -y and upward conventional Magnus
   lift. Normal frictionless impulse alone yields zero spin. A bare cross
   product of directions supplies neither RPM nor an axis when spin is zero.
   Gear effect involves eccentric head motion and tangential contact; it is
   not explained merely by a ball being touched on its surface.

8. **Face Weight Is Not a Total Miss Sensitivity.** The illustrative horizontal
   weight 0.76 gives launch 0.48 degrees right for a path 2 degrees right and
   square face. This predicts initial direction only. At a plane 250 yards
   downrange and zero launch azimuth, geometric face/path gains are 3.3161 and
   1.0472 yards per degree. One degree of launch instead gives 4.36377 yards
   through `250 tan(1 degree)`. Curvature, changing carry, strike, correlation
   and environmental response require the full model. There is no universal
   13–20 or 17–24 yard/degree range established by this geometry.

9. **Flight and Optimization Need a Complete Problem.** Initial position,
   velocity vector, spin vector, ball model, density, wind and landing surface
   are required; bounce and roll add ground interaction. Drag uses air-relative
   velocity, and lift must handle its zero-axis limit. Vacuum level-ground
   range `v^2 sin(2 theta)/g` is maximized at 45 degrees for every positive speed.
   This limiting counterexample refutes a universal speed-only optimum rule;
   it is not a driver fitting recommendation. Wind speed alone cannot specify
   an angle adjustment or a total-distance optimum.

10. **A Checkable Coupled Response Surface.** Around 140 mph ball speed,
    14-degree launch and 2,400 RPM, define yard-valued
    `D=230+2 delta v-0.5 a delta theta^2-b delta theta delta Omega-0.5 c delta Omega^2`,
    with a=0.8, b=0.002 and c=0.00002 in the stated compound units. Positive a
    and determinant `ac-b^2=0.000012` establish positive curvature of loss.
    At fixed 2,200 RPM, both 16 and 13 degrees give 228.8 yards, while the
    conditional optimum is 14.5 degrees and 229.7 yards. The joint center gives
    230 yards. A positive-coefficient model `A v^2-B Omega-C Omega^2` decreases
    for all nonnegative spin and cannot demonstrate a positive-spin optimum.

11. **Sensitivity Is Local; Covariance Matters.** At a smooth interior maximum
    the relevant first derivative is zero, not maximal. At 16 degrees and
    2,200 RPM the local angle slope is -1.2 yards/degree: a -3-degree step's
    predicted +3.6-yard linear gain is canceled by -3.6 yards of curvature.
    The one-yard-loss set is an ellipse, not independent angle/spin windows.
    Its axis intercepts are 1.58114 degrees and 316.228 RPM. With launch SD
    1 degree, spin SD 200 RPM and correlation rho, exact quadratic mean loss
    is `0.5 tr(H Sigma)=0.8+0.4 rho` yards: 1.0 at +0.5 and 0.6 at -0.5.

12. **Equipment and Effective Mass.** Under a free-body, frictionless normal
    impulse approximation, inverse effective mass is
    `1/m_B+1/M_H+(r_H cross n)^T I_H^-1 (r_H cross n)`.
    A centered spherical ball adds no normal rotational term. With head mass
    0.2 kg, ball mass 0.04593 kg, relevant head inertia 0.0004 kg m^2 and
    20 mm offset, the extra inverse mass is 1/kg. At fixed closing speed and
    restitution, the off-center/centered impulse ratio is
    `(5+1/0.04593)/(6+1/0.04593)=0.96399285`.
    This is not a measured mishit penalty or a prediction of gear-effect spin.

13. **Speed Ratio, Dispersion and Objective.** Smash factor is a speed ratio,
    not energy efficiency. At constant club speed 100 mph, smash-factor SD
    0.05 gives ball-speed SD 5 mph; variance 0.05 instead gives 22.36068 mph.
    For independent club speed V and ratio S, exact product variance is
    `mu_V^2 sigma_S^2+mu_S^2 sigma_V^2+sigma_V^2 sigma_S^2`.
    Correlated exact results need mixed moments; first-order propagation has
    the covariance cross term. In the declared linear 2 yard/mph example,
    3 mph more mean ball speed adds 6 mean yards, while ball-speed SD 4, 5 and
    2.5 mph map to distance SD 8, 10 and 5 yards. These trade-offs cannot be
    ranked without an objective and costs of misses.

## Source Reading and Evidence Limits

Primary-source reading took place on September 9, 2026. The complete extracted
text, tables, captions and references of Wood et al. (2018), six pages, and
Henrikson et al. (2020), eight pages, were read. Their figures were not visually
inspected: attempted web screenshots did not supply usable images. No claim
depends on visually measuring those plots.

- Wood et al., DOI [10.3390/proceedings2060249](https://doi.org/10.3390/proceedings2060249):
  the chapter identifies the filtered horizontal samples and 95% confidence
  intervals, distinguishes vertical ratios, and qualifies the robot comparison,
  measurement alignment and PING funding. The 157-player protocol and 1,575
  pre-filter shots are not the denominator of each horizontal estimate.
- Henrikson et al., DOI [10.3390/proceedings2020049027](https://doi.org/10.3390/proceedings2020049027):
  tangential compliance and friction support a mechanism under the model's
  assumptions. Reused player data do not form a new independent cohort.
  The fixed-surface approximation limits transfer to a free head. The extracted
  inequality for an error metric was ambiguous, so no numerical error bound is
  asserted. The unsupported linear fit was removed. Author Tom Nuttall replaces
  the incorrect Nathan Nuttall in the bibliography.
- Trackman, [What Is Swing Plane?](https://www.trackman.com/blog/what-is-swing-plane)
  and [40 Trackman Parameters](https://www.trackman.com/blog/40-trackman-parameters):
  vendor definitions support the finite-arc metric and point/event distinctions,
  not independent validation of all golfers or a lie-fitting prescription.
  The attack-angle page was also read; its population summaries were not
  promoted to individual fitting targets.

Direct MDPI retrieval failed; the primary papers were read from copies at
Semantic Scholar. The earlier preaudit scratch note saying the Quarto edition
was unread is superseded by this completed paired reading. No source was used
to establish a universal neural latency, launch window or causal joint share.

## Verification and Corrections During Review

- Independent NumPy/SciPy checks cover plane identities, finite rotations,
  normalized launch direction, impulse spin, normal effective mass, vacuum
  optimization, the quadratic optimum, covariance and product variance.
  The new suite has 23 cases. Its first run had two intended publication
  failures and two mistaken hand-entered numeric expectations. Those constants
  were checked independently and repaired; the resulting red run had 21 passes
  and two publication failures. The paired rewrite then passed all 23.
- The figure inventory integration tests were updated to the actual rewritten
  inventory: 34 chapters, 28 with figures, 32 TeX figures, 22 TikZ environments,
  10 includegraphics calls, 32 labels, 11 Quarto figures and 21 missing figures.
  This records the remaining book-wide parity gap, not a claim it is solved.
- The initial full suite had 4,922 passes, 29 skips and one failure: the old
  face-angle regression required an unsupported `13--20` range. Its two other
  tests used assumed multipliers without modeling a trajectory. The replacement
  tests check ray intersection, the distinction between launch and face angle,
  and both editions' explicit curvature limitation.
- The initial 34 static contracts found one unqualified ZTCF index entry.
  The preserved index entry now explicitly names the ZTCF family.
- Final print layout before that index-only correction was inspected on all
  18 chapter pages (physical 242–259, printed 214–231), plus the following part
  divider, contents page 14 and bibliography pages 537 and 543. The 552-page
  book compiled without overfull boxes or undefined references in this chapter.
  Long callout titles and three overflowing lines were repaired. Other chapters'
  pre-existing layout warnings are outside this claim.
- The chapter's duplicate `sec:sensitivity` TeX label was renamed to
  `sec:launch_sensitivity`; no reference to the old shared label existed.
  The other chapter retains its label. Historical heading aliases and figure,
  table and exercise destinations are retained in the web edition.
- Browser testing found low-contrast dark table captions and visible reference
  syntax. The captions now use Quarto table identifiers with separate legacy
  aliases; chapter-scoped CSS restores readable caption color. A later scrolling
  failure was a verifier timing error: the page uses smooth scrolling, and an
  immediate read preceded the movement. The verifier now explicitly requests
  instant scrolling before checking the result; no product workaround is needed.

## Delivery Status

Visual review then caught a conversion error missed by the browser's original
MathJax-error check: 21 unnumbered display equations had blank lines inside their
delimiters and appeared as ordinary paragraphs. Seeing no MathJax errors does
not prove that the intended equations were recognized. The converter now strips
the delimiters' interior boundary whitespace, and a new paired-edition test
compares every display equation's mathematical content and rejects blank lines.
Its first repaired check incorrectly rejected valid list indentation; that
assertion now distinguishes indentation from empty lines. All 28 numerical and
publication cases pass. The browser verifier now requires all 31 display
equations and rejects visible raw delimiters. Earlier screenshots with only
10 display equations are failed evidence, not accepted publication QA.

The second broad regression run recorded 4,922 passes and two failures, both
caused by `.playwright-cli` temporary output at the repository root. The second
static run failed on the same hygiene condition. Keep those failures in the
record and move only that verified temporary directory into the review scratch
area after browser work finishes. The numerical/source failures from the first
run are repaired; final hygiene and publication checks remain at this point.

Ruff, Black (677 files), mypy (88 source files), the tracked-Python quality
check including the new test, all 63 tracked CSS files and the new chapter CSS,
633 title checks, the site link gate, and 130 content-lint checks pass (four
content skips). A hidden-process server launch was rejected by automatic policy;
running the same localhost-only preview directly in the tool session succeeded.
No publication approval or branch-protection bypass was attempted.

The corrected content is local on `fix/4307-swing-plane-launch`, based on
30701c44. It has not been committed, pushed or opened as a PR. Final repaired
checks, web evidence, index rebuild and delivery remain. On resumption at
14:07 UTC, GitHub returned HTTP 401 for GH_TOKEN and both saved credentials;
claim renewal and remote state checks could not be verified. Authentication
restoration was requested while local work continues. Do not treat a failed-open
claim lookup as proof that another agent has no claim.

The brain correction PR #4306 was previously confirmed merged as 022fc21c.
Its main CI and deployment were still running at the last successful remote
inspection. Reverify publication after authentication returns. Before replaying
this chapter onto protected main, save a local checkpoint and replay only its
own commits after 30701c44; do not replay the brain ancestors. Keep the full
405-source corpus goal active and the pending/partial review entries honest.

## Final Local Verification and Restored Delivery Access

The final broad run passes 4,925 tests, with 29 skips, 131 deselections,
50 warnings and 92.65% source coverage (316.44 seconds). All 34 static
contracts pass. The final affected suite after web-only wrapping changes passes
51 tests. No mathematical or print-content changes followed the full run.
The index-only rebuild passes; final list-of-figures and index pages are
visually checked in the 552-page book.

The corrected browser run recognizes 221 mathematical expressions and all 31
display equations. Its 14 viewport/theme checks pass; all 52 body captures and
19 scroll-edge captures were visually inspected. All 31 historical heading
aliases remain unique, and image/fragment and keyboard checks pass. Final
targeted inspection covers all three tables at desktop and phone widths in
both themes (12 captures), plus the two long inline expressions' far edges
and keyboard access. Explanatory tables wrap; numerical headers retain whole
words. Only the two long expressions receive focusable scrolling wrappers.

The first inline CSS attempt had no effect on an inline formatting box.
A broader inline-block experiment created unwanted overflow for short italic
expressions and was discarded. The final wrappers leave ordinary inline
mathematics unchanged. Browser cache/service-worker state and rounded width
thresholds also caused verifier failures; the final verifier clears that
state, tests the actual scroll region and confirms keyboard movement.
No serious or critical axe findings remain. Inherited minor aria-allowed-role
and moderate landmark-unique findings remain, together with CSP-blocked
external polyfill/font requests and preload warnings. Do not describe the
console or the entire site as free of warnings.

Repository access resumed after the authentication interruption. A fresh claim
check found #4307 unheld; its codex lease was renewed through September 9,
16:49:45 UTC. Brain PR #4306's exact production artifact is now verified as
recorded in brain-review.md. Launch-monitor issue #4309 is a native child of
#4009, with a verified codex lease through 16:53:26 UTC. Its preliminary
review remains distinct from a completed correction.

## PR #4310 and Checkpoint

The complete correction was saved as 3e270aa0, retained on
checkpoint/swing-4307-reviewed-3e270aa0. Replaying only that commit onto
protected main 022fc21c produced 66f1fa43 with an identical complete tree;
no brain ancestors were replayed. The first push was blocked by Bandit finding
dynamic execution in the untracked conversion helper wrap_swing_math.py.
That helper now performs the explicit transformations without dynamic execution.
The first unit-test hook passed. The retry passed every push hook, including
Bandit and unit tests, and published the topic branch without a force push.

Ready PR #4310 references #4307 and carries agent:codex. SPEC.md adds exactly
one row keyed to this PR. Protected CI/review, merge and production verification
remain; local completion does not substitute for those delivery checks.
