# Benchmarks

This directory contains opt-in pytest-benchmark benchmarks for stable,
low-cost code paths. The normal pytest configuration still targets `tests/`,
so these benchmarks do not run as part of the default unit-test suite.

Run a smoke check without collecting timing statistics:

```powershell
python -m pytest benchmarks --benchmark-disable -q
```

Run the benchmark suite locally:

```powershell
python -m pytest benchmarks --benchmark-only --benchmark-autosave
```

Compare a later run against saved local results:

```powershell
python -m pytest benchmarks --benchmark-compare
```

Generated pytest-benchmark result files are machine-local evidence unless a PR
explicitly promotes a curated baseline.
