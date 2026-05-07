# Troubleshooting & Debug Guide

Quick-reference guide for diagnosing and resolving common errors in AffineDrift.
Entries follow the format: **Error → Likely Causes (ranked) → Resolution → Prevention**.

---

## CI / GitHub Actions

### `No runners are available to run the requested job`

**Likely causes:**
1. Self-hosted runner service is stopped.
2. Runner registration expired.
3. Runner machine is offline.

**Resolution:**
```bash
# On runner machine — restart the service
sudo systemctl restart actions.runner.d-sorganization.*.service

# Check registration
gh api repos/d-sorganization/AffineDrift/actions/runners
```

See [Playbook PB-002](incident-response-playbooks.md#pb-002-runner-outage).

---

### `Raw git merge conflict markers found!`

**Cause:** A file containing `<<<<<<< HEAD` was committed.

**Resolution:**
```bash
# Find the conflicted file
grep -rn "<<<<<<< HEAD" . --exclude-dir=.git

# Resolve the conflict manually, then:
git add <file>
git commit --amend  # or add a new fix commit
git push
```

---

### `pip install timeout` or `Retrying (Attempt N)`

**Likely causes:**
1. PyPI is slow (transient).
2. CI runner has poor network connectivity.
3. Package index is unavailable.

**Resolution:**
```bash
# CI uses a 600-second pip timeout (see ci-standard.yml)
# Retry the CI run manually:
gh run rerun <run_id> --failed

# If persistent, check PyPI status:
# https://status.python.org/
```

---

### `mypy: error: Argument has incompatible type`

**Likely causes (ranked):**
1. Missing type annotation on a new function.
2. `None` not handled (missing `Optional` or `| None`).
3. Third-party stub package missing.

**Resolution:**
```bash
# Run mypy with detailed output
python -m mypy src/ --show-error-codes --pretty

# Common fixes:
# Missing return type
def fn(x: int) -> float: ...

# Missing Optional
from typing import Optional
def fn(x: Optional[str] = None) -> None: ...

# Missing stub
pip install types-requests  # then add to requirements.txt
```

---

### `ruff: Found X lint errors`

**Resolution:**
```bash
# Auto-fix most errors
python -m ruff check --fix .
python -m ruff format .

# Check what remains
python -m ruff check .

# For manual fixes, see the error code:
# E501: line too long → shorten or use continuation
# F401: unused import → remove
# B007: loop variable unused → use _ as name
```

---

### `pytest: FAILED tests/test_xxx.py — AssertionError`

**Diagnosis:**
```bash
# Run with verbose + traceback
python -m pytest tests/test_xxx.py -v --tb=long

# Run with captured output
python -m pytest tests/test_xxx.py -v -s

# Check if failure is on main too
git stash
python -m pytest tests/test_xxx.py
git stash pop
```

---

## Python Source (`src/`)

### `ImportError: cannot import name 'X' from 'src.module'`

**Likely causes:**
1. Module renamed or moved.
2. Circular import.
3. PYTHONPATH not set.

**Resolution:**
```bash
# Ensure PYTHONPATH includes repo root
export PYTHONPATH=.

# Check the module exists
python -c "from src.module import X"

# Circular import: use lazy imports or restructure
```

---

### `ValueError: theta must be in [0, π]` (or similar contract violation)

**Cause:** Caller violated a precondition. Check the calling code, not the module.

**Resolution:**
```python
# Add input validation before the call
theta = max(0.0, min(math.pi, raw_theta))
compute_function(theta)
```

---

### `numpy.linalg.LinAlgError: Singular matrix`

**Likely causes (ranked):**
1. Hessian is ill-conditioned (iLQR backward pass).
2. Near-zero regularization value.
3. State variables have incompatible scales.

**Resolution:**
```python
# Increase regularization in ILQRSolver
solver = ILQRSolver(
    cost_fn=cost,
    dynamics=dynamics,
    regularization_init=1e-2,  # increase from default 1e-4
)

# Or normalize state variables to similar scales
```

---

### `RuntimeError: Solver did not converge`

**Likely causes:**
1. `max_iterations` too low for the problem.
2. Cost function poorly conditioned.
3. Initial state too far from feasible.

**Resolution:**
```python
# Increase iterations
config = SwingOptimizationConfig(max_iterations=500)

# Loosen convergence tolerance
config = SwingOptimizationConfig(convergence_tol=1e-4)

# Check initial state validity
print(f"Initial state: {initial_state}")
print(f"State norm: {np.linalg.norm(initial_state):.4f}")
```

---

### `logging.getLogger` — no output visible

**Cause:** Root logger level is WARNING; DEBUG/INFO messages suppressed.

**Resolution:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # in script entry points

# Or configure the specific logger
logging.getLogger("src.affine_control").setLevel(logging.DEBUG)
```

---

## Quarto / Site Build

### `quarto render: Unknown chunk option 'label'`

**Likely cause:** Quarto version mismatch. Some options changed between v1.3 and v1.4+.

**Resolution:**
```bash
quarto --version

# Update Quarto to the version in ci-standard.yml
# Or use the 1.4+ equivalent option
```

---

### `File not found: articles/xyz.qmd`

**Cause:** A `.qmd` file referenced in `_quarto.yml` navigation or another article
no longer exists.

**Resolution:**
```bash
# Find the broken reference
grep -r "xyz" _quarto.yml articles/ --include="*.qmd"

# Fix: update the reference or restore the file
```

---

### `Error in bibliography: Entry 'AuthorYear' not found`

**Cause:** Citation key used in a `.qmd` file is not in the `.bib` file.

**Resolution:**
```bash
# Find the broken citation
grep -rn "@AuthorYear" . --include="*.qmd"

# Find the bib file
ls resources/*.bib

# Add the missing entry or correct the citation key
```

---

### `Quarto syntax check: front matter missing 'title'`

**Cause:** A new `.qmd` file lacks required YAML front matter.

**Resolution:**
```yaml
---
title: "Article Title"
description: "Brief description."
date: 2026-05-07
---
```

---

## Docker / Container

### `docker build: checksum mismatch for quarto.deb`

**Cause:** Quarto released a new patch version; the SHA256 checksum in the
Dockerfile is outdated.

**Resolution:**
```bash
# Download the new version and compute the checksum
curl -L <quarto-deb-url> -o quarto.deb
sha256sum quarto.deb

# Update the checksum in the Dockerfile
```

---

### `requirements-docker.lock: hash mismatch`

**Cause:** A dependency was updated but the lock file wasn't regenerated.

**Resolution:**
```powershell
py -3.12 -m piptools compile --allow-unsafe --generate-hashes `
  --resolver=backtracking `
  --output-file requirements-docker.lock `
  requirements.txt
git add requirements-docker.lock
git commit -m "chore(deps): regenerate requirements-docker.lock"
```

---

## JavaScript / Frontend

### `npm test: Cannot find module '@testing-library/jest-dom'`

**Resolution:**
```bash
npm install
# Or if package.json is correct but node_modules is corrupt:
rm -rf node_modules package-lock.json
npm install
```

---

### `ESLint: Parsing error`

**Cause:** ES6+ syntax used without proper ESLint config, or mismatched
`ecmaVersion`.

**Resolution:**
```bash
# Check ESLint config
cat eslint.config.js

# Run ESLint with debug output
npx eslint --debug src/js/module.js 2>&1 | head -30
```

---

### `stylelint: Unknown rule`

**Cause:** stylelint plugin not installed or config mismatched.

**Resolution:**
```bash
npm install  # reinstall all plugins
npx stylelint --print-config css/styles.css
```

---

## Link Checker

### `ERROR: Undefined reference: @sec-xyz`

**Cause:** A Quarto cross-reference to `@sec-xyz` is used in a file, but no
element with `{#sec-xyz}` label is defined.

**Resolution:**
```bash
# Find the reference
grep -rn "@sec-xyz" . --include="*.qmd"

# Find where to add the label
grep -rn "## Expected Section Title" . --include="*.qmd"

# Add the label to the heading:
## Expected Section Title {#sec-xyz}
```

---

### `WARN: Invalid URL: https://... (Connection error)`

**Cause:** External URL is unreachable (transient) or the site is down.

**Resolution:**
- Retry after 5 minutes (most are transient).
- If persistent, replace with an archived URL (Wayback Machine).
- Add the domain to `KNOWN_FRAGILE_URLS` in `scripts/link-checker.py` if
  it's consistently unreliable.

---

## Getting More Help

1. **Search existing issues**: `gh issue list --repo d-sorganization/AffineDrift --state all --search "error message"`
2. **Check CI logs**: `gh run view <id> --log-failed`
3. **Ask in a new issue**: Include the error message, reproduction steps, and
   `git log --oneline -5` output.
4. **Check incident playbooks**: `docs/operations/incident-response-playbooks.md`

## References

- `docs/operations/incident-response-playbooks.md` — full playbooks with timelines
- `docs/development/testing-guide.md` — test debugging
- `docs/development/code-style-guide.md` — lint and formatting
- [Quarto docs](https://quarto.org/docs/)
- [ruff docs](https://docs.astral.sh/ruff/)
- [mypy docs](https://mypy.readthedocs.io/)
