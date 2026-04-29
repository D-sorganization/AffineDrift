# AffineDrift Performance Benchmarks

This directory contains `pytest-benchmark` based performance benchmarks for the
AffineDrift critical paths.  They measure real computation — no trivial toy operations —
so results give a meaningful baseline for regression detection.

## Covered hot paths

| # | Test | Module |
|---|------|--------|
| 1 | iLQR rollout – 50-step Euler forward pass | `src/core/optimizers/ilqr_solver.py` |
| 2 | iLQR finite-difference Jacobian linearisation | `src/core/optimizers/ilqr_solver.py` |
| 3 | iLQR backward pass – 10-step horizon | `src/core/optimizers/ilqr_solver.py` |
| 4 | iLQR quadratic trajectory cost | `src/core/optimizers/ilqr_solver.py` |
| 5 | Swing optimiser – instantaneous cost | `src/affine_control/swing_optimizer.py` |
| 6 | Swing optimiser – trajectory cost (20 steps) | `src/affine_control/swing_optimizer.py` |
| 7 | Ball flight – single RK4 integration step | `src/golf_simulation/ball_flight.py` |
| 8 | Ball flight – full driver trajectory simulation | `src/golf_simulation/ball_flight.py` |
| 9 | Ball flight – finite-difference Jacobians (9-D) | `src/golf_simulation/ball_flight.py` |
| 10 | Putting – flat green 10-ft roll-out | `src/golf_simulation/putting.py` |
| 11 | Putting – batch elevation queries (200 pts) | `src/golf_simulation/putting.py` |
| 12 | Residuals – Hessian norm (2-state pendulum) | `src/affine_control/residuals.py` |
| 13 | Residuals – `predict_residual_bound` (100 steps) | `src/affine_control/residuals.py` |
| 14 | DDP – perturbation-size estimation | `src/affine_control/ddp.py` |
| 15 | DDP – adaptive timestep selection (10 steps) | `src/affine_control/ddp.py` |

## Requirements

`pytest-benchmark` must be installed (listed under dev/test dependencies):

```bash
pip install pytest-benchmark>=4.0
```

Or install via the project's requirements file:

```bash
pip install -r requirements.txt
```

## Running the benchmarks

**Run all benchmarks (skip regular tests):**
```bash
pytest benchmarks/ --benchmark-only
```

**Run benchmarks alongside regular tests:**
```bash
pytest benchmarks/
```

**Run a single benchmark:**
```bash
pytest benchmarks/test_core_performance.py::TestCorePerformance::test_ball_flight_driver_trajectory --benchmark-only
```

**Save results to a JSON file for later comparison:**
```bash
pytest benchmarks/ --benchmark-only --benchmark-save=baseline
```

**Compare against a saved baseline:**
```bash
pytest benchmarks/ --benchmark-only --benchmark-compare=baseline
```

**Compare with a tolerance threshold (fail if >10% slower):**
```bash
pytest benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%
```

**Increase statistical confidence (more rounds):**
```bash
pytest benchmarks/ --benchmark-only --benchmark-min-rounds=10
```

**Disable garbage collection during measurements:**
```bash
pytest benchmarks/ --benchmark-only --benchmark-disable-gc
```

## Interpreting results

`pytest-benchmark` reports:

| Column | Meaning |
|--------|---------|
| `Min` | Fastest observed run |
| `Max` | Slowest observed run |
| `Mean` | Average run time |
| `StdDev` | Standard deviation across rounds |
| `Median` | Median run time (most stable signal) |
| `IQR` | Interquartile range (spread without outliers) |
| `Rounds` | Number of timing rounds |
| `Iterations` | Calls per round |

Use **Median** as the primary signal for regression detection.  The `Mean`
can be skewed by warm-up effects or OS scheduling noise.

## CI integration

To fail CI on performance regressions, add a step after running tests:

```yaml
- name: Benchmark (compare against saved baseline)
  run: |
    pytest benchmarks/ --benchmark-only \
      --benchmark-compare=.benchmarks/baseline \
      --benchmark-compare-fail=mean:15%
```

Store the `.benchmarks/` directory as a CI artifact or commit it alongside
the code for reproducible comparisons.
