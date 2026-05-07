# Performance Tuning Guide

AffineDrift's Python source includes numerically intensive physics simulation
code (iLQR, DDP, golf ball flight, wrist joint models). This guide documents
profiling tools, optimization patterns, and performance policies.

## Profiling Tools

### cProfile (Built-in)

Use cProfile for function-level profiling during development:

```python
import cProfile
import pstats
from pstats import SortKey

with cProfile.Profile() as pr:
    result = solver.solve()

stats = pstats.Stats(pr)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # Top 20 functions by cumulative time
```

Or from the command line:

```powershell
python -m cProfile -s cumtime src/affine_control/swing_optimizer.py
```

### line_profiler

For line-by-line analysis of a hot function:

```powershell
pip install line-profiler
kernprof -l -v src/core/optimizers/ilqr_solver.py
```

Annotate the target function with `@profile` (removed before committing):

```python
@profile  # added temporarily for line_profiler; remove before commit
def _backward_pass(self) -> None:
    ...
```

### memory_profiler

For memory usage analysis:

```powershell
pip install memory-profiler
python -m memory_profiler src/golf_simulation/round_simulator.py
```

### pytest-benchmark

For repeatable micro-benchmarks:

```powershell
# Smoke check (no timing)
python -m pytest benchmarks --benchmark-disable -q

# Timing run
python -m pytest benchmarks --benchmark-only --benchmark-autosave
```

See `docs/development/benchmarking.md` for the full benchmark policy.

## NumPy Performance Patterns

Most of AffineDrift's performance-sensitive code uses NumPy. Key patterns:

### Vectorize Instead of Looping

```python
import numpy as np

# Slow — Python loop over array
def compute_residuals_slow(states: list[float]) -> list[float]:
    return [state ** 2 - 1.0 for state in states]

# Fast — vectorized NumPy
def compute_residuals_fast(states: np.ndarray) -> np.ndarray:
    return states ** 2 - 1.0
```

### Avoid Repeated Memory Allocation

Pre-allocate arrays outside inner loops:

```python
# Slow — allocates a new array every iteration
for i in range(n_steps):
    grad = np.zeros(n_states)
    grad = compute_gradient(state[i])

# Fast — allocate once, overwrite in-place
grad = np.zeros(n_states)
for i in range(n_steps):
    compute_gradient_into(state[i], out=grad)
```

### Use In-Place Operations

```python
# Slower — creates temporary arrays
x = x + alpha * dx

# Faster — in-place modification
x += alpha * dx
np.multiply(alpha, dx, out=dx)
np.add(x, dx, out=x)
```

### Matrix Multiplication

Use `@` operator (or `np.matmul`) instead of `np.dot` for 2-D matrices:

```python
# Modern — uses BLAS automatically
result = A @ B

# Older — same, but less readable
result = np.matmul(A, B)
```

Avoid `np.matrix` — it's deprecated. Use `np.ndarray` exclusively.

### Caching Expensive Computations

Use `functools.lru_cache` for deterministic functions with repeated calls:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_inertia_matrix(joint_config: tuple[float, ...]) -> np.ndarray:
    # Expensive: computes full inertia matrix
    return compute_inertia(joint_config)
```

Note: `lru_cache` requires hashable arguments — convert arrays to tuples.

## Algorithm-Level Optimization

### iLQR Solver

The iLQR solver's performance is dominated by the backward and forward passes.
Key optimization opportunities:

- **Line search**: use Armijo backtracking to find the optimal step size
  without running the full forward pass multiple times.
- **Regularization**: adaptive Levenberg-Marquardt regularization avoids
  unnecessary iterations.
- **Early termination**: check convergence after each iteration and exit when
  the cost improvement is below tolerance.

```python
# Convergence check pattern (already in iLQR implementation)
if abs(delta_cost) / (abs(cost) + 1e-9) < self.tol:
    logger.info("iLQR converged in %d iterations", iteration)
    break
```

### DDP (Differential Dynamic Programming)

- Use analytical Jacobians where possible (avoid numerical finite differences
  for Jacobians of smooth functions).
- Parallelize trajectory rollouts if running multiple trials (see
  `src/affine_control/ddp.py`).

### Golf Ball Flight

The ball flight integrator (`src/golf_simulation/ball_flight.py`) uses RK45.
For performance:

- Use `scipy.integrate.solve_ivp` with `method='RK45'` and appropriate
  `rtol`/`atol` tolerances.
- Avoid storing full trajectory when only the endpoint is needed:
  set `dense_output=False`.

```python
from scipy.integrate import solve_ivp

sol = solve_ivp(
    ball_flight_ode,
    t_span=(0.0, t_max),
    y0=initial_conditions,
    method="RK45",
    rtol=1e-6,
    atol=1e-8,
    dense_output=False,  # faster when trajectory not needed
)
```

## JavaScript Performance

### DOM Access

Minimize DOM queries. Cache references:

```javascript
// Slow — repeated DOM query
function updateNav() {
  document.querySelector('.nav').style.display = 'block';
  document.querySelector('.nav').classList.add('active');
}

// Fast — cache the reference
function updateNav() {
  const nav = document.querySelector('.nav');
  nav.style.display = 'block';
  nav.classList.add('active');
}
```

### Debounce Expensive Event Handlers

```javascript
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

window.addEventListener('resize', debounce(recalculateLayout, 150));
```

### Lazy Loading

Use `loading="lazy"` on images and `import()` for code splitting:

```javascript
// Lazy-load heavy modules
const { renderMath } = await import('./mathjax-loader.js');
```

## Performance Budgets

The benchmark suite (`benchmarks/`) maintains timing baselines for:

| Benchmark | Target | Regression threshold |
|-----------|--------|---------------------|
| `double_pendulum_drift` | < 5ms | +20% |
| `double_pendulum_mass_matrix` | < 10ms | +20% |
| `trajectory_tracking_cost` | < 2ms | +20% |
| `rl_funnel_simulation` | < 100ms | +30% |

A benchmark regression at +20% triggers a CI warning. At +50% it is flagged
for review.

## CI Performance Monitoring

The `quality-gate` job has a 45-minute timeout. If CI is slow:

1. Check if new tests are hitting slow I/O paths (network, disk).
2. Profile the slowest test with `--durations=10`:
   ```powershell
   python -m pytest tests/ --durations=10
   ```
3. Mock slow external dependencies in unit tests.
4. Move genuinely slow integration tests to a separate CI job.

## Adding Performance Tests

When adding a performance-sensitive function, add a benchmark in `benchmarks/`:

```python
# benchmarks/test_benchmark_new_feature.py
import pytest
from src.new_module import expensive_function

def test_expensive_function(benchmark):
    result = benchmark(expensive_function, input_data)
    assert result is not None
```

Run the smoke check to verify the benchmark fixture is correct:

```powershell
python -m pytest benchmarks --benchmark-disable -q
```

## References

- `docs/development/benchmarking.md` — benchmark policy and baseline management
- `benchmarks/` — benchmark test suite
- `src/core/optimizers/ilqr_solver.py` — iLQR implementation
- [NumPy performance tips](https://numpy.org/doc/stable/user/basics.subclassing.html)
- [SciPy integrate.solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)
