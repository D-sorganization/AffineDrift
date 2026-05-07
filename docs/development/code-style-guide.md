# Code Style Guide

AffineDrift enforces consistent code style across Python, JavaScript, CSS, and
Quarto content. This guide documents the conventions enforced by CI and followed
in all new code.

## Python Style

### Formatter and Linter

AffineDrift uses **ruff** for both formatting and linting, with **black** as
secondary formatter for consistency:

```powershell
# Lint (check only)
python -m ruff check .

# Auto-fix lint issues
python -m ruff check --fix .

# Format
python -m ruff format .

# Type check
python -m mypy .
```

All four must pass before a PR can merge.

### Line Length

Maximum line length is **100 characters** (configured in `pyproject.toml`).

### Import Order

Imports follow the `isort` order enforced by ruff:

```python
# 1. Standard library
import re
import sys
from pathlib import Path

# 2. Third-party libraries
import numpy as np
import pytest

# 3. Local imports
from src.core.constants import GRAVITY
from src.affine_control.swing_types import SwingState
```

No wildcard imports (`from module import *`).

### Type Hints

All public functions must have full type annotations:

```python
# Good
def compute_trajectory(
    initial_state: SwingState,
    horizon: int,
    dt: float = 0.01,
) -> list[SwingState]:
    ...

# Bad — missing return type and parameter types
def compute_trajectory(initial_state, horizon, dt=0.01):
    ...
```

Use `Optional[T]` or `T | None` (Python 3.10+ union syntax preferred).
Use `list[T]` and `dict[K, V]` (lowercase generics, Python 3.9+).

### Docstrings

Public functions and classes require docstrings (enforced by
`test_docstring_coverage.py`):

```python
def solve_ilqr(
    cost_fn: CostFunction,
    dynamics: DynamicsModel,
    max_iterations: int = 100,
) -> TrajectoryResult:
    """Solve the iLQR optimal control problem.

    Args:
        cost_fn: Quadratic cost function defining the optimization objective.
        dynamics: Discrete-time dynamics model (affine in control).
        max_iterations: Maximum iLQR iterations before returning best result.

    Returns:
        TrajectoryResult with optimal state/control sequence and convergence info.

    Raises:
        ValueError: If cost_fn and dynamics have incompatible state dimensions.
    """
    ...
```

Private helper functions (`_`) may have shorter docstrings or inline comments.

### Logging

Use the `logging` module. **Never** use `print()` for application output in
`src/`:

```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("Solver converged in %d iterations", n_iter)
logger.warning("Theta near boundary: %.4f", theta)
logger.error("DDP failed: %s", exc)

# Bad — violates CI print prohibition
print(f"Solver converged in {n_iter} iterations")
```

`print()` is allowed in `scripts/` and test helpers where capturing output is
the intent.

### Exception Handling

Catch specific exceptions — never bare `except:`:

```python
# Good
try:
    result = solver.solve()
except ValueError as e:
    logger.error("Invalid input: %s", e)
    raise
except np.linalg.LinAlgError as e:
    logger.warning("Singular matrix, using fallback: %s", e)
    result = fallback_solver.solve()

# Bad
try:
    result = solver.solve()
except:
    pass
```

### Constants

Module-level constants use UPPER_SNAKE_CASE and live in `src/core/constants.py`
or the relevant module:

```python
GRAVITY: float = 9.81       # m/s²
AIR_DENSITY: float = 1.225  # kg/m³ at sea level
```

### No Magic Numbers

Avoid inline magic numbers in logic code. Name them:

```python
# Good
MAX_SWING_ITERATIONS = 50
if iterations > MAX_SWING_ITERATIONS:
    raise RuntimeError("Solver did not converge")

# Bad
if iterations > 50:
    raise RuntimeError("Solver did not converge")
```

## JavaScript Style

### ES6+ Only

AffineDrift uses ES6+ syntax throughout. Use:

- `const` by default; `let` when reassignment is needed; never `var`
- Arrow functions: `const fn = (x) => x * 2`
- Template literals: `` `Hello, ${name}!` ``
- `async/await` over `.then()` chains
- Strict equality: `===` and `!==` (never `==` or `!=`)
- Destructuring: `const { key } = obj`
- Optional chaining: `obj?.prop?.nested`

### Formatting

ESLint and Prettier are configured in `eslint.config.js` and `.prettierrc`.
Run before committing:

```bash
npx eslint --fix .
npx prettier --write .
```

### Module Structure

