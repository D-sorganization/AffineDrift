# Plane-to-Space Technical Review

Issue #4724 is a native child of epic #4009. This review covers the complete
companion Chapter 20, its figure description, three cited bibliography entries,
and the archived evidence used in its argument. It does not qualify other book
chapters or modify the immutable upstream monograph.

## Scientific Corrections

The opening now identifies the planar force and moment directions correctly.
A projected trajectory is not itself a closed planar dynamics model: omitted
motion and imposed constraints can change the forces in the displayed plane.

The wrench equation declares the direction of the reference offset and pairs
the shifted moment with the matching rigid-body velocity. Both a passive rotation
and a consistent point shift preserve power for one observer. An observer boost
changes external power by minus the resultant force dotted with observer velocity.
This distinction prevents body-aligned components from being mistaken for
body-relative motion. A six-component record does not grant six independent
contact reactions, and a deforming shaft requires actual contact and internal
energy accounting beyond one rigid wrench--velocity pair.

The geometric studies now have separate feasible sets and tolerances. The open
prescribed-state atlas uses 5 mm; the bounded closure and shoulder screens use
0.5 mm. The 234-case solve changes pelvis, trunk and arm coordinates while holding
the club fixed. The 54-case paired shoulder comparison fixes trunk and club.
Its 31 closed cases and 39 successful optimizer terminations overlap in only
16 cases. Full Jacobian rank and unconstrained local nullity do not certify
bounded finite reachability, human anatomy, or a particular internal strategy.

The engine section names the independent native acceleration operators and the
shared contact law and semi-implicit step. Agreement does not qualify either
engine's native contact solver or integrator. The driver killswitch advances a
new trajectory; coincident and reversed moment-arm controls reuse achieved forces
algebraically. Their sign response verifies the moment formula, not the future
motion of an altered physical grip. The archived negative scalar is a projected
point-force moment at the declared club reference, not a pure couple independent
of origin when resultant force is nonzero.

An explicit projection bound and one-degree counterexample explain why a moment
near perpendicular to a reporting axis has a fragile sign. Rotating both the
moment and normal is distinct from choosing a new physical normal. A probability
of negative sign requires a stated uncertainty distribution. Proposed geometry,
measurement and human-validation tests are separated from completed archive results.

## Evidence and Read Scope

The exact provider revision is `a1a613999eb0c744da96caa040941955eb210a21`.
Four JSON/NPZ pairs were read from Git blobs, with `allow_pickle=False` for arrays.
`plane-space-archive-checks.json` preserves digests, recomputed results and limits.
All twelve source hashes supplied by three records match that revision. The
shoulder-screen JSON supplies no generating source hash; its result-count
implementation was inspected at the release revision without inventing provenance.
No provider engine or optimizer was executed.

Read scopes were the full companion chapter; the provider common-state chapter's
formulation, results and closure sections; the shoulder-screen opening and
result-count implementation; and the full forward-carriage chapter. Later
articulated extensions retain their earlier review scopes and were not newly
audited here. The prior two-hand archive receipt is context, not a substitute for
the new array recomputation.

Primary literature checks:

- Meister et al. (2011): bibliographic metadata, abstract and participant/protocol
  methods on the first two pages of the
  [institution-hosted paper](https://people.stfx.ca/smackenz/courses/DirectedStudy/Articles/Meister%20-%20Rotational%20Biomechanics%20of%20the%20Elite%20Golf%20Swing.pdf).
  This supports the existence of measured spatial motion, not validation of the
  particular bilateral compliant-contact hypothesis.
- Joyce et al. (2013): publisher-indexed abstract and metadata, also indexed by
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/23898684/). No full-text method review
  claimed. The abstract describes measured trunk kinematics in low-handicap golfers.
- McPhee (2022): [publisher abstract and metadata](https://link.springer.com/article/10.1007/s12283-022-00387-0)
  and author-institution bibliographic record. The chapter now calls this a narrative
  review of modeling and measurement, without attributing a separate systematic
  heterogeneity analysis to it. Existing bibliography entries require no correction.
- Lynch and Park: the complete [Modern Robotics wrench transcript](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/)
  supports the representation and power-pairing conventions. The observer-boost
  and projection examples were independently derived and tested here.

## Independent Checks and Delegation

Three new numerical cases check passive rotation versus observer boost,
projection sign reversal with a rigorous angular bound, and full-rank but bounded
infeasibility. Existing Chapter 12 tests provide independent point-force rank,
reference-shift power, deformation-power and negative-projection counterexamples.
Eight source-boundary checks failed before correction; all 26 new and reused
checks passed afterward.

Two agy Gemini 3.8 Flash supplied-text inventories were reviewed by the lead.
They had no tools, network or editing authority. The lead rejected the assertion
that only rotations preserve power: a consistent rigid reference-point shift does
too. A mixed-unit six-vector norm was not accepted as an invariant wrench magnitude.

## Publication and Scope Preservation

The figure itself is unchanged. Visual inspection shows two two-link sketches
and one arrow; its new alt text describes those marks rather than inventing a full
golfer or multiple motion arrows. Final rendering and repository-validation
receipts are recorded separately. Rebuilding the book PDF does not constitute a
new scientific review of all thirty chapters.

The original route audit and all findings are preserved verbatim as structured
records in `plane-space-prior-reviews.json`. Dependency carry-forward must verify
that only Chapter 20 and the generated book PDF changed among prior publication
dependencies. One prior text-anchor test now checks the narrower engineering guards,
0.5 mm gate and permitted trunk motion; its other functions are unchanged.
Earlier findings retain their original scientific scope.
