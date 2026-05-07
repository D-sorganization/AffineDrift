# Incident Response Playbooks

Standard response procedures for AffineDrift infrastructure and CI failures.
Each playbook follows the format: **Symptoms → Diagnosis → Resolution → Prevention**.

> **Context**: AffineDrift is a Quarto static site with Python tooling, GitHub
> Actions CI on self-hosted runners (`d-sorg-fleet`), and GitHub Pages deployment.
> The primary failure modes are CI pipeline failures, runner outages, and
> Quarto/dependency issues.

---

## Playbook Index

| Playbook | Trigger | MTTR Target |
|----------|---------|-------------|
| [PB-001](#pb-001-ci-pipeline-failure) | CI pipeline fails on PR | 30 min |
| [PB-002](#pb-002-runner-outage) | Self-hosted runner offline | 15 min |
| [PB-003](#pb-003-quarto-build-failure) | Quarto render/deploy fails | 45 min |
| [PB-004](#pb-004-python-dependency-conflict) | Dependency install fails | 30 min |
| [PB-005](#pb-005-merge-conflict-blocking-pr) | PR blocked by merge conflict | 20 min |
| [PB-006](#pb-006-sast-security-gate-failure) | bandit/pip-audit blocks merge | 60 min |
| [PB-007](#pb-007-type-check-regression) | MyPy strict mode failures | 45 min |
| [PB-008](#pb-008-test-suite-regression) | New test failures on main | 60 min |

---

## PB-001: CI Pipeline Failure

### Symptoms

- PR shows red CI status.
- Merge button disabled.
- GitHub Actions job shows `quality-gate` failed.

### Diagnosis

```bash
# View failing CI logs
gh run list --repo d-sorganization/AffineDrift --limit 5
gh run view <run_id> --log-failed
```

Categorize the failure:

| Log output | Likely cause | Playbook |
|-----------|-------------|---------|
| `ruff check` errors | Lint violations | Fix lint, re-push |
| `mypy` errors | Type annotation gaps | PB-007 |
| `pytest` failures | Test regressions | PB-008 |
| `pip install` failure | Dependency conflict | PB-004 |
| `quarto check` failure | Quarto syntax error | PB-003 |
| `runner offline` | Runner not available | PB-002 |

### Resolution

**Lint failures:**
```bash
git checkout <pr-branch>
python -m ruff check --fix .
python -m ruff format .
git add -p && git commit -m "fix(ci): resolve ruff lint violations"
git push
```

**Test failures:** See PB-008.

**Runner issues:** See PB-002.

### Prevention

- Run `ruff check . && python -m mypy . && python -m pytest tests/ -q` locally
  before every push.
- Use the pre-push hook in `CONTRIBUTING.md`.

---

## PB-002: Runner Outage

### Symptoms

- CI jobs stuck in "Queued" state for > 10 minutes.
- Runner status page shows offline.
- Error: `No runners are available to run the requested job.`

### Diagnosis

```bash
# Check runner status
gh api repos/d-sorganization/AffineDrift/actions/runners
```

Expected: runner with `status: "online"`.

### Resolution

1. **Check the runner machine** — ensure the self-hosted runner service is running:
   ```bash
   # On the runner machine
   sudo systemctl status actions.runner.d-sorganization.*.service
   sudo systemctl start actions.runner.d-sorganization.*.service
   ```

2. **Re-register the runner** if the service is missing:
   - Go to GitHub > Repository > Settings > Actions > Runners.
   - Click "New self-hosted runner" and follow the registration steps.

3. **Trigger CI re-run** once the runner is back:
   ```bash
   gh run rerun <run_id> --failed
   ```

### Prevention

- Monitor runner health with `docs/operations/slo-targets.md` dashboards.
- Set up systemd watchdog for the runner service.
- Keep 2+ runners registered for redundancy.

---

## PB-003: Quarto Build Failure

### Symptoms

- `deploy-website.yml` fails on `quarto render`.
- Site not updated at AffineDrift.com.
- `quarto-syntax-check.yml` fails on PR.

### Diagnosis

```bash
# Reproduce locally
cd AffineDrift
quarto check
quarto render --quiet 2>&1 | tail -50
```

Common causes:

| Error | Cause |
|-------|-------|
| `Unknown chunk option` | Quarto version mismatch |
| `File not found: xyz.qmd` | Renamed file, broken cross-reference |
| `pandoc.exe: cannot find` | Pandoc not installed |
| `BibTeX error` | Malformed .bib entry |
| `YAML parse error` | Bad front matter |

### Resolution

**Broken cross-reference:**
```bash
# Find the reference
grep -r "@sec-broken-ref" . --include="*.qmd"
# Fix the reference or add the label
```

**YAML front matter error:**
```bash
python -m pytest tests/test_frontmatter_utils.py -v
```

**Quarto version mismatch:**
```bash
quarto --version  # Check local version
# Compare to .github/workflows/deploy-website.yml: QUARTO_VERSION
```

### Prevention

- Run `quarto check` before pushing `.qmd` changes.
- CI syntax check runs on all PRs (not skipped for docs).
- New `.qmd` files must be added to the Quarto project `_quarto.yml`.

---

## PB-004: Python Dependency Conflict

### Symptoms

- CI fails at `pip install` step.
- Error: `ERROR: Cannot install package X because of requirement Y`.
- `pip-audit` flags a vulnerability.

### Diagnosis

```bash
pip install -r requirements.txt 2>&1 | grep "ERROR"
pip-audit --requirement requirements.txt
```

### Resolution

**Version conflict:**
```bash
# Identify conflicting packages
pip install -r requirements.txt --dry-run 2>&1

# Update the conflicting package version in requirements.txt
# Run tests to verify
python -m pytest tests/ -q
```

**Security vulnerability:**
```bash
pip-audit --requirement requirements.txt --fix --dry-run
# Review the proposed fix
# Update requirements.txt
# Regenerate Docker lock if needed:
py -3.12 -m piptools compile --allow-unsafe --generate-hashes \
  --resolver=backtracking \
  --output-file requirements-docker.lock requirements.txt
```

### Prevention

- Dependabot opens PRs for outdated packages automatically.
- `pip-audit` runs in CI — vulnerabilities block merge.
- Avoid unpinned (`>=X.Y`) dependencies in production requirements.

---

## PB-005: Merge Conflict Blocking PR

### Symptoms

- GitHub PR page shows "This branch has conflicts".
- CI fails with "merge conflict marker found" check.

### Resolution

```bash
# Fetch latest main
git fetch origin main

# On the PR branch, merge main
git checkout <pr-branch>
git merge origin/main

# Resolve each conflicted file
# For non-code files (docs, config): prefer incoming
git checkout --theirs <file>

# For intentionally modified files: resolve manually, then
git add <resolved-file>

git commit -m "merge: resolve conflicts with main

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin <pr-branch>
```

CI will re-run automatically after the push.

### Prevention

- Keep PRs short and focused.
- Rebase or merge main into long-lived branches daily.
- The `check-merge-conflicts` CI step catches markers before merge.

---

## PB-006: SAST Security Gate Failure

### Symptoms

- CI fails at bandit or pip-audit step.
- Error: `Issue [B604] Found shell injection vulnerability`.

### Resolution

**bandit finding:**
```bash
# See the full finding
python -m bandit -r src/ -c pyproject.toml --format txt

# For false positives, add a targeted noqa comment with justification:
result = subprocess.run(cmd, shell=False)  # noqa: B603 - shell=False is set

# For real issues: fix the code
```

**pip-audit vulnerability:**
See PB-004.

### Escalation

If a finding represents a genuine vulnerability that cannot be immediately fixed:

1. Open a `security` labeled issue with full details.
2. Add a `# noqa: B<code>` suppression with a comment linking the issue.
3. Set the issue milestone to the next sprint.

---

## PB-007: Type Check Regression (MyPy)

### Symptoms

- CI fails at `mypy` step.
- Error: `error: Argument 1 to "solve" has incompatible type`.

### Diagnosis

```bash
python -m mypy src/ --show-error-codes
```

### Resolution

**Missing return annotation:**
```python
# Before
def compute_cost(state):
    return float(np.sum(state ** 2))

# After
def compute_cost(state: np.ndarray) -> float:
    return float(np.sum(state ** 2))
```

**Incompatible types:**
```python
# Use Optional[T] or T | None for nullable values
def get_result(key: str) -> TrajectoryResult | None:
    return self._cache.get(key)
```

**Third-party stub missing:**
```bash
pip install types-<package>  # e.g., types-requests
# Add to requirements.txt
```

### Prevention

- Run `python -m mypy src/` locally before pushing.
- CI enforces mypy strict mode — new code must be fully typed.

---

## PB-008: Test Suite Regression

### Symptoms

- New test failures on main after a merge.
- `pytest` fails on previously-passing tests.

### Diagnosis

```bash
# Run failing tests with verbose output
python -m pytest tests/test_failing.py -v --tb=long

# Check if failure is pre-existing on main
git checkout main
python -m pytest tests/test_failing.py -v
```

### Resolution

**Test failure introduced by a new commit:**
```bash
# Identify the breaking commit
git bisect start
git bisect bad HEAD
git bisect good <last-good-sha>
# pytest to identify the commit
```

**Flaky test (intermittent):**
```bash
# Run 10 times to confirm flakiness
python -m pytest tests/test_flaky.py --count=10
```

For flaky tests:
1. Add retry logic if the test validates an inherently probabilistic outcome.
2. Fix the underlying non-determinism.
3. Mark as `@pytest.mark.xfail(strict=False)` temporarily with a tracking issue.

### Post-Incident

After resolving:
1. Add a regression test to prevent recurrence.
2. Document the root cause in the commit message.
3. Update this playbook if a new failure pattern was encountered.

---

## Post-Incident Review Template

Use this template after any incident that took > 1 hour to resolve:

```markdown
## Post-Incident Review — [Title]

**Date:** YYYY-MM-DD
**Duration:** X hours Y minutes
**Severity:** Low / Medium / High
**Playbook used:** PB-00X

### Timeline

- HH:MM — Issue detected
- HH:MM — Root cause identified
- HH:MM — Fix applied
- HH:MM — CI green, resolved

### Root Cause

[One paragraph explaining the root cause]

### Resolution

[What was done to fix it]

### Prevention

[Changes to prevent recurrence: tests added, config changes, playbook updates]

### Action Items

- [ ] [Action] — owner, due date
```

## References

- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Quarto troubleshooting](https://quarto.org/docs/troubleshooting/)
- `docs/operations/slo-targets.md` — SLO targets and error budgets
- `docs/operations/monitoring-setup.md` — monitoring and alerting
- `docs/development/security-guidelines.md` — security response
- `.github/workflows/ci-standard.yml` — CI pipeline definition
