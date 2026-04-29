# Benchmarks

This directory contains opt-in pytest-benchmark benchmarks for stable,
performance-critical code paths. The normal pytest configuration still targets
`tests/`, so these benchmarks do not run as part of the default unit-test suite.

## Overview

The benchmarking suite covers:

- **Core dynamics**: Double pendulum drift and mass matrix computations
- **Trajectory optimization**: Trajectory cost calculation at various scales
- **Affine control**: Hessian norm and bound computations for control systems
- **Batch operations**: Performance across multiple evaluations

All benchmarks use `pytest-benchmark` for consistent measurement and comparison.

## Running Benchmarks

### Smoke Test (No Timing Collection)

Verify benchmarks run correctly without collecting timing data:

```bash
python -m pytest benchmarks --benchmark-disable -q
```

### Run Full Benchmark Suite

Execute benchmarks and save results:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-autosave
```

Results are saved to `.benchmarks/` directory in JSON format.

### Compare Against Baseline

Compare latest results against the previous run:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-compare
```

To compare against a specific saved result:

```bash
python -m pytest benchmarks --benchmark-compare=.benchmarks/0001_*.json
```

### Run Specific Benchmark

Run a single benchmark test:

```bash
python -m pytest benchmarks/test_core_benchmarks.py::test_double_pendulum_drift_baseline -v
```

### Run All Benchmarks with Verbose Output

```bash
python -m pytest benchmarks -v --benchmark-only --benchmark-autosave
```

## Benchmark Files

- **`test_core_benchmarks.py`** — Core dynamics and trajectory generation
  - `test_double_pendulum_drift_baseline` — Single drift evaluation
  - `test_double_pendulum_mass_matrix_baseline` — Mass matrix computation
  - `test_trajectory_tracking_cost_baseline` — Baseline trajectory cost
  - `test_reference_trajectory_generation_short` — Short trajectory (100ms)
  - `test_reference_trajectory_generation_medium` — Medium trajectory (1s)
  - `test_drift_dynamics_batch` — Batch drift evaluation (100 states)

- **`test_affine_control_benchmarks.py`** — Control system computations
  - `test_hessian_norm_computation` — Hessian norm for linear systems
  - `test_hessian_bound_computation` — Hessian bound computation
  - `test_nonlinear_hessian_bound` — Hessian bound for nonlinear systems

- **`test_trajectory_optimization_benchmarks.py`** — Trajectory optimization
  - `test_trajectory_cost_small_scale` — Small trajectories (32 points)
  - `test_trajectory_cost_medium_scale` — Medium trajectories (256 points)
  - `test_trajectory_cost_large_scale` — Large trajectories (1024 points)
  - `test_trajectory_cost_multivariate` — Multivariate trajectories (4D)
  - `test_trajectory_cost_worst_case` — Large perturbations

## Baseline Results

Baseline results are stored in `.benchmarks/` as JSON files. Generated results
are machine-local evidence unless explicitly promoted in a PR.

To establish a new baseline:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-autosave
git add .benchmarks/
git commit -m "perf: update benchmark baseline"
```

## CI Integration

Benchmarks are **not** run in the default CI pipeline. They can be run manually
in CI with a special workflow trigger or as part of performance validation.

To run benchmarks in a CI environment:

```bash
python -m pytest benchmarks --benchmark-only --benchmark-json=benchmarks/results.json
```

Results are saved to `benchmarks/results.json` for external analysis or regression
detection.

## Adding New Benchmarks

When adding a new benchmark:

1. Create a test function in the appropriate file
2. Mark it with `@pytest.mark.benchmark`
3. Use the `benchmark` fixture as a callable argument
4. Validate the result for correctness and finite values
5. Include a descriptive docstring with scale/scope information

Example:

```python
@pytest.mark.benchmark
def test_new_computation(benchmark: Callable[..., Any]) -> None:
    """Benchmark description with scale/scope information."""
    # Setup
    data = prepare_test_data()

    # Run benchmark
    result = benchmark(computation_function, data)

    # Validate correctness
    assert result_is_correct(result)
    assert np.all(np.isfinite(result))
```

## Interpreting Results

Benchmark output shows:

- **min/max** — Minimum and maximum execution time across iterations
- **mean ± std** — Average execution time and standard deviation
- **rounds** — Number of times the benchmark was executed
- **iterations** — Number of iterations per round

Lower values are better. Look for unexpected regressions when comparing runs.
