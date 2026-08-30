# AffineDrift Website and UpstreamDrift Companion Review

Date: 2026-08-29
Status: Package A protected and deployed; Packages B–E remain governed work

Protected delivery: issue #4080 / PR #4083 / merge
`75042154b05c2a04351b0d47e6ed44c994243476`.

## Executive Finding

AffineDrift has unusually strong long-form material, governed scientific caveats, and reproducible publication evidence, but its public information architecture has not consistently communicated that strength. The principal problem is not a shortage of content. It is that readers can encounter articles, software links, provisional workbenches, technical monographs, and research-readiness records without a stable explanation of which repository owns computation, which revision is authoritative, what evidence state applies, or what to do next.

The proximal-to-distal publication is the clearest example. It is a substantial
governed monograph that was previously presented more like a specialized
article than a peer of the longer books. Protected PR #4083 corrected that
discovery problem without changing the immutable monograph source.

## Companion Contract

The two repositories should present one program with distinct authority:

- **UpstreamDrift owns computation.** It owns executable models, scientific records, claims, critiques, release manifests, calibration and qualification results, and campaign state.
- **AffineDrift owns explanation and immutable publication.** It owns the reader journey, long-form synthesis, stable projections, limitations, learning paths, and links to exact protected UpstreamDrift evidence.
- **Neither repository may silently borrow the other's authority.** A readable AffineDrift page is not evidence that an UpstreamDrift calculation reproduced. An UpstreamDrift fixture or simulation is not human validation, coaching advice, or publication authority.
- **Mutable branch links are navigation, not evidence.** Scientific statements must resolve to protected revisions or governed release records.

This contract should be visible wherever a reader can move between reading, evidence, and execution.

## Content and Argument Gaps

### 1. Model evidence can be read as human evidence

The site discusses mechanics, motor control, anatomy, equipment, and sequencing in adjacent surfaces. Even when individual caveats are accurate, adjacency can imply a stronger causal chain than the evidence establishes.

Improvement:

- Show an evidence ladder on synthesis pages: mathematical identity, manufactured fixture, qualified simulation, measured participant result, replicated result, and bounded application.
- State the current rung for every featured program.
- Keep technique, anatomy, physiology, injury, equipment fitting, and coaching conclusions unavailable unless separately supported.

Further research:

- Participant-level perturbation and held-out validation.
- Measurement-error propagation from markerless kinematics through inverse dynamics and attribution.
- Sensitivity to coordinate choice, constraint model, contact model, soft-tissue artifact, and residual handling.

### 2. Proximal-to-distal sequencing lacks one compact falsification map

The monograph contains detailed mechanics and limitations, but a reader still has to assemble the decisive counterexamples across chapters: similar endpoint outcomes from different internal pathways, timing changes without beneficial transfer, coordinate-dependent attribution, two-hand ambiguity, prescribed-base artifacts, and shaft/contact confounding.

Improvement:

- Add a governed "claim / alternative / discriminating measurement / current state" explorer derived from existing claim and critique records.
- Link each row to the exact monograph chapter and protected UpstreamDrift record.
- Preserve adverse and unavailable outcomes rather than summarizing only qualified cases.

Further research:

- Counterfactual interventions that distinguish timing correlation from causal transfer.
- Model-family comparisons using the same coordinates, loads, phase windows, and output definitions.
- Identifiability analysis for bilateral hand forces and muscle-level interpretations.

### 3. Reading and running are not yet one continuous journey

The site has a monograph, companion article, model workbench, Software page, and UpstreamDrift links, but the transition from conceptual reading to exact reproduction is still distributed.

Improvement:

- Standardize a three-step panel: **Read the explanation -> inspect governed evidence -> reproduce in UpstreamDrift**.
- Display the protected UpstreamDrift revision, compatible AffineDrift projection revision, environment/profile, release state, and known blockers together.
- Provide copyable commands only when the pinned release makes them truthful and reproducible.

Further research:

- Reproduction success across clean Windows and Linux environments.
- Time-to-first-qualified-result and failure categorization for new users.
- Version-compatibility testing between projected publications and provider releases.

### 4. Publication state vocabulary is rigorous but cognitively expensive

The governed state model is a strength, yet readers should not need repository context to distinguish available, scaffolded, simulation-ready, validated, published, and deferred.

Improvement:

- Use the same compact state badge and plain-language definition on cards, page headers, search results, and evidence panels.
- Pair every state with "this establishes" and "this does not establish."
- Never use visual prominence to imply a higher evidence state.

Further research:

- Comprehension testing with technical and nontechnical readers.
- Search-result snippets that preserve state and limitations outside the source page.

### 5. The site lacks a single cross-repository coverage map

Readers can find models and publications but cannot quickly see which scientific questions have a model, an executable workflow, a governed record, a public explanation, a critique, or a validation protocol.

Improvement:

- Build a generated program matrix from governed manifests rather than maintaining prose duplicates.
- Recommended columns: question, AffineDrift reading, UpstreamDrift implementation, model tier, evidence state, claim/critique coverage, reproduction status, human-data status, and next falsifier.
- Fail the build on broken protected pins or contradictory states.

### 6. Findability claims are not yet supported by user evidence

The #4080 navigation and layout changes improve objective visibility, but no user study yet proves better discovery or comprehension.

Improvement:

- Track privacy-preserving navigation events for Books, monograph, evidence, and workbench transitions only after governance approval.
- Run task-based usability review: find the long monograph, identify its evidence state, locate the provider record, and explain one limitation.
- Treat analytics as interface evidence, not scientific validation.

## Delivered in #4080 / PR #4083