```javascript
// Good: named exports
export function parseLink(url) { ... }
export function validateUrl(url) { ... }

// Avoid: anonymous default exports
export default function(url) { ... }
```

### Error Handling

```javascript
// Good
async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${url}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch failed:', error.message);
    throw error;
  }
}
```

## CSS Style

### Design Token System

All colors, spacing, typography, and shadows must use CSS custom properties
(design tokens) defined in `css/tokens/`:

```css
/* Good — uses tokens */
.nav-link {
  color: var(--color-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-body);
}

/* Bad — hardcoded values */
.nav-link {
  color: #3b82f6;
  padding: 8px 16px;
  font-size: 16px;
}
```

### BEM Naming

Use BEM (Block__Element--Modifier) for CSS class names:

```css
/* Block */
.bibliography { ... }

/* Element */
.bibliography__entry { ... }
.bibliography__title { ... }

/* Modifier */
.bibliography__entry--highlighted { ... }
```

### Mobile-First

Write mobile styles first, then scale up with `min-width` media queries:

```css
.sidebar {
  display: none;           /* Mobile: hidden */
}

@media (min-width: 768px) {
  .sidebar {
    display: block;        /* Tablet+: shown */
  }
}
```

### No ID Selectors in CSS

IDs are for JavaScript hooks. CSS must use class selectors only:

```css
/* Good */
.header-nav { ... }

/* Bad */
#header-nav { ... }
```

### Accessibility

- Provide `:focus-visible` styles for all interactive elements
- Use `prefers-reduced-motion` for animations
- Minimum touch target size: 44×44px (enforced by `test_validate_accessibility.py`)

```css
.button:focus-visible {
  outline: var(--focus-outline-width) solid var(--focus-outline-color);
  outline-offset: var(--focus-outline-offset);
}

@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

## Quarto Content Style

### Front Matter

Every `.qmd` file must have YAML front matter with at minimum:

```yaml
---
title: "Article Title"
description: "One-sentence description for SEO and navigation."
date: 2026-01-15
---
```

### Citations

Use Pandoc citation keys `[@AuthorYear]` — not inline URLs. All citation keys
must appear in `resources/bibliography.qmd` or a local `.bib` file.

```markdown
The control-affine formulation follows [@Murray1994] and is reviewed
in [@Isidori1989, Ch. 4].
```

### LaTeX Math

Use `$...$` for inline and `$$...$$` for display math. Label equations for
cross-referencing:

```markdown
The affine drift term satisfies

$$
\dot{x} = f(x) + g(x)u
$$ {#eq-affine-control}

where $f$ is the drift field and $g$ is the input matrix.

As shown in @eq-affine-control, ...
```

### Internal Links

Use relative `.qmd` paths (not `.html`) so Quarto resolves them correctly:

```markdown
See [Canonical Parameters](PARAMETERS.md) for symbol definitions.
```

## File Size Budget

The file-sizing strategy is documented in
[`docs/development/repository_inventory.md`](repository_inventory.md).
Key limits:

| File type | Soft limit | Hard limit |
|-----------|-----------|-----------|
| Python module (`src/`) | 300 lines | 500 lines |
| Test file | 400 lines | 600 lines |
| Quarto article | 600 lines | 1000 lines |
| CSS file | 500 lines | 800 lines |
| JavaScript module | 300 lines | 500 lines |

Files exceeding the soft limit should be split. Files exceeding the hard limit
are blocked by CI size checks.

## Commit Message Conventions

AffineDrift follows **Conventional Commits**:

```
<type>(<scope>): <short description>

[optional body]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Types:**

| Type | When to use |
|------|------------|
| `feat` | New feature or content |
| `fix` | Bug fix or correction |
| `docs` | Documentation only |
| `refactor` | Code restructure without behavior change |
| `test` | Adding or fixing tests |
| `chore` | Build, CI, dependency updates |
| `perf` | Performance improvement |

**Scope** (optional): `ci`, `src`, `tests`, `docs`, `css`, `js`, `api`

```
feat(src): add trajectory smoothing to iLQR solver
fix(ci): increase pip install timeout for slow runners
docs(api): add docstrings to ball_flight module
test(src): add property-based tests for residual norm
```

## References

- `CONTRIBUTING.md` — full contribution guide
- `pyproject.toml` — ruff and mypy configuration
- `eslint.config.js` — JavaScript lint rules
- `css/tokens/` — CSS design token definitions
- `docs/development/testing-guide.md` — test writing guide
