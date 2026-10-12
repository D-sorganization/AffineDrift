# Shot-Pattern Publication Technical Review

Review date: 2026-10-11. Reviewer: Codex publication-review subagent.
Base reviewed revision: `0e33178dfd8c9d80b1be4b9c3130178fe085343f`.
The final uncommitted metadata, denominator wording, and navigation repair
was reread on the same date; its exact source hashes are recorded below.

## Scope and Evidence

This is a scoped review of the complete publication QMD, its numerical
summary against selected sections of the canonical upstream LaTeX and text
extracted from the frozen PDF, and visual inspection of `summary.png` and
`facebook_preview.png`. It is not an independent simulation rerun, full
upstream-code audit, full PDF page-layout review, or empirical qualification.
The six linked density/flight plates were hash-checked, not visually reviewed
in this review. Full-site rendering and deployment verification are separate
gates and are not established by this receipt.

The upstream source consulted is
`D-sorganization/UpstreamDrift:docs/research/shot_pattern_analysis/shot_pattern_analysis.tex`,
with SHA-256
`99582319359e5957d538580005ec61656592cccabcab3518d8260620597a0ac2`.
The PDF's relevant text was independently extracted with `pdftotext -layout`.
All nine publication assets match their existing asset-manifest hashes.
The immutable report SHA-256 is
`fd5506da87f5e619a550fb8cc871a0e8195b6fb98965a99809e3238a0f01508b`.

## Evidence Findings

The six QMD scoring ranges agree, with display rounding, with the canonical
LaTeX's Selected Relative-SG Ranges and Pointwise Interval Directions table
and frozen PDF Table 12:

| Club and Pattern | Minimum | Maximum | Positive/Negative/Spans Zero |
|---|---:|---:|---|
| Driver Draw | +0.00002691177 | +0.007797655 | 6/0/2 |
| Driver Fade | -0.001460539 | +0.000234387 | 1/4/3 |
| Seven-Iron Draw | -0.00135572 | -0.0002882714 | 0/8/0 |
| Seven-Iron Fade | +0.0008933618 | +0.002581634 | 8/0/0 |
| Pitching-Wedge Draw | +0.00009508286 | +0.0111171 | 6/0/2 |
| Pitching-Wedge Fade | -0.01096597 | +0.0002919228 | 1/6/1 |

The article correctly identifies eight selected zero-lean conditions per club,
positive Fade and negative Draw intervals for the selected seven-iron cases,
and mixed directions/zero-spanning intervals elsewhere. The source supports
10,000 attempts per executed pattern/condition, nominal target tolerance
0.05 m, RK4 production time step 0.02 s, 100 replay paths per pattern, and
the hypothetical 400 m driver scoring context. These are source consistency
checks, not fresh checks of the underlying calculations.

One correction was required: the original QMD described 10.44 million
attempted rows as including unavailable nominal matches. The source inventory
instead totals 8.1 million completed-primary attempts, 1.56 million
completed-control attempts, and 0.78 million supplemental attempts.
Unsupported outcomes are included in attempted rows; unavailable nominal
matches remain separate inventory records and contribute no simulated rows.
The final QMD repair preserves that distinction and resolves this finding.

## Uncertainty and Audience Framing

The QMD distinguishes supported endpoint populations from common-pattern
scoring and paired populations. It retains unsupported outcomes, disclaims
physical impossibility from bounded-search failure, and does not attribute
effects to curvature alone after rematching face, path, and speed.
Sampling intervals are explicitly separated from physical-model, course,
clubhead, and human-delivery uncertainty. No multiplicity-adjusted discovery,
individual-player recommendation, per-round gain, or empirical acceptance is
claimed. The historical scoring reference and first-contact-as-final-lie
assumption are explicit.

Both inspected graphics show the six range directions consistently with the
table, identify selected zero-lean conditions and relative SG per modeled
opportunity, and explain that the ranges are not pooled intervals or per-round
gains. The social preview explicitly says geometric simulation, conditional SG,
and not player data. The summary retains the qualification that loft closure
does not by itself determine carry. Text and axes are legible in the inspected
native images. This does not certify social-platform cropping or the final
HTML's responsive layout.

## Falsifiers and Remaining Gates

