# Performance Benchmarking Guide

This document describes how to run, interpret, and maintain performance benchmarks for AffineDrift.

## Quick Start

Run all benchmarks locally:

```bash
pytest benchmarks/ --benchmark-only
```

Compare against the baseline:

```bash
pytest benchmarks/ --benchmark-only --benchmark-compare=initial
```

## Benchmark Organization

Benchmarks are organized by performance domain:

### 1. RLFunnel Benchmarks (`test_benchmark_rl_funnel.py`)

Measures the performance of double-pendulum control algorithms:
- **drift_step**: Passive dynamics computation (critical hot path)
- **setpoint_lqr_controller**: Setpoint control law evaluation
- **trajectory_tracking_lqr**: Trajectory-tracking LQR computation
- **reference_trajectory_generation**: Reference path generation
- **full_simulation_loop**: End-to-end control loop
- **rl_funnel_solver_convergence**: Trajectory-tracking controller construction

**Typical performance**: 10-100 microseconds per step

### 2. Trajectory Cost Benchmarks (`test_benchmark_trajectory_cost.py`)

Measures trajectory cost computation performance:
- **setpoint_cost_small/medium**: Cost for setpoint-only objectives
- **trajectory_tracking_cost_small/medium/large**: Trajectory tracking cost at various scales
- **trajectory_tracking_with_deviation**: Cost when trajectory deviates from reference
- **setpoint_vs_tracking_gap**: Full cost gap analysis
- **cost_computation_scaling**: Scaling with trajectory length (4D state, 100 steps)

**Typical performance**: 25-200 microseconds per computation

### 3. Optimizer Benchmarks (`test_benchmark_optimizer.py`)

Measures swing optimization pipeline performance:
- **optimizer_instantiation**: SwingOptimizer setup and initialization
- **instantaneous_cost_computation**: Single step cost c(x, u)
- **terminal_cost_computation**: Terminal cost c_f(x_T)
- **trajectory_cost_short_horizon**: Full trajectory cost (10 steps)
- **trajectory_cost_long_horizon**: Full trajectory cost (100 steps)
- **high_dimensional_optimizer**: 6-joint system performance
- **cost_matrix_construction**: Q, R, Q_f matrix building
- **full_trajectory_cost_realistic_problem**: 3-joint, 50-step problem

**Typical performance**: 1-200 microseconds per computation

### 4. Simulation Benchmarks (`test_benchmark_simulation.py`)

Measures physics simulation engine performance:
- **ball_flight_dynamics_step**: Single aerodynamic dynamics step
- **ball_flight_state_creation**: BallFlightState instantiation
- **ball_flight_linearization**: Jacobian computation (A, B matrices)
- **trajectory_simulation_10/100/1000_steps**: Multi-step integration
- **ddp_mock_initialization**: DDP solver setup
- **complete_ball_flight_simulation**: Full realistic flight (up to 7 seconds)

**Typical performance**: 4 microseconds to 2 milliseconds depending on complexity

### 5. API and Module Loading Benchmarks (`test_benchmark_api.py`)

Measures module import times and API response time proxies:
- **core_module_import**: Core module loading time
- **contracts_module_import**: Contracts framework import
- **swing_optimizer_import**: Optimizer module import
- **ball_flight_import**: Simulation module import
- **numpy_serialization_small/large**: Binary serialization performance
- **numpy_deserialization_small/large**: Binary deserialization
- **json_serialization_trajectory_metadata**: JSON encoding
- **trajectory_length_query**: Trajectory statistics computation
- **full_module_startup**: Complete startup time
- **result_preparation_query_response**: API response formatting

**Typical performance**: 10 microseconds to 500 milliseconds depending on operation

## Running Benchmarks

### Run all benchmarks

```bash
pytest benchmarks/ --benchmark-only
```

### Run benchmarks with detailed output

```bash
pytest benchmarks/ --benchmark-only -v
```

### Run specific benchmark group

```bash
# Only trajectory cost benchmarks
pytest benchmarks/test_benchmark_trajectory_cost.py --benchmark-only

# Only optimizer benchmarks
pytest benchmarks/test_benchmark_optimizer.py --benchmark-only
```

### Run single benchmark

```bash
pytest benchmarks/test_benchmark_optimizer.py::TestOptimizerBenchmarks::test_benchmark_instantaneous_cost_computation --benchmark-only -v
```

### Save baseline for comparison

```bash
pytest benchmarks/ --benchmark-only --benchmark-save=my_baseline
```

### Compare against baseline

```bash
pytest benchmarks/ --benchmark-only --benchmark-compare=my_baseline
```

### Show only regressions

```bash
pytest benchmarks/ --benchmark-only --benchmark-compare=initial --benchmark-compare-fail=mean:15%
```

## Interpreting Results

A typical benchmark output looks like:

```
Name                                    Min       Max      Mean    StdDev  Median     IQR  Outliers  OPS        Rounds
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
test_benchmark_instantaneous_cost      8.5us  45.2us    16.3us    8.1us   12.1us  4.5us    15;42   61,349      8500
```

Key columns:

- **Min/Max**: Range of measured times
- **Mean**: Average execution time (main metric)
- **StdDev**: Standard deviation (variance indicator)
- **Median**: 50th percentile (robust central tendency)
- **IQR**: Interquartile range (quartile 3 - quartile 1)
- **Outliers**: Count of outliers beyond 1 std dev
- **OPS**: Operations per second
- **Rounds**: Number of measurement rounds