- Promoted the proximal-to-distal monograph into the primary Read navigation.
- Featured it on the homepage and as an equal long-form card on the Books hub.
- Widened the desktop Books layout to a centered three-column long-form library, with two columns at intermediate width and one on mobile.
- Expanded the article catalog from 34 to 37 entries and added direct discovery surfaces.
- Added proximal-to-distal routes to the golf-science and biomechanics learning paths.
- Reframed Models and Software as read-to-evidence-to-workbench journeys.
- Replaced mutable companion/workbench authority links with local governed evidence or exact protected pins.
- Added search targeting and cross-surface authority regressions.
- Refreshed book, claim, and trust-surface audits while leaving the immutable monograph tree unchanged.

## Selectable Feature Packages

### Package A — Discovery and Desktop Polish

Status: delivered and live at protected merge `75042154`.

Scope: the protected #4080 implementation.

Benefits:

- Immediate improvement to desktop hierarchy and long-form discovery.
- Low scientific risk because canonical monograph content is unchanged.
- Strong automated and responsive-browser verification surface.

Limits:

- Improves findability but does not prove comprehension.
- Does not itself make UpstreamDrift reproduction easier.

Acceptance gates:

- [x] Full-route Quarto render, site health, and 231-route manifest.
- [x] One visible H1 and no overflow at 390 px mobile and 1440 px desktop.
- [x] Light/dark inspection, search discovery, and 924 browser cells.
- [x] Immutable projection verifier and zero source-manifest drift.

### Package B — Governed Companion Dashboard

Scope: generated compatibility and evidence panels on the monograph, companion, workbench, Models, and Software routes.

Benefits:

- Makes the AffineDrift/UpstreamDrift boundary immediately legible.
- Gives readers one protected route from explanation to evidence and reproduction.
- Reduces stale prose and mutable-link risk.

Costs and risks:

- Requires a stable machine-readable provider release contract.
- Must fail closed when protected UpstreamDrift evidence is absent.

Acceptance gates:

- Exact provider/projection revision pair.
- Deterministic generated panel with schema validation.
- Broken-pin, stale-release, unavailable-evidence, and state-contradiction tests.
- Windows/Linux clean-environment reproduction evidence.

### Package C — Claim, Critique, and Falsification Explorer

Scope: a generated reader interface over existing governed claim, critique, route-audit, and research-readiness records.

Benefits:

- Addresses the substantive argument holes directly.
- Makes alternative mechanisms and missing measurements first-class.
- Supports reviewers without duplicating scientific authority.

Costs and risks:

- Requires careful language to avoid presenting ledger completeness as scientific consensus.
- Needs accessibility and large-table performance design.

Acceptance gates:

- Every displayed claim and critique resolves to an exact governed record.
- Missing, superseded, private, adverse, and unavailable states remain visible.
- No client-side rewriting of scientific status.
- Keyboard, screen-reader, mobile, and print/PDF checks.

### Package D — Reproducible Study Workbench

Scope: bounded, pinned reproductions for selected monograph figures and tables.

Benefits:

- Most direct expression of the two-repository companion vision.
- Turns long-form explanations into inspectable computational experiments.
- Makes coordinate, sign, tolerance, and solver assumptions concrete.

Costs and risks:

- Highest implementation and maintenance cost.
- Must not execute mutable provider code or imply that a successful fixture is human validation.

Acceptance gates:

- Protected provider release and exact environment lock.
- Two-build byte stability where promised.
- Adverse fixture and negative-control preservation.
- Downloadable provenance bundle and independent reproduction review.

### Package E — Reader Validation and Editorial Augmentation

Scope: structured external review of findability, comprehension, and argument coverage.

Benefits:

- Tests whether the architecture works for actual readers.
- Produces evidence for prioritizing B, C, or D.

Costs and risks:

- Requires participant/privacy governance and a declared sampling frame.
- Interface feedback cannot validate biomechanical claims.

Acceptance gates:

- Preregistered tasks and success measures.
- Separate technical-reviewer and general-reader cohorts.
- Privacy-preserving data handling and reported uncertainty.
- Public limitations and negative findings.

## Recommended Sequence

1. Package A is complete at protected `75042154` with live deployment evidence.
2. Complete UpstreamDrift #9174/#9190–#9193 before exposing a new reproduction promise.
3. Implement Package B through existing AffineDrift #4010/#4022–#4030.
4. Implement Package C from the same governed data through #4084/#4086/#4087 and #4032.
5. Complete the narrow Package D pilot through #4028/#4029/#4042 only after B is stable.
6. Run Package E through #4088 before expanding the workbench or claiming improved discovery.

## Decision Points

- **Delivered discovery baseline:** Package A / #4080 / PR #4083.
- **Programming companion:** #4010 and #4022–#4030, sourced from UpstreamDrift #9174.
- **Scientific-review companion:** #4084, #4086, #4087, and #4032.
- **Executable companion:** #4028, #4029, and #4042 after the provider contract is protected.
- **Reader evidence:** #4088; whole-site desktop regression is #4089.

## Safety and Publication Boundaries

- The large deletion summaries observed during this work are not accepted as evidence of content loss. Git ranges, deleted paths, immutable manifests, and the completed post-render tree must be checked independently.
- Generated Quarto output may disappear and reappear during rendering or pruning. Canonical QMD, source manifests, PDFs, code, tests, and protected Git history are the content-loss authority.
- #4042 has a reviewed partial local adapter but remains unpublished because 14
  standard-lane publication/reproduction contracts still fail. They may not be
  hidden, skipped, or deselected to obtain a green check.
- UpstreamDrift #9267 remains blocked until the exact CPython 3.11.15 authority lane produces a reviewable record, publication manifests are rebuilt from that accepted record, and protected checks pass.
- No package may promote manufactured, simulation-ready, deferred, private, or unavailable evidence into human validation or application guidance.
