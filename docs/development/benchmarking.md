# Benchmarking

AffineDrift keeps performance benchmarks separate from the default unit-test
suite. This makes benchmark infrastructure available for regression evidence
without making normal CI slower or noisy.

## Install

The root `requirements.txt` includes `pytest-benchmark`. Use the same Python
environment as the test suite:

```powershell
python -m pip install -r requirements.txt
```

## Smoke Check

Use this command when changing benchmark files or benchmarked helper APIs:

```powershell
python -m pytest benchmarks --benchmark-disable -q
```

It verifies imports, benchmark fixtures, and post-run assertions without
recording timing data.

## Local Timing Run

Run timing benchmarks only when local dependency installation makes it cheap:

```powershell
python -m pytest benchmarks --benchmark-only --benchmark-autosave
```

The first benchmark slice covers stable, lightweight computational paths:

- `double_pendulum_drift`
- `double_pendulum_mass_matrix`
- `trajectory_tracking_cost`

Generated pytest-benchmark JSON output is local evidence by default. Commit a
baseline only when the PR explicitly updates the baseline contract and explains
the machine/runtime context used to produce it.

## CI Policy

Benchmarks are opt-in. The default pytest configuration still points at
`tests/`, so benchmark timing does not run during routine unit tests. A future
CI job can add advisory benchmark comparison once the repository has an agreed
baseline and runner variability policy.