## Performance Thresholds

The CI pipeline uses these thresholds:

| Regression | Action | Details |
|-----------|--------|---------|
| < 5% | ✅ Pass | No action needed |
| 5-15% | ⚠️ Warn | Flagged in PR comments, does not fail CI |
| > 15% | ❌ Fail | Blocks merge, requires investigation |

These thresholds balance:
- **Sensitivity**: Catching real performance regressions
- **Stability**: Avoiding false positives from system variance
- **Practicality**: Allowing small optimizations without breaking CI

## Investigating Regressions

If a benchmark regresses:

1. **Confirm it's real** (not measurement noise):
   ```bash
   # Run multiple times
   for i in {1..5}; do
     pytest benchmarks/test_benchmark_optimizer.py::TestOptimizerBenchmarks::test_benchmark_instantaneous_cost_computation --benchmark-only
   done
   ```

2. **Check git history**:
   ```bash
   git log --oneline --all -- <benchmark_file>
   ```

3. **Profile the code**:
   ```bash
   python -m cProfile -s cumtime -m pytest benchmarks/test_benchmark_optimizer.py --benchmark-only
   ```

4. **Check system state**:
   - CPU governor (frequency scaling)
   - Background processes
   - Available memory
   - Thermal throttling

5. **Run baseline again**:
   ```bash
   pytest benchmarks/ --benchmark-only --benchmark-save=baseline_check
   pytest benchmarks/ --benchmark-only --benchmark-compare=baseline_check
   ```

## Best Practices

### Writing Benchmarks

1. **Keep benchmarks focused**: One operation per benchmark
2. **Use realistic inputs**: Match production problem sizes
3. **Measure what matters**: Focus on hot paths, not setup
4. **Document the "why"**: Explain why this metric matters
5. **Set proper scales**: Use appropriate units (µs, ms, s)

Example:

```python
def test_benchmark_critical_computation(benchmark):
    """Benchmark the hot-path computation in solver.
    
    This is called 100+ times per optimization, so 10% regression
    = 10x slower solver overall.
    """
    data = generate_realistic_input()
    
    def compute():
        return critical_function(data)
    
    result = benchmark(compute)
    assert result is not None
```

### Avoiding False Positives

1. **Disable garbage collection** during benchmarks (pytest-benchmark does this by default)
2. **Use warm-up iterations** (pytest-benchmark auto-warms)
3. **Run in quiet environment**: Minimize background processes
4. **Use statistical thresholds**: 5% accounts for measurement noise
5. **Don't benchmark import time** (varies by caching)

### Maintaining Benchmarks

1. **Update baselines** when intentional optimization occurs:
   ```bash
   pytest benchmarks/ --benchmark-only --benchmark-save=initial
   git add .benchmarks/
   git commit -m "perf: update benchmark baseline after optimization"
   ```

2. **Review regressions**: Never merge with unexplained regressions
3. **Track trends**: Watch for slow degradation over time
4. **Document changes**: Explain any intentional performance trade-offs

## Baseline Storage

Baseline results are stored in `.benchmarks/` in JSON format, organized by platform:

```
.benchmarks/
├── Windows-CPython-3.12-64bit/
│   ├── 0001_initial.json      # Initial baseline
│   ├── 0002_initial.json      # Updated baseline v1
│   └── 0003_initial.json      # Updated baseline v2
└── Linux-CPython-3.12-64bit/
    └── ...
```

Each JSON file contains:
- Benchmark names and descriptions
- All measured times (min, max, mean, std dev)
- Number of iterations
- Machine/Python version info
- Timestamp

## CI Integration

The benchmarking CI workflow:

1. **Runs on**: Push to `main`/`staging`, all PRs
2. **Compares against**: Initial baseline (`.benchmarks/*/0001_initial.json`)
3. **Thresholds**:
   - Warns: > 5% regression
   - Fails: > 15% regression
4. **Output**: Comments on PRs with summary + detailed results artifact

## Performance Optimization Workflow

When optimizing:

1. Create a feature branch
2. Run baseline before changes:
   ```bash
   pytest benchmarks/ --benchmark-only --benchmark-save=before
   ```
3. Make optimizations
4. Run benchmarks after changes:
   ```bash
   pytest benchmarks/ --benchmark-only --benchmark-compare=before
   ```
5. Verify improvement meets goals
6. Update baseline only if optimization is intentional:
   ```bash
   pytest benchmarks/ --benchmark-only --benchmark-save=initial
   git add .benchmarks/
   ```
7. Open PR with benchmark improvements documented

## References

- [pytest-benchmark docs](https://pytest-benchmark.readthedocs.io/)
- [Statistical analysis of benchmarks](https://en.wikipedia.org/wiki/Benchmarking_(computing))
- Performance analysis: `docs/operations/observability.md`

## Contributing

When adding new benchmarks:

1. Place in appropriate `test_benchmark_*.py` file
2. Use `@pytest.mark.benchmark(group="name")` marker
3. Include docstring explaining the operation
4. Document typical performance range
5. Verify baseline is created: `pytest benchmarks/test_benchmark_myfile.py --benchmark-only --benchmark-save=initial`
6. Add entry to this guide
