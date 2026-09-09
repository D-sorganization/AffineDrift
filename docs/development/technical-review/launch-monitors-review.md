# Launch-Monitor Estimation: Technical Review #4309

## Scope and Current State

The complete original technology-launch-monitors.qmd was read, including its
tables, mathematical proposal, patent descriptions, references and related links.
It was indexed at approximately 6,705 words. The replacement is approximately
7,100 whitespace-delimited words, with two independently generated figures.
All 20 historical heading destinations are retained.

Issue #4309 is a native child of #4009, part of corpus #4021 and measurement
batch #4059. Issue-filing exemption is false. An unheld claim check preceded
the codex lease, which expires September 9, 2026 at 16:53:26 UTC.
Branch fix/4309-launch-monitor-estimation originally started at swing PR
#4310 head 5499b61b. Reviewed checkpoint 70f0d252 is retained on
checkpoint/launch-4309-reviewed-70f0d252. Only that issue commit was replayed
onto published main 6b6876c0, producing 382daa9e with an identical complete
tree. No swing/brain ancestors were replayed.

The complete manuscript, derivation checks and local publication QA are finished.
Ready PR #4312 is pushed, references #4309 and carries agent:codex. All commit
and push hooks pass, including Bandit and unit tests. SPEC.md has exactly one
row keyed to this PR. Protected CI/review, merge and production verification
remain. This article's local completion does not establish completion of the
other corpus sources.

The first replay attempt stopped because Git reported an unstaged handoff file
despite an empty content diff. The working file and HEAD normalized to the same
blob 828243d38a00c8a111fcc4420ecdc5e112f03172. Restaging that identical
file refreshed the index without changing content; replay then succeeded.

## Editorial Argument

The site is investigating how a coupled golfer, shaft, head and contact system
produces a shot. The rewritten article distinguishes the observable consequences
from the unobserved force and state histories that could produce them. A common
head motion representation improves definitions, transforms and sensor fusion,
but cannot create absent observations or uniquely identify upstream causes.

Replace the modality-wide measured-versus-modeled ranking with a measurement
chain: measurand, observations, calibration, inference, uncertainty and independent
validation. Keep the research proposal, but state its hypotheses and experiments.
Avoid turning known commercial conventions into universal corrections or treating
a patent embodiment as a verified product implementation.

## Independent Derivations and Counterexamples

1. Two-way monostatic Doppler gives 2 fc v/c. At one mph, 24 GHz gives
   71.5759167 Hz and 10.5 GHz gives 31.3144636 Hz. This corrects the loose
   71.7 value without making a hardware specification claim.
2. For a material feature, radial rotation contribution is
   (u cross omega) dot r. Geometry and symmetry affect amplitude and harmonics.
   A harmonic feature is not automatically the fundamental spin frequency.
3. Under the declared local lift law L=k(omega cross v_air), k>0,
   omega_perp=(v_air cross L)/(k |v_air|²). Parallel spin is invisible at one
   instant. Vectors (80,-200,40) and (-80,-200,40) rad/s have the same magnitude
   and modeled lift at air velocity (50,0,0) m/s. This retains gyro-sign ambiguity
   even with a total spin-magnitude observation.
4. Homogeneous lift rows have rank one for parallel lift directions and can
   have rank two with changing directions under a constant-axis assumption.
   Normalization does not fix sign. State rank, conditioning and the force law.
5. A principal camera rotation of -90 degrees about z is consistent with a
   true +270-degree interframe rotation. Eigenvectors alone do not fix axis
   sign; zero and pi cases and temporal/texture aliases require explicit handling.
6. Point transport vP=vO+omega cross r gives contributions (0,1.2,0.4) and
   (0,-1.2,-0.4) m/s for r=(.04,0,0) m and opposite angular velocities
   ±(0,-10,30) rad/s. Therefore a forward reference point is not universally
   leftward and shallower. A curved translational trajectory does not determine
   body angular velocity; arc and closure terms cannot be added without a
   declared relative-motion decomposition.
7. Head geometric center, center of mass, face center and strike point differ.
   Face normals may vary over a curved face. A reported cross-reference
   face-to-path remains defined but needs a mapping into the contact model.
   Neither a universal three-degree correction nor a built-in slice follows.
8. Inverse horizontal launch f=p+(ell-p)/w has gradient
   (1/w,1-1/w,-(ell-p)/w²). Gains 1/.76 and 1/.85 have ratio 1.118421,
   not two. For ell=.5 degrees, p=-2 degrees and w=.76, f=1.289474 degrees.
   Independent standard deviations .1 degree, .2 degree and .03 give a
   first-order face SD of .195352 degree. Correlation, bias and model error
   remain separate. The equation contains no spin input.
