# Falsification Atlas Technical Review

Issue #4749 is a child of epic #4009. The reviewed surface is the entire six-card
atlas, its canonical wrapper and editorial mappings, and its renderer and tests.
The imported monograph's six claim records were read in full. This is not a
fresh review of every linked monograph chapter or a rerun of its simulations.
The prior route record is preserved in `atlas-prior-review.json`.

## Findings and Corrections

1. **Evidence Labels:** A source-reported supported claim and an unavailable
   registered workflow describe different evidence layers. Label source status,
   declared domain, uncertainty, editorial comparisons, critique disposition and
   workflow registration separately. In particular, an untested hypothesis's
   negative uncertainty statement must not appear beneath an affirmative
   “establishes” label. Preserve imported statements verbatim.
2. **Endpoint and Intervention:** One matching scalar endpoint does not determine
   the full terminal state or internal history. A same-state intervention needs
   complete memory variables and a declared command/feedback policy; command
   removal does not generally remove force instantaneously. Do not infer that
   arbitrary competing histories are admissible.
3. **Contact Identifiability:** Opposite contact-force increments preserve
   resultant force but generally change moment. In the ideal point-force model,
   increments along the separation line preserve the complete wrench. State
   contact limits and common reference points. Internal rigid-body power can
   vanish with nonzero contact loads; muscle effort is not thereby identified.
4. **Coordinate Metrics:** Covectors and Jacobians transform together and
   preserve their physical power pairing. Reapplying an unweighted residual norm
   after coordinate scaling changes the force fit. The scalar example gives
   0.5 before scaling and 0.8 after scaling; transforming the metric restores
   0.5. A non-diagonal shear test guards the order in the general transformation
   `W_z = S^-1 W_q S^-T`. Minimum-norm selection is an additional convention
   when the fit has multiple minimizers, not biological evidence.
5. **Supports and Compliance:** Fixed ideal supports can exchange momentum with
   zero boundary work; moving supports can exchange energy. Replacing a support
   changes the plant. Elastic energy magnitude alone does not determine the
   sign, destination or timing of transfer. Separate fixed-command comparisons
   from matched-delivery comparisons and account for external constraints and
   rigid-reference inertias.
6. **Falsifier Scope:** Source-stated falsifiers include numerical checks,
   scientific comparisons and editorial boundaries. Distinguish them explicitly.
   Extra measurements do not refute non-identifiability from net wrench alone;
   an operational test of an untested relationship needs a specified effect,
   uncertainty and rejection criterion. Preserve the source statements and
   explain the limitation rather than silently editing the authority.

## Evidence and Limits

The imported provider revision is
`85cce4d3307bb7ad3953d9fc6e583e370803515c`. Its
[registered rotating-base artifact](https://github.com/D-sorganization/UpstreamDrift/blob/85cce4d3307bb7ad3953d9fc6e583e370803515c/docs/research/proximal_distal_energy_transfer/data/rotating_base_torso_velocity_study.json)
was read from that Git object. The three selected 30 ms branches report zero
pre-branch state difference and continuing-minus-removed-command delivery-speed
differences of 1.2227382449148392, -1.3642478456036784 and 1.8176278535896682 m/s.
The wrist-command contact-work difference is -3.001175758902944 J. This checks
reported numbers, not simulation execution or physical accuracy. The artifact's
general interpretation field still describes a torso-only removal; the atlas
uses the explicitly identified per-channel results and does not generalize that
stale sentence. Targeted chapter passages were consulted without claiming a
full new chapter audit.

[Modern Robotics, Section 5.2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/)
provides the virtual-power derivation of the Jacobian-transpose mapping. The
two-contact counterexample, weighted-fit example and spring-rate check are
independent synthetic calculations. They supply no measured golf distribution,
human control strategy, metabolic estimate or participant validation.

The provider publication issue #9174 records progress beyond an entirely absent
software foundation. The atlas now states its own registration limitation
instead of claiming the provider has published nothing. No unavailable workflow
was promoted and no authority digest or source adjudication was changed.

## Delegation and Adjudication

Five supplied-text agy `gemini-3.8-flash-high` jobs supported card inventory,
provenance inventory, numerical-test drafting, final notation review and a turnover checklist.
The lead checked every accepted change. Rejected suggestions include treating
different status layers as contradictory, equating force magnitude with muscle
effort, and using `(S S^T)^-1` as the general transformed covector metric.
The numeric tests include a shear to expose that last error. The notation pass
correctly identified the misleading phrase “wrist speed”; the final text refers
to delivery speed under the wrist-command intervention.

## Reading Surface

Mobile inspection revealed nested global display-math size rules shrinking the
new equations. Multi-line equations and an atlas-only inherited-font override
restore reading size without changing the global stylesheet. The final page
passes all four viewport/theme cases and axe; 37 math expressions render with
no math errors or page overflow.

## Validation and Continuation

The accompanying `atlas-validation.json` records exact source digests and test
and browser outcomes. Validation applies to this atlas surface; it is not a
site-wide scientific completion or deployment claim. Canonical handoffs and the
development log retain PR dependencies and the remaining corpus count.
