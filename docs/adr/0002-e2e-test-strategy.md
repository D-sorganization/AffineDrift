# ADR 0002: PR E2E Smoke + Full Matrix Strategy

- Status: Accepted
- Date: 2026-02-13
- Owners: AffineDrift maintainers

## Context
Full browser-matrix E2E in PR gating can become slow and unstable for routine changes.

## Decision
Use fast deterministic Chromium smoke tests for PR blocking checks. Run broader matrix coverage in separate workflows.

## Alternatives Considered
1. Full matrix blocking all PRs
2. Remove E2E from PR gating entirely

## Consequences
- Positive: Faster developer feedback and less CI queue congestion.
- Negative: Some cross-browser regressions are detected later.
- Follow-up work: Ensure full-matrix workflow cadence is maintained.

## Validation
- PR E2E consistently completes within target budget.
- Smoke suite protects core routes and critical interactions.
