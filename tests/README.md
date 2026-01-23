# Tests Directory

This directory contains all test suites for the AffineDrift project.

## Directory Structure

```
tests/
├── conftest.py                      # Pytest configuration and fixtures
├── test_deployment_integrity.py     # Deployment validation tests
├── test_latex_to_qmd.py            # LaTeX converter tests
├── test_update_navigation.py        # Navigation updater tests
├── test_wrist_simulator.py         # Wrist simulation tests
├── verification/                    # Verification scripts and data
└── __pycache__/                    # Python bytecode cache
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_deployment_integrity.py
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test Function

```bash
pytest tests/test_latex_to_qmd.py::test_convert_equation
```

## Test Categories

### Unit Tests

Test individual functions and modules in isolation.

**Files:**
- `test_latex_to_qmd.py` - LaTeX to QMD conversion
- `test_update_navigation.py` - Navigation menu generation

**Example:**
```python
def test_convert_simple_equation():
    """Test conversion of simple LaTeX equation."""
    latex = r"\frac{a}{b}"
    result = convert_latex(latex)
    assert result == expected_output
```

### Integration Tests

Test interactions between multiple components.

**Files:**
- `test_deployment_integrity.py` - Full deployment pipeline

**Example:**
```python
def test_full_build_pipeline():
    """Test complete build from source to deployment."""
    build_site()
    assert_valid_html()
    assert_valid_links()
```

### Verification Tests

Located in `verification/` directory. These tests verify mathematical correctness and scientific accuracy.

## Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def sample_latex_file(tmp_path):
    """Create a temporary LaTeX file for testing."""
    file_path = tmp_path / "test.tex"
    file_path.write_text(r"\documentclass{article}...")
    return file_path

@pytest.fixture
def mock_quarto_config():
    """Provide a mock Quarto configuration."""
    return {
        "project": {"type": "website"},
        "website": {"navbar": {...}}
    }
```

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_function_name():
    """Test description."""
    # Arrange: Set up test data
    input_data = create_test_data()
    
    # Act: Execute the function
    result = function_under_test(input_data)
    
    # Assert: Verify the result
    assert result == expected_value
    assert result.property == expected_property
```

### Docstrings

All tests should have descriptive docstrings:

```python
def test_convert_complex_equation():
    """
    Test conversion of complex LaTeX equations with nested structures.
    
    Verifies that:
    - Nested fractions are handled correctly
    - Subscripts and superscripts are preserved
    - Special symbols are converted properly
    """
    # Test implementation
```

### Assertions

Use descriptive assertion messages:

```python
assert len(results) > 0, "Expected non-empty results list"
assert result.status == "success", f"Expected success, got {result.status}"
```

## Test Coverage

### Current Coverage

Run coverage report:
```bash
pytest --cov=. --cov-report=term-missing
```

### Coverage Goals

- **Target:** 60-80% code coverage
- **Critical paths:** 90%+ coverage
- **Utilities:** 70%+ coverage

### Viewing Coverage Reports

HTML coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Nightly builds

### CI Configuration

See `.github/workflows/` for CI pipeline configuration.

### Pre-commit Checks

Run tests before committing:
```bash
# Add to .git/hooks/pre-commit
pytest --exitfirst
```

## Mocking and Fixtures

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocked external service."""
    with patch('module.external_api') as mock_api:
        mock_api.return_value = {"status": "ok"}
        result = function_that_calls_api()
        assert result.success
```

### Temporary Files

Use `tmp_path` fixture for file operations:

```python
def test_file_processing(tmp_path):
    """Test file processing with temporary files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    result = process_file(test_file)
    assert result.success
```

## Debugging Tests

### Run with Debugger

```bash
pytest --pdb
```

### Print Debug Information

```python
def test_with_debug():
    """Test with debug output."""
    result = function_under_test()
    print(f"Debug: result = {result}")  # Visible with pytest -s
    assert result.valid
```

### Verbose Output

```bash
pytest -vv  # Extra verbose
pytest -s   # Show print statements
```

## Performance Testing

### Timing Tests

```python
import time

def test_performance():
    """Test that function completes within time limit."""
    start = time.time()
    result = expensive_function()
    duration = time.time() - start
    
    assert duration < 1.0, f"Function took {duration}s, expected < 1s"
```

### Profiling

```bash
pytest --profile
```

## Common Issues

### Import Errors

Ensure project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Fixture Not Found

Check that `conftest.py` is in the correct location and fixtures are properly defined.

### Flaky Tests

For tests that occasionally fail:
```python
import pytest

@pytest.mark.flaky(reruns=3)
def test_sometimes_fails():
    """Test that may fail intermittently."""
    # Test implementation
```

## Contributing

When adding new tests:

1. **Follow naming conventions**
2. **Add docstrings** to all test functions
3. **Use fixtures** for common setup
4. **Keep tests isolated** - no dependencies between tests
5. **Test edge cases** - not just happy paths
6. **Update this README** if adding new test categories

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [AGENTS.md](../AGENTS.md) - Coding standards
- [pytest documentation](https://docs.pytest.org/) - Official pytest docs