9. If T=[R,p;0,1], spatial twist translation is pdot-omega cross p, while
   body twist translation is Rᵀ pdot. The convenient point-referenced pair
   (omega,vO) must not be silently substituted into the spatial matrix.
10. For nonzero omega, rISA=(omega cross vO)/|omega|² and
    h=(omega dot vO)/|omega|² yield axis-point velocity h omega.
    Pure translation, rest and near-zero angular speed require separate
    treatment. An ISA is not a uniquely determined swing plane.
11. For one monostatic location s, r_i cross u_i=(s-p) cross u_i, so every
    Doppler row depends only on vO+omega cross(s-p). Exact invisible changes
    satisfy delta vO=delta omega cross(p-s). The Doppler-only rank is at most
    three even when sightlines diverge. This does not discard pose information
    supplied by range/angle observations of known associated body features.
12. Thirty manufactured features near (2,.2,.1) m give ranks 3,5,6 for
    separate monostatic locations (0,0,0), (0,1,0), (0,0,1) m. Two stations
    retain baseline-axis null rotation. A commercial receiver array requires
    its own propagation model. The figure uses parameter scales 20 rad/s and
    1 m/s and independent range-rate SD .01 m/s; these do not change rank.
13. Spatial updates multiply on the left and body updates on the right.
    Rx(60 degrees) followed by fixed-axis Ry(45 degrees) differs from exp of
    the summed rotation vectors by 22.500474 degrees. Time order matters.
14. A face normal supplies two orientation degrees of freedom. It can be
    propagated with known spatial omega when that normal is the desired state;
    a full head frame needs additional information. At omega_z=30 rad/s,
    100 microseconds of timing error gives .171887 degree azimuth error.
15. Discrete covariance propagation includes state/rate cross-covariance:
    FPFᵀ+GQGᵀ+FCGᵀ+GCᵀFᵀ. Bias and event-time uncertainty must be represented
    or bounded. A later anchor can have worse image quality or correlations.
16. Two ideal infinite grooves with image heights ±.001 can have identical
    images and 2 mm spacing in planes with normals 63.434949 degrees apart.
    One plane is at depth 1 m. The other's groove depths are .4463191683 and
    .4481080227 m. Known endpoints, other features, range or views could supply
    the missing constraints; the two image lines alone do not.
17. With outgoing unit rays toward light and camera, the ideal reflection
    normal is parallel to their sum. It depends on the reflection point and
    propagation geometry. A normal-line anchor leaves axial orientation free.
18. Raw singular values mix parameter units. Use declared dimensionless
    parameter scales and noise whitening; evaluate the actual augmented
    temporal observation matrix. Smoothing and priors do not automatically
    remove geometric nullspaces.
19. A forward ball residual has covariance SigmaB+J SigmaC Jᵀ
    -C_BC Jᵀ-J C_BCᵀ, with model discrepancy where appropriate. Reusing the
    same ball data to infer face and validate it is not independent evidence.
20. Continuing forces and elastic states must be distinguished from a new
    delayed corrective response. Rigidity and event definitions are modeling
    choices; an unconditional 500-microsecond validity switch is unjustified.

## Primary Sources Read and Their Limits

- Wood et al. 2018 and Henrikson et al. 2020: complete papers previously read
  for #4307, retained as impact-wood2018 and impact-henrikson2020 PDF/text.
  The driver interval is a 95% confidence interval, not shot SD; horizontal
  and vertical samples and filters differ. The 2020 paper reuses the earlier
  data and examines friction/compliance without proving universal coefficients.
  The first draft mistyped the 2020 DOI; checking the actual paper and book
  bibliography corrected it to 10.3390/proceedings2020049027 before publication.
- Leach et al. 2017: complete accepted manuscript previously read in #4290;
  reuse the detailed scope in vendor-reference-review.md. Do not generalize
  January 2015 devices/setup to current product families or call its
  research/coaching bands independent certification.
- US8845442B2: relevant harmonic and trajectory-estimation descriptions,
  including equations 10–22, read. US10850179B2: phase/angle, resolution,
  transverse-projection and full-axis completion passages read (web description
  lines 374–460). Both remain method disclosures, not product validation.
- US9868044B2: relevant periodic demodulation, lens and symmetry descriptions
  read. US7292711B2: image preprocessing, correlation and constrained spin
  search passages read. Do not silently adopt those patents' aerodynamic or
  gyro-spin simplifications. Legal claims/history were not reviewed in full.
- Lynch and Park: complete angular-velocity video transcript read on the
  authors' Northwestern site; confirms the declared spatial/body convention.
