# System Boundaries, Contact Work and Observer Power — #4783

## Scope and Status

Full canonical source under review:
`articles/proximal_distal_companion/chapters/ch02_choose_the_system.qmd`.
Baseline: `23a47f628c3f1345cc2c7fb40e6af02c96ba8368`, including Chapter 17
PR 4782 and Chapter 24 PR 4772. PR 4772 is now verified on remote main;
PR 4782 still requires protected delivery.
This is a source-review record, not a statement that the new chapter is shipped.
The 227-page PDF and HTML publication have been inspected. Initial full regression
passed 6,432 checks and failed two stale evidence-digest checks; binding and
follow-up validation are recorded separately. Final delivery remains pending.
Corpus credit stays at 117 pending until source binding is complete.

The chapter connects nine local corrections. Several carry established
qualifications into another source; they are not discoveries of new physics.
The scope does not include changing the immutable provider monograph, rerunning
its simulations, or establishing human intervention efficacy.

## Scientific Decisions

1. **Contact Work and COM Work.** An external force can change momentum without
   supplying energy at its contact. The revised chapter distinguishes local
   force power from the resultant-force COM kinetic-energy relation. Stationary
   sticking and prevented-rotation assumptions are explicit. The zero-gravity,
   supported two-mass example reconciles 20 J internal conversion, 20 J kinetic
   gain, 10 J COM gain and zero support work. A free-pair control preserves zero
   total momentum. The ground reaction enables the supported motion without
   becoming its energy source.
2. **Gravity and Actuation Counted Once.** A prescribed static external field
   admits an effective potential without adding Earth as a dynamical body.
   Gravity power and potential change are alternative ledger representations.
   An unpowered club has no internal actuator conversion: the golfer's input
   already enters through the hand interface. The same wrist work must not be
   added again under that club-only boundary.
3. **Internal Power and Compatible Motion.** Coincident positions alone do not
   guarantee cancellation. Pair power uses relative material-point velocities
   and relative angular velocities. Compatible ideal passive constraints give
   zero pairing; slip, storage, interface inertia and actuation require their
   own terms. A massless passive storage/loss balance is explicitly bounded to
   that model. A force perpendicular to relative motion still gives zero power.
4. **Representation Versus Observer.** Consistent rigid-point transport or axis
   relabeling preserves wrench power for the same observer. A nonrotating
   Galilean boost instead changes it by minus resultant force dotted with boost
   velocity. The pure-couple exception has zero resultant. Neither operation
   causes a physical change in the swing.
5. **Resultant Wrench Versus Deformation.** Rigid trajectory equivalence needs
   the same initial state, parameters, other loads and complete input history.
   A self-equilibrated axial load has zero resultant wrench but 2 W under the
   specified outward deformation field. Zero loads have the same resultant but
   zero power. This is a counterexample to unqualified flexible-body inference,
   not a measured effect size for grip or shaft deformation.
6. **Recoil and Frame.** Translational recoil follows the COM momentum identity
   for constant mass and total impulse over an interval. Large mass suppresses
   the quadratic term for bounded impulse, not the initial-velocity cross term.
   Local deformation, spin and support motion are separate. No infinite-Earth-
   mass limit at fixed gravitational constant and distance is used to justify
   a finite prescribed gravity field.
7. **Explicit Body Inventories.** Club, hands-plus-club, both complete upper
   limbs-plus-club and golfer-plus-club have named interfaces. Shoulder ports
   are external for the upper-limb inventory, while wrists and elbows are
   internal. Spanning muscles, tissues and contact elements still require an
   explicit model allocation. Enlarging the inventory does not uniquely
   identify muscle work or imply an isolated system.
8. **Verification and Evidence.** Energy closure does not independently prove
   anatomy, contact-law realism, angular-momentum closure or unique allocation.
   Pinned two-sided shaft-power and two-hand reconstruction accounts support
   the explanation within their reported scope. Human work estimates remain
   model dependent. The hypothetical transfer pathway requires compatible data,
   intervals and endpoint definitions.
9. **Figure Semantics.** The old combined gravity/ground arrow sat outside the
   outer Earth-inclusive boundary. The replacement classifies interactions and
   muscle conversion under three explicit body inventories. It makes no arrow
   imply positive energy transfer, and notes that effective field potential
   does not require including Earth. Only the existing `make_system_boundaries` function changes in
   the shared generator; four small private drawing helpers keep each changed
   function below 50 lines. All other existing function ASTs and top-level
   non-function nodes were checked unchanged. The helper extraction preserves
   the exact rendered RGBA pixels of the inspected figure.

## Primary Sources and Reading Limits

- Complete Chapter 2 read before and after revision. Complete pinned provider
  `_ch05_two_hand_wrench.qmd` and `_ch06_shaft_contributions.qmd` read at
  UpstreamDrift 85cce4d3307bb7ad3953d9fc6e583e370803515c. No new provider run or
  quantitative reproduction. The local reader links now name this revision.
