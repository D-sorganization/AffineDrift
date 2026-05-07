# Testing Guide

AffineDrift maintains a comprehensive test suite covering Python source code,
JavaScript modules, Quarto content integrity, and CI quality gates. This guide
explains test patterns, conventions, and how to write tests that fit the existing
architecture.

## Test Layout

```
tests/
  conftest.py                  # Shared fixtures and configuration
  README.md                    # Test index and patterns
  test_*.py                    # Python test modules
  *.test.js                    # Jest JavaScript test modules
  test_affine_control/         # Physics module tests
  tools/                       # Tool-specific tests
benchmarks/
  test_benchmark_*.py          # Performance benchmarks (opt-in)
```

The default `pytest` configuration targets `tests/` only. Benchmarks are
opt-in and live in `benchmarks/`.

## Python Tests

### Naming Conventions

- **Files**: `test_<module>.py` or `test_<feature>.py`
- **Classes**: `Test<Feature>` (PascalCase)
- **Functions**: `test_<behavior>_<condition>` (snake_case)

```python
# Good
def test_swing_optimizer_returns_valid_trajectory():
    ...

def test_ilqr_solver_converges_within_iteration_budget():
    ...

# Bad
def test_it():
    ...

def test_solver():
    ...
```

### Standard Imports

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
```

Do **not** use wildcard imports (`from module import *`).

### Fixtures (conftest.py)

Shared fixtures live in `tests/conftest.py`. Use fixtures for:

- Temporary directories (`tmp_path` from pytest)
- Repository root paths
- Shared test data

```python
# Access the repo root
@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).parent.parent
```

### Type Hints

All test functions must have type annotations (mypy strict mode is enforced):

```python
def test_ball_flight_reaches_expected_distance(
    tmp_path: Path,
) -> None:
    ...
```

### Assertion Style

Prefer plain `assert` statements. Use `pytest.raises` for expected exceptions:

```python
def test_invalid_theta_raises_value_error() -> None:
    with pytest.raises(ValueError, match="theta must be"):
        validate_theta(-999.0)
```

Avoid bare `except:` blocks. Catch specific exception types.

### Contract-Based Tests

AffineDrift uses Design By Contract (DBC) patterns. Tests in
`test_dbc_application_contracts.py` and `test_architecture_dbc.py` verify
precondition/postcondition invariants. When adding a public function with
contracts, add a companion DBC test:

```python
class TestSwingOptimizerContracts:
    """Verify precondition/postcondition contracts for SwingOptimizer."""

    def test_precondition_rejects_empty_trajectory(self) -> None:
        with pytest.raises(ValueError):
            SwingOptimizer(trajectory=[])

    def test_postcondition_result_is_finite(self) -> None:
        result = SwingOptimizer(trajectory=VALID_TRAJECTORY).optimize()
        assert all(math.isfinite(v) for v in result)
```

### Property-Based Tests

Hypothesis is available for property-based testing. Use it for numerical
functions where the input space is large:

```python
from hypothesis import given, settings
from hypothesis import strategies as st

@given(theta=st.floats(min_value=0.0, max_value=math.pi))
@settings(max_examples=200)
def test_residual_norm_is_non_negative(theta: float) -> None:
    assert compute_residual(theta) >= 0.0
```

See `tests/test_affine_control/test_property_based.py` for examples.

### Physics / Regression Tests

For physics accuracy, lock expected values in regression tests and mark them
explicitly:

```python
# Regression for issue #2345: ball flight distance off by 15%
def test_ball_flight_distance_regression() -> None:
    result = simulate_ball_flight(club="driver", swing_speed=110)
    assert abs(result.distance - 285.0) < 5.0, (
        f"Ball flight regression: expected ~285 yards, got {result.distance:.1f}"
    )
```

## JavaScript Tests (Jest)

### Location

JavaScript tests use Jest and live alongside source files or in `tests/*.test.js`.

### Running Tests

```bash
npm test                        # All Jest tests
npm test -- --watch            # Watch mode
npm test -- --coverage         # Coverage report
npm test -- <pattern>          # Specific test file
```

### Writing Tests

```javascript
// tests/bibliography.test.js
import { parseBibliography } from '../js/bibliography.js';

describe('parseBibliography', () => {
  it('returns empty array for empty input', () => {
    expect(parseBibliography('')).toEqual([]);
  });

  it('parses a valid BibTeX entry', () => {
    const result = parseBibliography(VALID_BIBTEX);
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe('Smith2020');
  });
});
```

### DOM Testing

Use `@testing-library/jest-dom` matchers for DOM assertions:

```javascript
expect(document.querySelector('.nav-link')).toBeInTheDocument();
expect(button).toBeEnabled();
```

## Benchmark Tests

Benchmarks are **opt-in** and live in `benchmarks/`. They use `pytest-benchmark`.

### Smoke Check (no timing)

Run this during development to verify imports and fixture correctness:

```powershell
python -m pytest benchmarks --benchmark-disable -q
```

### Timing Run

Run locally only (not in default CI):

```powershell
python -m pytest benchmarks --benchmark-only --benchmark-autosave
```

See `docs/development/benchmarking.md` for the full benchmark policy.

## CI Integration

The `quality-gate` job in `.github/workflows/ci-standard.yml` runs:

1. Merge conflict marker check
2. Python lint (`ruff check`, `ruff format --check`)
3. Type check (`mypy`)
4. Unit tests (`pytest tests/`)
5. JavaScript tests (`npm test`)
6. Quarto syntax check

Tests must pass on the **d-sorg-fleet** runner. Do not rely on GitHub-hosted
runners — they are blocked by governance policy.

## Common Patterns

### Testing File Content

```python
def test_readme_contains_required_section(repo_root: Path) -> None:
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "## Local Development" in readme
```

### Testing CLI Scripts

```python
import subprocess

def test_link_checker_exits_zero_on_clean_repo(repo_root: Path) -> None:
    result = subprocess.run(
        ["python", "scripts/link-checker.py", "--internal-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
```

### Mocking External I/O

```python
from unittest.mock import patch

def test_publish_article_calls_gh_cli() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        publish_article("draft.qmd")
        mock_run.assert_called_once()
```

### Skipping Platform-Specific Tests

```python
import sys

@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test")
def test_docker_build_succeeds() -> None:
    ...
```

## Coverage Policy

- CI enforces a minimum coverage floor (see `pyproject.toml` or `setup.cfg`).
- Run coverage locally: `python -m pytest --cov=src --cov-report=term-missing`
- Focus coverage on `src/` — not `scripts/` or `tests/` themselves.
- Aim for ≥90% coverage on new modules.

## Adding Tests for New Code

When adding a new module or function:

1. Create `tests/test_<module>.py` (or add to the appropriate existing file).
2. Write at least one happy-path test and one error-path test.
3. Add DBC tests if the function has contracts.
4. Run `python -m pytest tests/ -q` locally before pushing.
5. Verify `mypy` passes: `python -m mypy src/`.
6. Run `ruff check .` and `ruff format .` for lint compliance.

## References

- [pytest docs](https://docs.pytest.org/)
- [Hypothesis docs](https://hypothesis.readthedocs.io/)
- [Jest docs](https://jestjs.io/)
- `docs/development/benchmarking.md` — benchmark policy
- `tests/README.md` — test index
- `CONTRIBUTING.md` — full contribution workflow
