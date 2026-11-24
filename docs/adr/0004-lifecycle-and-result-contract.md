# 0004. Result and Lifecycle Contract

## Status

Accepted (Dieter Olson, Nov 9 2026, #5565 / #6760508859).

## Context

Across product repositories (`Tools`, `UpstreamDrift`, `AffineDrift`), asynchronous jobs,
pipelines, and solver workflows historically used disparate state names and unvalidated
lifecycle booleans (`done`, `ok`, `success`, `cancelled`). In addition, cancellation races
and implicit defaults led to inconsistent terminal states and silent masking of errors.

Dieter's owner decision on `#5565` (#6760508859, aligning with Tools #6003 / #6760508857)
established that each repository maintains its own standard-library-only lifecycle kernel
following a single shared convention. Cross-repo submodule coupling is avoided until Tools
publishes tagged releases.

## Decision

AffineDrift adopts the canonical per-repo lifecycle and result contract implemented in
`src/core/lifecycle.py`.

### Part A: Lifecycle Convention

1. **Canonical Vocabulary**: The canonical lifecycle words are `QUEUED`, `RUNNING`,
   `CANCEL_REQUESTED`, `SUCCEEDED`, `FAILED`, and `CANCELLED`.
2. **Transition Table and Function**: State transitions are validated by `transition()`
   against `CANONICAL_LIFECYCLE_TRANSITIONS`. Terminal states (`SUCCEEDED`, `FAILED`,
   `CANCELLED`) cannot be exited. `QUEUED` cannot transition directly to `SUCCEEDED`.
3. **Cancellation Race Resolution**: When cancellation is requested while work completes,
   `CANCEL_REQUESTED -> SUCCEEDED` is valid and preserves the finished outcome; if aborted,
   `CANCEL_REQUESTED -> CANCELLED` is taken.
4. **Typed Snapshot**: `LifecycleSnapshot` provides an immutable, validated point-in-time
   record. Derived booleans (`done`, `ok`, `success`, `cancelled`) are strictly computed
   properties from `status` and can never be passed to the constructor or stored as mutable flags.
5. **Structured Failures**: `FAILED` states require a non-empty `LifecycleFailure` record;
   `SUCCEEDED` states forbid any failure record.

### Part B: Result Convention

1. **No Status Default**: Snapshots and result structures require explicit status initialization.
2. **Derived Booleans**: `ok`, `success`, and `done` must always be derived from canonical status.
3. **Solver Convergence and Feasibility**: Numerical operations require explicit validation of
   both convergence and physical feasibility.
4. **Finite Outputs**: Non-finite numbers (`NaN`, `Inf`) map to failure rather than silent defaults.

### Reversibility and Scoping

The kernel is self-contained in `src/core/lifecycle.py` with zero third-party dependencies.
No cross-repo submodule coupling is introduced.

## Consequences

- Consistent lifecycle behavior across AffineDrift pipeline and worker stages.
- Elimination of state desynchronization between status enums and boolean flags.
- Safe handling of cancellation races with deterministic outcome retention.