- Murray author archive: confirms the formerly linked PDF was withdrawn in
  2020. The draft no longer promises a current freely available book.
- Vena Parts 1 and 2: public abstracts read; Part 1's visible analytical
  appendix was also inspected. Full subscription main texts were not accessed.
  The abstracts concern segment motion, and Part 2 reports the expected
  sequence in two of five subjects. No radar-estimator or universal skill
  classification result is claimed.
- Burke et al. 2022: public 45-page arXiv PDF downloaded and extracted after
  web tools hit size limits; reflection ambiguity, setup calibration and
  sections 2.5.1–2.5.2 on integrability and reconstruction were read. Full paper
  reading is not claimed. Global constraints can resolve ideal pointwise
  ambiguity while practical conditioning remains difficult.

## Validation Record

New tests first produced 20 passes and four intended source failures:
noncommuting propagation, inverse-gain arithmetic, two-groove reconstruction
and the ISA-as-plane claim. The complete rewrite passes all 24. Ruff and Black
pass. The title audit passes all 633 source files.

The two independent figures were visually inspected as standalone PNGs before
embedding their SVGs. The groove cross-sections preserve equal millimeter axes;
the spectral figure marks exact zeros separately from its logarithmic nonzero
values. Both state their manufactured assumptions.

Full regression passes 4,949 tests, with 29 skips, 131 deselections and 50
warnings in 400.15 seconds; coverage is 92.65%. Content lint passes 130 tests
with four skips. All 34 static contracts pass. Ruff, Black (678 configured
files), mypy (88 sources), tracked-file quality and the new CSS style check
pass. Final focused verification passes all 24 cases in 1.35 seconds.

The initial site gate rejected nine top-level internal links written with QMD
extensions. The authoring conversion now preserves their destinations while
using the required HTML extensions; the site gate passes. The final complete
source read caught a missing addition sign before the receiver calibration
phase and corrected it. It also made the acceleration units of the drag/lift
terms explicit and replaced the misleading word endpoints in the infinite-line
counterexample with cross-section points. These source corrections do not
change the tested numerical examples. The reproducible figure script initially
needed import ordering, an explicit strict zip and a function docstring; all
are corrected and its quality checks pass.

The complete rendered article was read in 29 overlapping desktop captures.
All 128 mathematical expressions and 34 display equations render, with no raw
display delimiters or MathJax errors. All 20 historical heading destinations
exist exactly once; images load with alt text and fragment destinations resolve.
Both themes pass at 320, 375, 390, 768, 1024, 1440 and 1920 pixels without
page-width overflow. Fourteen formula/figure scroll-edge views were inspected;
both figures respond to keyboard scrolling by 40 pixels. No inline expression
exceeds its paragraph width at the inspected phone width.

Visual QA found a substantive presentation defect that a zero-MathJax-error
check missed: the top bars of transpose symbols were clipped by the inherited
horizontal-scroll container. Native before/after equation captures verify that
0.25em of top padding restores the full symbols. Six final covariance-equation
captures in both themes confirm the repair. The new figure SVGs initially used
a font unavailable in the browser, producing different lettering from their
verified PNGs. Reproducible path glyphs now preserve the intended lettering;
their panels and opposite scroll edges were inspected in the browser.

The evidence tables initially wrapped a header and slash-separated phrases
poorly on phones. A shorter header, modest header sizing and clearer short
phrases preserve the information. The 320-pixel viewport leaves only a
199-pixel reading column; its two tables now retain a 270-pixel minimum width
within the existing focusable scroll wrappers. Both tables scroll by keyboard
in both themes, with 40-pixel movement and no page overflow. Final left/right
table views confirm access to complete text. Wider tables remain wrapped in
the normal reading column. Final affected checks pass 24/24 in 1.05 seconds;
all 34 static contracts and the final CSS style check pass after these fixes.

Automated axe checks report no serious or critical findings. The inherited
moderate landmark-unique warning includes navigation and repeated generic
equation/table labels. Browser console errors concern the existing external
polyfill and font requests blocked by CSP, including axe's stylesheet fetches;
do not describe the console as clean. The immutable proximal-distal publication
is untouched. Unrelated generated trust dates, formatting and digests created
by tests/builds are restored to the reviewed base before the checkpoint.

Swing PR #4310 is protected-merged and published as
6b6876c03f85b9db59d89a835983ca3a3250c1ef. Main CI 34371089520,
textbook build 34371089313 and deployment 34371089396 succeed. Exact live
artifact 10113084054 passes 956/956 checks across 239 routes, with zero
failures, axe violations, retries or transient responses.
