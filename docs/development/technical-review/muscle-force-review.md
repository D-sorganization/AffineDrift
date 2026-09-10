# Muscle Force Generation: Paired Technical Review

Issue #4331 is a native child of epic #4009; corpus #4021 and Physics textbook
#4054 remain unfinished. Branch `fix/4331-muscle-force-rigor` starts from motor
delivery checkpoint `71e80bb98531798d6d7c438d2858e932697fe469`; PR not created.
Both complete original chapter editions and all seven exercises have been read.
The print source is indexed at 6,139 words. Peer joint-friction work is excluded.

Claim check was free; lease comment 5610965947 expires 2026-09-10T02:49:29Z.
Central presence comment 5610973267 covers both editions and book bibliography
through 02:50:17Z. No subagents; no Git mutation during tests, rendering or QA.

## Confirmed Findings

The print and web editions diverge despite sharing serious model errors. Local
fiber speed is confused with clubhead speed and absolute whole-arm motion.
Shortening sign and normalization are inconsistent; 2–4 fiber lengths/second
for a 0.10 m fiber is 0.2–0.4 m/s, not 5 m/s. The hyperbolic concentric law is
called linear, extrapolated to negative force and used to prove inevitable
control failure. The web eccentric expression tends to
F_asym + (F_asym−1)/k, not F_asym, as signed velocity tends to minus infinity.

Active cross-bridge overlap, recruitment and total passive tension are mixed.
The passive exponential is negative below its unstated threshold. A Gaussian
does not have an exactly flat plateau or a finite zero. Fiber percentages,
specific tension and latissimus/triceps swing profiles lack suitable evidence.
Lower-limb publications are used as sources for forearm muscle parameters.

The CE/parallel-PEE network cannot have CE force equal to tendon force when
PEE is loaded. Pennation and tendon/fiber kinematics must be stated together.
The tendon-energy exercise integrates force over strain without slack length
and supplies insufficient compatible parameters. Stiffness is conflated with
a dimensionless exponential coefficient; elastic return is treated as free
energy or a universal shaft/coaching advantage.

Activation time constants, pure onset delays, EMG and full recruitment are
confused. The timing example places half force at 250 ms and impact at 300 ms,
then calls them simultaneous. Neural excitation is mistaken for muscle output.
The state excludes activation/elastic memory while calling the system Markovian;
the control-affine expression equates a state derivative with a scalar torque.
Measured inertial demand I*qddot is mislabeled as free drift. Joint moment
ranges and phase sequencing are not validated by their citations, and inverse
dynamics does not identify individual muscle forces or a unique optimal policy.

## Verification and Correction Plan

Derive a consistent teaching model from architecture to signed musculotendon
geometry, tensile force curves, massless force balance, tendon work and state
augmentation. Independently test limits, units, power duality, activation timing,
redundancy and finite-horizon effects. Use reproducible figures and seven fully
specified exercises with worked answers. Preserve historical labels/links;
render and visually inspect both editions and run all required checks before
protected delivery. No corrected chapter or completed validation is claimed yet.

## Primary Evidence Read So Far

- Millard et al. (2013), DOI 10.1115/1.4023390: indexed abstract, author-hosted
  paper through modeling sections 2.1–2.4, plus indexed discussion and limitations.
  Full remaining methods/results and visual equations are still to be checked.
  Comparison data are rat/cat soleus, not golf. A cached local author PDF/text is
  available; PMC direct access returned a CAPTCHA. Do not bypass access controls.
- OpenSim official Thelen-model documentation: text read, including the fact that
  its implementation differs from the original 2003 formulation and its inverse
  can be singular. Web math did not extract; no equation verification from that
  rendering is claimed. Its linked original paper failed to open.
- Rajagopal et al. (2016), PMID 27392337: complete primary indexed abstract and
  metadata read. The actual title ends in Human Gait, and the model has muscle-
  actuated lower limbs and torque-actuated upper body. The book's author list,
  title and note claiming upper-limb muscle parameters are wrong. Correct them
  and withdraw use as a forearm-force source. No full-paper claim yet.
- Nordez et al. (2009), PMID 19359617: full primary indexed abstract read.
  Electrically stimulated gastrocnemius in nine subjects separates some onset
  events, not all proposed delay components. Use only a bounded illustration of
  why EMD definitions/protocols matter; no universal golf latency.
- Moment-arm, upper-limb geometry, EMG interpretation and muscle physiology
  sources remain discovery leads until their relevant primary content is read.

## Delivery Context

Motor-learning PR #4330 is open at `71e80bb9` with normal squash auto-merge.
Its implementation is `fafad3fc`; all local checks and normal hooks pass.
Nonlinear repair #4329 is published as `1fe7997e`, verified by every one of
956 records in exact live artifact 10131240380. Motion/rotation publication is
verified through `4cf3514d`, artifact 10130399466. The corpus still has 405 rows
and 212 Indexed statuses, with additional partial and whole-book audits pending.
