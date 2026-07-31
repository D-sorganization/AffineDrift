# Findings Index — full-corpus content review, 2026-07-31

A review of every piece of written content in the repository: **328 files, ~123,000 lines**,
across 17 units. Roughly **940 findings, ~120 of them P0.**

Reviewers were read-only on the repository and re-executed code and re-derived identities rather
than trusting the text. Findings that could not be verified were rejected before filing — see
"Rejected findings" below.

## Coverage

| Corpus                                  | Files |       Lines |
| --------------------------------------- | ----: | ----------: |
| The Geometry of Motion (LaTeX, Vol 0–V) |    77 |      31,611 |
| The Physics of Golf (LaTeX, ch01–ch32)  |    35 |      16,102 |
| Quarto site content                     |   191 |      60,728 |
| Bibliographies                          |     7 | 561 entries |

## Tracking epics

| Epic                                                                | Scope               | Headline                                             |
| ------------------------------------------------------------------- | ------------------- | ---------------------------------------------------- |
| [#3491](https://github.com/D-sorganization/AffineDrift/issues/3491) | Build integrity     | No book in the repository compiles                   |
| [#3500](https://github.com/D-sorganization/AffineDrift/issues/3500) | Citations           | 41 unresolved keys; 8 `\cite{}` containing prose     |
| [#3509](https://github.com/D-sorganization/AffineDrift/issues/3509) | Geometry of Motion  | Sign errors in the foundational identities           |
| [#3521](https://github.com/D-sorganization/AffineDrift/issues/3521) | Physics of Golf     | Worked examples that do not follow from their models |
| [#3522](https://github.com/D-sorganization/AffineDrift/issues/3522) | Notation            | `NOTATION.md` contradicts itself                     |
| [#3532](https://github.com/D-sorganization/AffineDrift/issues/3532) | Website articles    | Fabricated solver output; two live JS bugs           |
| [#3533](https://github.com/D-sorganization/AffineDrift/issues/3533) | Site framing        | Promises outrun what exists                          |
| [#3542](https://github.com/D-sorganization/AffineDrift/issues/3542) | Content development | What to add, not what to fix                         |

## The three systemic findings

**1. Nothing compiles, because the gate was deleted.** PR #2928 removed
`compile_textbooks.yml` and `compile_golf_textbook.yml` on 2026-04-28. Everything else
accumulated silently in the months after. One missing `\providecommand{\dd}` blocks all six
Geometry of Motion volumes; a stray `\end{document}` truncates Volume 0 after chapter 3, hiding
about 8,400 of its 9,366 lines.

**2. Fixes land in one tree while the issue is closed as complete.** Issue #3321 was closed
`COMPLETED` on 2026-06-12; its body scopes itself to `The_Physics_of_Golf/quarto/`, so the book
still says a golf ball weighs 150 grams while the website correctly says 45.93 g. The same
pattern appears _within_ files — a correction and the error it replaced, eighteen lines apart.

**Consequence: past issue closure on this repository is not evidence content was fixed.**

**3. The corpus asserts more than it demonstrates.** Numbers are typed into tables by hand, so
nothing catches a "verified stable" loop with spectral radius 1.043, a mass matrix with negative
determinant, or CVXPY output for a provably infeasible problem. Four reviewers independently
recommended the same fix: generate every number from CI-executed code.

## Rejected findings

Recorded because a rejected finding is as informative as an accepted one.

**"The textbooks are effectively unpublished."** A reviewer found no rendered HTML under
`docs/articles/.../quarto/` and concluded the navbar links are dead. **Rejected** —
`.gitignore:110` ignores `docs/**/*.html` because CI renders it at deploy time, and the repository
ships `scripts/check_quarto_render_coverage.py` as a gate against exactly that failure.

The real residue: the deploy pipeline is unhealthy — the latest run stuck `queued` since
2026-07-30, the four before it cancelled, last success 2026-07-24.

This is why [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) requires any finding inferred from a
missing file to be checked against `.gitignore`, the CI workflows, and the deploy pipeline first.

## Full findings

The complete per-unit findings files (~1.5 MB) live outside the repository at
`_review/affinedrift-content-2026-07-30/findings/`. Each issue cites its source unit and finding
ID, so any tracked issue can be traced back to the reasoning that produced it.