- Modern Robotics 3.4 official transcript read in full. Its wrench/twist
  representation change is interpreted as representation of the same motion,
  not a change of physical observer. The resource states no publication date;
  its bibliography entry uses an access date without inventing a release year.
- MIT 16.07 Lecture 12 PDF substantive pages 1–10 read. The document is Widnall
  and Peraire, Fall 2008 version 2.0, hosted with the Fall 2009 course. Its local
  force-work examples are useful; its loose internal/external terminology is
  not imported into the chapter's explicit body inventory.
- Diaz, Herrera and Manjarres arXiv 0803.2560v2: abstract and PDF pages 1–2 through
  Eq. 13 read. No full-paper audit. Publisher-deposited Crossref metadata confirms
  AJP 77(3), 270–273, 2009, DOI 10.1119/1.3036418 and the author's accented surname.
  The DOI landing page was inaccessible to the browser tool; Crossref and the
  accessible author manuscript were used, not a guessed page range.
- Nesbit and Serrano 2005: publisher PDF pages 1–5, abstract and methods through
  subject setup read for this review. No new full-paper read. The compliant
  foot-ground model is not equated with the ideal stationary-contact example;
  modeled joint work is not presented as direct muscle measurement.
- Winter remains a general cited reference. No new full-book read is claimed.

All links and bibliographic fields are in the canonical source/bibliography.
The external references support the stated mechanics or methods; none is used
to turn these manufactured examples into a golf-performance recommendation.

## Manufactured Checks and Delegation

Eleven agy Gemini 3.8 Flash supplied-text jobs completed for this source:
length inventory, claim inventory, power algebra, work ledger, issue checklist,
test draft, test refinement, figure draft, report-spacing proofread, carry-forward verifier draft and
figure-helper extraction. The lead made scientific decisions,
checked arithmetic and reviewed generated code and figure output. These counts
are separate from Chapter 17's twelve source jobs and three delivery helpers.

Rejected or corrected suggestions include missing-compliance claims about the
original chapter, automatic power loss from any nonzero relative velocity,
unqualified recoil equivalence, an invalid fixed-field infinite-mass argument,
and describing an external field as an open thermodynamic mass system.
The test draft's support-work calculation used zero force times the moving
mass's displacement; it now uses the nonzero support force times the supported
mass's zero displacement. Pure-couple geometry is explicit. The large-mass
check uses exact rational endpoint energies to avoid subtractive cancellation.

The lead's initial test-file assembly placed the recoil tail in the wrong
function. That was corrected before the accepted RED run. The valid RED result
is 12 numerical passes and 4 source-contract failures; the source revision then
passes all 16. These checks are manufactured Newton/point-power/energy examples
plus narrow publication contracts. They do not prove the entire prose correct.

Independent preparation also checked 100 seeded 3D transport and boost identities
with errors below 1e-12. The work ledger, explicit 12 W sliding loss and 2 W
self-equilibrated deformation contrast were checked separately. The verifier draft rejected the bibliography header comments as parse failures;
the lead instead verified that the entire old bibliography is an unchanged
prefix, with exactly three additional entries and no duplicate keys. All 78
old entries and their surrounding text are preserved. Raw drafts,
rejected suggestions and execution logs remain in development QA.

The first figure inspection caught a heading crossing the first card's border;
it was wrapped and the regenerated figure inspected before final book rebuild.
The 653-source title audit and twelve publication gates pass. The rebuilt
227-page PDF matches the public copy. Physical pages 12–20 and bibliography
pages 224–227 were visually inspected: no clipped or overlapping content.
All four browser profiles pass, with no serious/critical axe findings. All
64 chapter math expressions, including ten displays, render at 390 and 1440
pixels with no errors, placeholders or page overflow. The mobile figure
zoom opens and closes; the adjacent body-inventory table provides text access.
The inline mobile figure remains small, so zoom and prose remain important.

The full Windows regression returned 6,432 passes, two stale evidence-digest
failures, 29 skips and 187 deselections. The failures concerned the rebuilt
book PDF against its old digest. They are retained in the QA log and are
not described as a green full run. The quality scanner also requires the
existing unannotated spelling of the named gravity constant; the fixture
was adjusted without changing its value. An unrestricted local scan included
untracked QA drafts; the tracked-file follow-up is recorded separately.

## Development Log Maintenance

The active log was within 46 bytes of its 200000-byte limit. Owned shipped
entries 4769 and 4766 were moved without text changes to the canonical 2026
archive, using the existing archiver's zero-day age threshold. Peer entries
were not edited. The current log has 70 validator findings versus 71 before;
the new entry has no field findings, but the portfolio warning changes from
three to four in-progress entries. This is not a whole-log validation pass.