The nominal matching criterion is falsifiable by a raw endpoint residual
above 0.05 m. The linked report's replay contract rejects mismatched execution
identities or failure to reproduce saved path coordinates to 1e-6 m; selected
shot outputs normally use 1e-6 in their declared units and spin uses 1e-5 rpm.
The article's numerical summary can be refuted by disagreement with the bound
selected result tables. This review checked table transcription and image
framing, not execution of those numerical tests. No extra falsifier paragraph
is necessary for this summary page, which links the detailed methods.

Physical predictive validity requires independent measured data and declared
measurement uncertainty. It remains open. Neither successful rendering nor
the review inventory's `reviewed` status establishes that qualification.

## Configuration Evidence Carry-Forward

The prior `_quarto.yml` blob at
`21ff5811a231d1666366b2a050724af77b6d1c27` (`dc91cbc6^`) has SHA-256
`d16c913dffc8d149f643ad33fccb46f871afef7cf6c4200d51905ec7c4f3a43f`.
That exactly matches the stored configuration evidence in the reviews for
`/articles/proximal-distal-falsification-atlas.html` and
`/models/research-protocol-readiness.html`; these are the only review records
that bind this configuration file.

The publication change adds `articles/shot_pattern_analysis/` as a resource
and one navigation entry for the article. The metadata repair changes that
entry's display label to match the article title. The final `git diff
dc91cbc6^ -- _quarto.yml` comparison contains only these resource/navigation
additions. These changes do not change
the two existing routes' scientific content, equations, source imports, or
review scope. Preserve their original reviewer identities and review dates.
Updating this configuration digest records a scoped carry-forward, not a new
scientific review or approval of unrelated evidence. Inspect regenerated
ledger changes and do not renew unexplained evidence drift.

## Final Source Check

The final metadata retains the conditional model scope, uses `experimental`
publication status and the `qualified-simulation` evidence rung, and leaves
the first-publication date unverified instead of inventing publication evidence.
The rung describes the preserved study's reported numerical checks; it does
not claim fresh execution by this reviewer. The upstream primary and control
final-audit receipts report complete/pass for 324 and 72 audited cells, and
the supplemental completion receipt reports a passed saved-data audit and
restoration for 780,000 rows. The headline traceability receipt explicitly says
saved-summary traceability is not publication acceptance. I inspected these
receipt result fields, not every underlying saved sample or audit calculation.

The corrected attempted-row sentence and the final navigation label were
checked. No unresolved scientific-transcription or audience-framing blocker
was found in this scoped review. Rendering, accessibility, link resolution,
CI and public deployment checks remain separate pending gates.

| Reviewed File | SHA-256 |
|---|---|
| `articles/shot-pattern-analysis.qmd` | `6359c5ee00826365c2ddcc4fc238ccc9eefeb8057ddbc2df9d6ca97a7da42dc2` |
| `_quarto.yml` | `1b1a3e0386538735af954821806264393ab9a8a091a37c3a242bbff694953015` |
| `articles/shot_pattern_analysis/summary.png` | `6a152790f7e81440dfde1e7dc3069e7355106596f94269820750d2ab9a3bc016` |
| `articles/shot_pattern_analysis/facebook_preview.png` | `e5e610febc41025d91f3532745cf9ce5bc6dd7e29b8bec8829cfe8c9e564a3b5` |

The inventory should identify the actual commit containing these reviewed
source bytes once committed. Later changes require checking affected review
claims rather than silently carrying this receipt forward.

## Presentation-Only Mobile Title Follow-Up — 12 October 2026

The published source above has SHA-256 `6359c5ee00826365c2ddcc4fc238ccc9eefeb8057ddbc2df9d6ca97a7da42dc2`.
The follow-up source has SHA-256 `c0e8127f38dab54a504ba59f5753dcb0d28ca6bb315d95c54243915f75a9800c`.
The sole source change is `format.html.code-tools: false` for this article, which has no code blocks.
It removes an unnecessary Code control beside the title; no scientific statement, figure,
table, method, or linked asset changes. The prior scientific review remains bound to its
original source hash. The rendered mobile layout regression fails before this change and
passes afterward, and all nine published assets retain their recorded hashes and byte counts.
