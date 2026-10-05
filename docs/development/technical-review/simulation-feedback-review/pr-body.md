## Problem and Result

Volume V chapters 4–6 confused inverse dynamics with integration, supplied incorrect iLQR value updates without a line search, and overstated tracking and stability guarantees. They now share the canonical three-link model, provide tested simulation and quadratic-minimization listings, and distinguish regulation, trajectory tracking, contraction and finite-time funnels under explicit assumptions. Golf interpretation separates inverse torque, an imposed optimization objective and evidence about human control.

Fixes #4927. Part of #4009 and #4021. Depends on #4930; initially targets fix/platform-model-contracts-review to isolate the diff. Retarget only after verified parent delivery to main. Do not merge into the topic parent.

## Validation

- 51 actual-listing tests failed/errored against the originals and pass after correction; 89 combined listing/reference/audit checks pass.
- Six independent checks, 100 cases each; maximum error 1.289e-10 below 1e-6.
- Frozen source bece6bee500fb24f82530794e059faab94e44531: 7172 passed, 29 skipped, 210 deselected, 60 warnings; 93.25% coverage; tracked tree unchanged.
- All five pre-PR gates passed, including 51 mapped tests.
- Rebuilt 52-page PDF with 28 references; scoped pages inspected, including final affected-page reinspection. No scoped overflow or unresolved references. One historical title overflow remains in chapter 7.
- Five successful agy Gemini 3.8 Flash reviews/proposals, lead-adjudicated. One failed oversized invocation excluded.

## Handoff

Acceptance and eight exact hashes: reports/technical-review/simulation-feedback-validation.json. Primary-reading scope, derivations, rejected findings, failure history and delivery guidance: docs/development/technical-review/simulation-feedback-review/review-notes.md. Per-issue turnover: changes/4927-simulation-feedback-review.md. Three complete corpus rows accepted, leaving 56 pending-prefix rows of 407 heterogeneous inventory rows. No complete optimizer, whole-volume or empirical human certification.
