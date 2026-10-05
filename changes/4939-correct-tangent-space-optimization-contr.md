---
issue: 4939
summary: "Correct tangent-space, optimization, contraction and hybrid application claims"
---

Review all six canonical tangent-series articles and the applications appendix.
Distinguish first variations from finite differences, preserve feedforward DDP
updates, state contraction hypotheses, derive event-time saltation, and separate
same-state input removal from forward counterfactual trajectories. Correct the
moving-tangent figure and the appendix's expanded plain-language rendering.

Turnover and derivations: docs/development/technical-review/tangent-applications-review/review-notes.md.
Eight groups of 100 manufactured checks pass; nine Flash jobs were lead-reviewed.
Seven pages inspected at phone and desktop widths. Frozen regression passed 7227 tests with 93.25% coverage and unchanged tracked
source; seven corpus rows accepted, leaving 42 of 407 indexed scopes. Do not
claim main delivery from a topic PR. Parent putting PR #4940 must reach main before this batch is retargeted.
