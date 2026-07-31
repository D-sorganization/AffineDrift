# Content Review Protocol

How to run a content review that finds real problems and does not manufacture false ones.

This protocol produced the 2026-07-31 full-corpus review: 17 units, ~940 findings, ~120 of them
P0, across 328 files and ~123,000 lines. It is written so the next review is reproducible.

## Severity rubric

Rank by how badly a **biomechanics or robotics researcher** would be misled.

| Severity | Meaning                                                                                                                                                                                                                                      |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**   | Wrong physics or mathematics a researcher would act on. Wrong sign, wrong identity, wrong units, a derivation that does not follow, a theorem without its hypotheses, a numerical result the stated model cannot produce, fabricated output. |
| **P1**   | Materially misleading or unsupported. A quantitative claim with no citation and no derivation. A method described in a way that would not reproduce. A contested result stated as settled. Notation that changes meaning mid-chapter.        |
| **P2**   | Accuracy or clarity gap. Missing hypotheses, hand-waved step, undefined symbol on first use, missing units, stale API, broken cross-reference.                                                                                               |
| **P3**   | Polish. Wording, structure, pedagogy, a place where a figure or worked example would help.                                                                                                                                                   |

## Finding format

```
### F-<unit>-<n> — <one-line claim>
- **Severity:** P0 | P1 | P2 | P3
- **File:** <repo-relative path>:<line>
- **Category:** physics-error | math-error | unsupported-claim | citation-gap |
  notation-inconsistency | outdated-api | pedagogy | rigor | cross-ref | reproducibility |
  missing-content
- **What the text says:** <short quote>
- **Why it is wrong / weak:** <specific technical reasoning>
- **Correct statement / fix:** <concretely what it should say>
- **Confidence:** high | medium | low
```

Every finding needs a real `file:line`, verified by reading the file. Never cite from memory.

## Rules that matter

**Do not pad.** A confident wrong finding is worse than no finding. If unsure, mark
`Confidence: low` and say why — but still report it if a researcher would stumble there.

**Verify before filing.** The review is only as good as its weakest accepted claim, and one
debunked finding costs more credibility than ten real ones earn.

**A finding inferred from an absence must be checked against the build.** This is the rule that
saved the 2026-07-31 review from its worst mistake. A reviewer found no rendered HTML under
`docs/articles/.../quarto/` and concluded both textbooks were unpublished — which would have been
the most alarming finding of the review. It was wrong: `.gitignore` ignores `docs/**/*.html`
because CI renders it at deploy time. **Before filing anything based on a missing file, check
`.gitignore`, the CI workflows, and the deploy pipeline.** Generated artifacts are routinely
absent from the working tree by design.

**Re-execute rather than reason.** The most valuable findings in the last review came from
reviewers who ran the code: solving the stated Clohessy–Wiltshire problem and comparing spectra,
re-deriving a mass matrix and finding a negative determinant, rendering probe documents with the
installed Quarto to prove 761 math spans use undefined macros. Inference finds fewer real
problems and more false ones.

**Check whether it is already fixed.** Past issue closure on this repository is **not** evidence
the content was fixed — issue #3321 was closed complete while the book still carried the error it
described, because the fix went to one tree only. Always verify against the working tree, in both
trees.

## Running a review

1. **Scope and inventory.** Count files and lines. Split into units of roughly one coherent
   corpus each — a textbook volume, a chapter range, an article cluster.
2. **Write a shared brief** defining the audience, the severity rubric, the finding format, and
   the domain facts to check. Every reviewer reads the same one.
3. **Dispatch reviewers read-only.** Reviewers must not edit the repository; they write findings
   to a workspace outside it. Parallel agents that edit files need worktree isolation.
4. **Run deterministic checks yourself.** Environment balance, stray document environments,
   truncation, citation resolution, cross-tree divergence. These are cheap, exact, and they
   found five P0s in the last review before any reviewer reported.
5. **Verify load-bearing claims personally**, especially any claim that would change the plan.
6. **Keep a state ledger** updated as each unit completes, so an interrupted review resumes
   without redoing work.
7. **File issues clustered by fix-site**, not one per finding — this repository's automation opens
   a PR per issue, and many small issues on one file produce conflicting PRs. P0s get their own
   issue each. Cross-tree duplicates are one issue naming both paths.

## Domain facts worth checking

Recurring problem areas, with the values to check against.

**Golf canonical numbers.** Ball 45.93 g max (R&A/USGA), diameter ≥42.67 mm. Driver head
~195–205 g, total driver ~310 g. Impact ~0.4–0.5 ms. COR ≤0.83. Smash factor ≤1.50. Tour driver
clubhead speed ~113 mph, ball speed ~167 mph. Shaft first bending ~3–5 Hz. Peak vertical GRF
~1.0–1.6 bodyweight per foot. Driver backspin 2000–3000 rpm. Golf ball `C_d` ≈ 0.22–0.28 in the
operating range.

**Dynamics.** Twists angular-first. `Ṁ − 2C` skew-symmetry holds only for the Christoffel choice
of `C`. RNEA is inverse dynamics, ABA is forward dynamics — RNEA does not "run forward". Spatial
inertia is symmetric positive definite. Closed chains make inverse dynamics indeterminate.

**Control.** Lie algebra rank condition gives _accessibility_, not controllability, for systems
with drift. Contraction requires uniform negative definiteness in a stated metric over a stated
region. Stability of each mode does not imply stability of a switched system.

**Biomechanics.** ISB conventions (Wu et al. 2002/2005; Grood & Suntay for the knee; Y-X-Y for
the glenohumeral joint). Hill-type eccentric plateau ~1.4–1.8×F₀, force-velocity → 0 at `v_max`.
Activation ~10–20 ms, deactivation ~40–60 ms. Inverse dynamics gives net joint moments only.

**Motor control.** Reflex latencies: monosynaptic ~25–40 ms, long-latency ~50–100 ms, voluntary
~150–200 ms. HKB: **anti-phase** destabilises into in-phase, not the reverse. Human CPG evidence
is indirect. The power law of practice fits better as an exponential at the individual level.
Ericsson's work does not support a universal 10,000-hour threshold.
