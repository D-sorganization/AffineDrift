# ADR 0001: Canonical Frontend Asset Ownership

- Status: Accepted
- Date: 2026-02-13
- Owners: AffineDrift maintainers

## Context
Historically, frontend assets existed in multiple mirrored locations and drifted.

## Decision
Maintain one canonical source per synchronized asset and enforce sync checks in CI.

## Alternatives Considered
1. Keep all copies hand-maintained
2. Move all assets into docs-only generated output

## Consequences
- Positive: Reduced drift and deterministic PR review surface.
- Negative: Requires sync tooling and contributor discipline.
- Follow-up work: Continue reducing mirror set where possible.

## Validation
- `scripts/sync_frontend_assets.py --check` remains green.
- No PR introduces unmanaged mirror divergence.
