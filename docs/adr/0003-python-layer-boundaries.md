# ADR 0003: Layered Python Dependency Boundaries

- Status: Accepted
- Date: 2026-02-13
- Owners: AffineDrift maintainers

## Context
As utilities and domain logic expand, cross-layer imports can increase coupling and reduce maintainability.

## Decision
Enforce Python dependency boundaries via a CI check script and versioned rule config.

## Alternatives Considered
1. Rely on code review only
2. Enforce boundaries only for selected packages

## Consequences
- Positive: Clear coupling rules and lower architectural drift.
- Negative: Occasional refactor work when existing modules violate rules.
- Follow-up work: Extend rules as package boundaries mature.

## Validation
- Boundary checker passes in CI/deploy.
- Violations are explicit and quickly remediated.
