# Impact Optimality and Model Limits: Technical Review

Issue [#4714](https://github.com/D-sorganization/AffineDrift/issues/4714), epic
#4009, historical corpus umbrella #4021. Started 2026-09-30 after explicit user
resumption. The article was the longest remaining source marked Full Technical
Audit Pending: 2,719 words in the original census.

## Scope and Connected Argument

Review the complete impact-optimality article, including its public summary,
derivation, historical simulations, literature claims, interpretation and
implementation references. Correct the same argument in the workbench's
dedicated model-limit section and the article-index description. Those two
linked corrections do not constitute a full new review of their other content.

The central argument now connects the velocity map, energy metric, coupling,
actuation, reachable trajectories, measurement definitions and identifiability.
Preserve the distinction between a useful reduced model and evidence about a
golfer. Preserve historical numerical reports with their provenance instead of
silently replacing them with newly implied experiments.

## Findings and Resolutions

1. **P1: Instantaneous versus trajectory optimum.** Define relative/absolute
   angles, signed output, collinearity, positive-definite inertia and positive
   energy. Derive the normalized Cauchy–Schwarz optimum and state the singular
   zero-proximal-inertia exception. A terminal energy allocation does not prove
   a torque history, collision optimum, or physiological strategy.
2. **P1: Distributed inertia and physical feasibility.** Supply the complete
   mass matrix, determinant and first inverse-output component. Correct the
   example threshold from roughly 0.2 to 0.0698027 kg·m². Derive the support
   inequality for collinear mass and distinguish bodies with transverse extent.
3. **P1: Inertia equivalence.** Matching the wrist-row diagonal preserves one
   coefficient. Derive the coupling error in terms of the same bracket governing
   optimal hand-rate sign. Separate the two historical club-property examples,
   butt versus grip origins, and physical versus model head length. Recompute
   all displayed inertia/coupling values under declared assumptions.
4. **P1: Solver and historical-run evidence.** Preserve the reported tables but
   distinguish source reports from rerun results. Record the 0.36 s frontier,
   0.28 s revised objective comparison, 24% remaining modeled braking, and
   failed Hill candidate's order-one defects. A local failure or dynamics-only
   predicate is not an infeasibility certificate or full feasibility check.
5. **P1: Actuation and anatomical inference.** Distinguish muscle shortening
   behavior, aggregate joint-actuator assumptions, eccentric energy absorption,
   net moments, segment deceleration and muscle activation. The provider itself
   permits braking. A single rollout does not prove reversal is necessary for
   every release.
6. **P1: Comparison-band provenance.** Label the six implementation intervals
   heuristic until exact provenance and observable mappings are established.
   Correct the Nesbit cohort and quote its actual Table 3 ranges as reported.
   Separate model reference scores from statistical validation or likelihood.
7. **P1: Objective identification.** Similar terminal scalars do not establish
   identical trajectories, and indistinguishable predictions cannot identify
   a person's objective. Centrifugal impulse is not a hold-lag instruction.
8. **P1: Parametric acceleration.** Miura's relevant example has fixed links and
   a translating pivot. Explain grip power and moving-base energy accounting;
   do not infer a unique human mechanism or require a shortening proximal link.
9. **P1/P2: Linked public summaries.** Remove the workbench's obsolete universal
   zero-speed/reversal claims and reconcile the catalog title/description. Add
   resolving related articles and remove only the resolved link-gate baseline.

## Primary Evidence and Access Limits

- Nesbit (2005), _A Three Dimensional Kinematic and Kinetic Study of the Golf
  Swing_: complete 21-page primary PDF text read; Table 3 on p. 504 visually
  inspected. The p. 503 results section calls it aggregate-group statistics;
  four selected subjects supply the detailed time-history comparisons. The
  study comprises 84 male and one female amateur golfers.
- Nesbit and Serrano (2005), _Work and Power Analysis of the Golf Swing_:
  independently reread methods pp. 520–523 and discussion pp. 527–531. Its
  kinematically driven net-work analysis does not measure individual-muscle
  braking. No claim of a new full-paper review or experimental rerun.
- Miura (2001): complete main text reread; pp. 82–83 visually inspected,
  including the moving-pivot diagram, equation (13) and Table 1. The 0.08 m pull
  and 46.8-to-50.1 m/s result are a modeled emulation, not a measured intervention.
- MacKenzie and Sprigings (2009): complete primary text read. One three-handicap
  male, six selected drives, single-camera 2D comparison and separate 3D
  optimization. Four aggregate torque generators are not specific muscles.
- Hill (1938): primary PDF pp. 160–163 and 192–193 read. The force–shortening
  relationship and lengthening discussion do not justify excluding eccentric
  muscle action or identifying joint torque directly with one muscle's force.
- Jorgensen (1970) and Sprigings–Neal (2000): retained only as the implementation's
  stated reference-band provenance. Exact intervals have not been independently
  verified in those papers; the Sprigings–Neal publisher page was inaccessible.

## Provider and Historical Evidence

Read the article's referenced Tools implementation and design contract at local
revision `dcd4b2ae9e0e3aa665280efb20769ea2b5d33948`, with the inspected source
files unchanged in that checkout. Pin links to that revision. The closed
Tools #4785 issue and the original AffineDrift source preserve the reported
experiment numbers. A retrieved issue snapshot is retained in local review
scratch space; no source-level solver artifact was recovered for every table.
Do not equate narrative provenance with independent reproduction.

The provider prose still contains corresponding overclaims and a 0.31-versus-
0.50 kg arithmetic typo. The AffineDrift correction does not silently modify
that upstream implementation or claim its wording has been repaired. The bounded
provider follow-up is [Tools #5393](https://github.com/D-sorganization/Tools/issues/5393).

## Delegation and Adjudication

Two parallel agy Gemini 3.8 Flash supplied-text inventories covered numbers and
claims. No delegated tools, edits, or publishing. The lead rejected suggestions
that mistook a failed 6.8 m/s model output for a literature measurement, called
90% release premature, assumed physical club length was the model length, or
treated all Miura results as one evidence category. Adopted findings were
independently derived or checked against primary sources.

## Validation and Publication Status

Twelve independent numerical cases pass: body-energy assembly, normalized bound,
tip-mass and singular limits, distributed coefficient, realizability, coupling
error, inertia arithmetic and origin shifts. Eight article-boundary cases and
one workbench-summary case failed before their respective corrections; all
21 checks now pass. Ruff, Black and the 651-source title-case gate pass.

Initial root-project HTML render succeeds. Complete browser inspection,
revision-bound evidence, full repository validation and protected delivery
remain pending. The corpus row must not be marked complete until the bounded
review and publication checks finish. Other sources retain their independent
review status.
