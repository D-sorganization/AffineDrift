# Induced Acceleration: Paired Chapter Review

## Scope and Argument

Issue #4425 belongs to Physics #4054, corpus #4021 and epic #4009. Both complete
Chapter 30b sources, including exercises, were read. The earlier web-only
attribution correction did not reconcile the print edition. This review replaces
both bodies with the same derivation and preserves the shared normative web
include, the print attribution record, equation labels and historical section
destinations. It establishes analytical examples, not a new human-golf dataset.

## Findings and Corrections

1. **P1 — Constraint baseline.** Derive the coupled equality-constrained solve,
   its Schur complement and affine force map. Count curvature once; distinguish
   homogeneous force increments from complete isolated-force solves. State rank,
   velocity-coordinate and contact-feasibility assumptions. A circular-guide
   example independently exposes double-counting and reaction dependence.
2. **P1 — Physical output.** Derive point acceleration as joint acceleration
   projection plus Jacobian transport. Distinguish tangential speed rate from
   acceleration magnitude. A rotating-point counterexample and fully specified
   two-rod ledger show that zero angular acceleration need not mean zero point
   acceleration and that large signed terms can cancel.
3. **P1 — Coupling and index.** Replace the every-joint assertion with an exact
   zero-cross-response posture. Define a two-coordinate normalized ratio without
   conflating inverse-matrix entries and reciprocal diagonal mass entries.
   Generalize passive coordinates by a block solve. Equal-torque mobility remains
   reciprocal while differently normalized ratios can differ eightfold. State
   units and coordinate scaling; do not attribute our independently derived
   equation to an uninspected full-text Challis convention.
4. **P1 — Representation.** Prove invariance of a fixed physical output increment
   under consistent coordinate, force, mass and Jacobian transformations. A
   nonlinear free-particle coordinate example supplies the missing transport
   term. Representation-dependent components do not imply arbitrary physics.
5. **P1 — History and intervention.** Separate instantaneous terms, nominal
   integrals and integrated interventions. Distinct double-integrator inputs
   reach the same state; a nonlinear scalar model has a removed-input trajectory
   different from its nominal input integral. Neither drift nor current velocity
   uniquely reconstructs previous muscle action.
6. **P1 — Plant, muscle and energy interpretation.** Include the kinematic drift
   block and complete autonomous force model. Require actuator equations before
   equating generalized control with excitation. Separate inverse-dynamics net
   moments, estimated muscle forces, acceleration, interface power and energy
   transfer. Retain hybrid/contact and uncertainty limits without replacing
   technical explanation with repeated disclaimers.
7. **P1 — Literature and novelty.** Remove first-golf-application, universal
   late-swing dominance, unsupported shoulder-speed numbers, protective intent
   and diagnostic/intervention claims. Correct the walking explanation so the
   gastrocnemius energy result does not erase its reported support/progression
   functions. Remove unverified model-size particulars and the misleading
   pectoralis-major biarticular exercise. Cite prior golf pelvis research.
8. **P2 — Bibliography and paired pedagogy.** Correct Zajac/Gordon's volume from
   16 to 17 in both textbook databases; add Takagi's prior golf paper and five
   DOI fields in the Physics database. Remove six interpretive bibliography
   notes, which otherwise republished overclaims below the corrected chapter.
   Other existing entry fields are unchanged. Supply numerical answers in the
   chapter/exercises and a common physical-output investigation workflow.

## Primary Sources and Access Limits

- [Hirashima et al. (2008)](https://doi.org/10.1016/j.jbiomech.2008.06.014):
  primary ten-page PDF from the StFX university archive; abstract, introduction,
  methods, results and discussion text read. Appendix points to online
  supplementary material that was not obtained. No reproduced experimental
  dataset, full figure digitization or supplemental-method certification.
- [Challis (2011)](https://pubmed.ncbi.nlm.nih.gov/21723558/): abstract and
  author-institution metadata. The reported standing comparison stays attached
  to that source. The exact full-text index convention was not inspected.
- [Takagi et al. (2021; online 2019)](https://pubmed.ncbi.nlm.nih.gov/31038009/):
  abstract and metadata support prior golf pelvis acceleration research. Full
  methods were not inspected; no equivalence to our chapter's model is claimed.
- [Neptune et al. (2001)](https://pubmed.ncbi.nlm.nih.gov/11672713/): complete
  abstract supports the bounded walking example. Full paper not used to certify
  contact implementation or reproduce simulation results.
- [Caruthers et al. (2016)](https://pubmed.ncbi.nlm.nih.gov/27341083/): complete
  abstract supports optimization before attribution and the selected output
  directions; remove unverified 46-coordinate/194-actuator particulars.
- [Riley and Kerrigan (1999)](https://pubmed.ncbi.nlm.nih.gov/10609629/): metadata
  supports the application topic; no detailed patient or treatment claim retained.
- [Zajac and Gordon (1989)](https://pubmed.ncbi.nlm.nih.gov/2676547/): metadata
  confirms volume 17. No abstract was available and the full review was not read.

## Validation and Acceptance Boundary

Nine independent chapter tests plus eleven existing constrained-superposition
tests pass. The existing fourteen attribution-contract tests also pass when
explicitly selected with the content-lint marker. The new tests include a finite
difference of endpoint position, ODE integrations and an independent block solve;
they do not merely search the article for expected formulas.

All 128 body math expressions match between editions after whitespace/label
normalization. The existing format-specific attribution records are excluded
from that count and checked by their dedicated contract tests. The shared web
include remains byte-identical. The isolated print chapter uses the real book
preamble and bibliography; all ten pages were inspected. Final log has no
overfull boxes, undefined references or duplicate labels. This is chapter-level
acceptance, not a full-book build.

The root-configuration public route passes all four mobile/desktop, light/dark
production verification cases, with no serious/critical axe violations. A
separate settled browser walk renders all 139 expressions, including the shared
record, in each case with no math errors, unresolved lazy nodes, broken local
anchors or document overflow. Detailed equation and horizontal-scroll evidence
is recorded in the companion render-verification JSON before final binding.

The route remains explicitly reopened until the complete review/render evidence
is committed and bound. Prior Chapter 15/16/22 bibliography dependencies require
an exact-byte carry-forward audit; their scientific content is not re-reviewed
or silently promoted by this chapter's acceptance.
