## Problem and Result

Volume V chapters 1–3 conflated engine capabilities with wrapper support, presented unmeasured performance rankings, and included a pendulum energy calculation with a zero initial-energy denominator and an incomplete, disconnected URDF export. The chapters now separate those claims, provide tested cylinder simulation/comparison listings and a complete URDF, and explain how model frames, inertia, external forces and actuator assumptions affect golf-swing interpretation.

Fixes #4923. Part of epic #4009 and corpus #4021. Depends on #4928; this regular PR initially targets fix/golf-capstone-review solely to isolate its diff. Retarget to main only after the parent is verified there. Do not merge into the topic parent.

## Validation

- 49 actual-listing/XML tests, including MuJoCo 3.4.0 import; all failed against the originals and now pass. 87 combined reference/audit/listing checks passed.
- Six independent mechanical checks, 100 cases each; maximum error 1.098e-9 below 1e-7.
- Frozen source 29a555d22ee4c71403259ced67b97b8c66b94ece: 7121 tests passed, 29 skipped, 210 deselected, 60 warnings; 93.25% source coverage; tracked tree unchanged.
- Rebuilt 48-page PDF, 26 references. Scoped pages inspected, including final bibliography repair; no scoped overflow or unresolved references. Two historical overflows remain in other chapters.
- Six agy Gemini 3.8 Flash reviews/proposals, with lead adjudication and rejected claims documented.

## Handoff

Acceptance and eight exact source hashes: reports/technical-review/platform-model-contracts-validation.json. Decisions, primary-reading scope, failure history and delegation: docs/development/technical-review/platform-model-contracts-review/review-notes.md. Per-issue turnover: changes/4923-platform-model-contracts-review.md. Three complete corpus rows accepted; 59 pending-prefix rows remain out of 407 inventory rows, which are scope labels rather than a scientific completion percentage. No whole-engine, whole-volume or empirical human validation is claimed.
