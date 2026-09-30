# Induced Acceleration in Biomechanics: Paired Review

Issue [#4706](https://github.com/D-sorganization/AffineDrift/issues/4706), corpus
#4021, epic #4009. Review started 2026-09-30 after explicit user resumption.

## Scope and Purpose

Read both complete Geometry of Motion Chapter 3b sources. Preserve their six
major sections, historical LaTeX labels and shared normative attribution record.
Reconcile the print/web discrepancies and connect the literature to a complete
mechanical account. The Physics of Golf IAA chapter (#4425) supplies independently
reviewed neighboring treatment and reusable numerical tests; it is unchanged.
This is a chapter review, not completion of whole-book scientific reconciliation.

## Findings and Resolutions

1. **P1: Signs and complete forces.** Stop changing the meaning of the gravity
   symbol between equations. Separate potential gradient from gravitational
   force. Include passive, external and residual channels without duplication;
   distinguish positive-definite inertia from actuation and constraint rank.
2. **P1: State and input.** Supply the missing kinematic drift block and zero
   upper input block. Distinguish moment input from excitation through an
   activation-state example. Include all autonomous terms and state exactly
   when the constrained lower blocks share an affine operator.
3. **P1: History.** Replace cumulative-effect equals drift with three distinct
   operations: instantaneous partition, nominal trajectory integrals, and
   forward interventions. Retain valid nominal integration for absolutely
   continuous velocity and add impact-law velocity jumps across impulsive events;
   give the variational
   equation and a nonunique-history counterexample. Do not claim earlier inputs
   uniquely determine later force labels.
4. **P1: Coupling index.** Replace ambiguous inverse-element notation with an
   independently derived two-coordinate ratio. Its directional asymmetry is
   compatible with equal-torque reciprocal mobility. A multi-articular force
   channel combines columns; scalar passive-coordinate division does not
   generalize to coupled blocks. Declare units, scaling and denominator limits.
5. **P1: Contact and outputs.** Derive reaction recovery and the constraint
   baseline; count it once. Add a KKT-checkable fixture and unilateral release
   example. Distinguish compliant contact perturbation from fixed-state force
   response. Include physical-point Jacobian transport, tangential speed rate,
   and nonlinear coordinate transport.
6. **P1: Primary studies.** Correct trunk versus whole-body COM in the walking
   example, retain phase-specific roles, distinguish the 2007 throwing method
   from the 2008 coupled calculation, and distinguish three force components
   plus ten moments from individual muscle torques. Replace the inaccurate
   characterization of segment equations with the actual simultaneous-solve
   issue. Remove unsupported actuator counts and treatment-success claims.
7. **P1: Validation and golf interpretation.** Closure and reconstruction do not
   establish anatomical identifiability. Add a conditioned-force-error example,
   independent validation targets and a linked explanation of posture, history,
   contact, actuator dynamics, physical output, power and control limits.
8. **P2: Paired publication.** The web/print bodies now share their argument and
   mathematics. The print normative record explicitly limits its linear
   coordinate-change example to a constant invertible transform. Other chapter
   sources and historical review reports retain their independent status.

## Primary Evidence and Access Boundaries

- [Neptune et al. (2001)](https://pubmed.ncbi.nlm.nih.gov/11672713/): complete
  primary abstract, including the 1.5 m/s simulation and trunk/leg output
  definitions. Full contact implementation and actuator count not certified.
- [Hirashima et al. (2007)](https://pubmed.ncbi.nlm.nih.gov/17079349/): primary
  abstract identifies nonorthogonal torque decomposition and speed conditions.
- [Hirashima et al. (2008)](https://doi.org/10.1016/j.jbiomech.2008.06.014):
  primary PDF from the StFX university archive, specifically introduction,
  methods, nomenclature and results. Verified cohort, four segments, thirteen
  coordinates, force/moment distinction, coupled-solve criticism and nominal
  integrals. No experimental rerun, figure digitization or supplement audit.
- [Challis (2011)](https://pubmed.ncbi.nlm.nih.gov/21723558/) and
  [author-institution record](https://pure.psu.edu/en/publications/an-induced-acceleration-index-for-examining-joint-couplings):
  abstract and metadata. Full-paper index convention remains unavailable;
  our equation is explicitly our derivation, not an asserted transcription.
- [Riley and Kerrigan (1999)](https://pubmed.ncbi.nlm.nih.gov/10609629/): complete
  primary abstract confirms ten stroke participants and ten controls,
  subject-specific calculations and acceleration comparison. No intervention
  efficacy trial is claimed.
- [Caruthers et al. (2016)](https://pubmed.ncbi.nlm.nih.gov/27341083/): primary
  abstract confirms static optimization, population and directional COM terms.
  Unverified 46-coordinate/194-actuator particulars were removed.
- Zajac/Gordon, the two-part walking review, Kepple, Schutte, Silverman and the
  2011 Hirashima chapter retain bounded contextual citations. No new full-paper
  verification is claimed. DOI attempts for Schutte and Silverman and the
  author-hosted 2008 review PDF were inaccessible. The existing bibliography
  already dates Silverman's chapter 2018 despite its historical 2014 key.

## Delegation and Independent Judgment

Two parallel supplied-text-only agy Gemini 3.8 Flash inventories covered equation
assumptions and empirical claims. No tools, files, network, edits or publishing
were delegated. The lead derived the corrections and checked adopted claims.
Accepted the sign, state-dimension, input-map and study-specific verification
checklists. Rejected the suggestion that positive-definite inertia requires an
entirely unconstrained system: an ambient independent-coordinate inertia can
remain positive definite while equality constraints are solved separately.
Also rejected equating kinematic agreement with only an algebraic consistency
test; it can provide physical evidence, whose strength depends on independence.

## Validation State

Before correction: five independent numerical checks passed and fourteen
paired-source boundary regressions failed. After correction: all nineteen new
checks and nine existing IAA numerical checks pass. Fourteen existing shared
attribution contracts also pass. Ruff and Black pass for the new test module.

The complete 149-page Volume I PDF builds through LaTeX, BibTeX, index and two
final LaTeX passes. Final log has no overfull boxes, undefined references or
multiply defined labels. All six changed chapter pages (physical 58–63,
printed 44–49) and the following chapter transition (physical 64) were visually
inspected. The root-website production gate passes all four desktop/mobile and
light/dark combinations; axe scans the route once with zero serious or critical
violations. A fresh browser session renders all 126 math expressions, including
twelve display equations, with zero math errors, unresolved lazy placeholders,
broken internal anchors or document overflow. All display equations were visually
inspected at 1440 and 390 pixels. Three numbered mobile equations use contained
horizontal scrolling; both ends and their numbers were checked. Title views were
inspected in both themes. The initial browser session retained stale content via
a service worker and is excluded from accepted evidence.

Initial source checkpoint `f30e64cbcbef1b68692b5b5a7a92f0966a840d97` and the first
render receipt preserve the initial review. The final source adds the explicit
impact qualification after integrating main's separate Binder update (#4682).
`iaa-biomechanics-final-render-verification.json` records the final source/PDF
digests and post-integration browser checks. The PDF remains 149 pages with the
same chapter range; reflowed physical pages 60–63 were visually reinspected.
Repository-wide checks and protected publication are tracked in the current
turnover and development log; this report does not certify other chapters.
