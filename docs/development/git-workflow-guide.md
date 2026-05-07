# Git Workflow Guide

This guide documents the branch, commit, and PR workflow for AffineDrift
contributors. It is the operational companion to `CONTRIBUTING.md`.

## Branch Strategy

AffineDrift uses a **trunk-based development** model with short-lived feature
branches.

```
main (protected)
  ├── feat/<scope>-<issue>          # New features/content
  ├── fix/<scope>-<issue>           # Bug fixes
  ├── docs/<scope>-<issue>          # Documentation only
  ├── chore/<scope>-<issue>         # Build/CI/dependency work
  └── test/<scope>-<issue>          # Test additions only
```

### Branch Naming

```bash
# Feature
git checkout -b feat/ilqr-convergence-2919

# Fix
git checkout -b fix/link-checker-timeout-2965

# Documentation
git checkout -b docs/wave5-api-reference-3052

# Test
git checkout -b test/property-based-swing-optimizer

# Chore
git checkout -b chore/update-ruff-2.0
```

Use the issue number where applicable. Keep names concise but descriptive.

### Protected Branches

`main` is the only protected branch:

- Direct pushes are blocked.
- All changes require a PR.
- Branch protection requires CI checks to pass.
- Self-merge is allowed for the repository owner.

## Commit Conventions

AffineDrift follows **Conventional Commits** (https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <short description (≤72 chars)>

[optional body — explain WHY, not WHAT]

[optional footer: Co-Authored-By, Closes #issue]
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature, content, or capability |
| `fix` | Bug fix or content correction |
| `docs` | Documentation only changes |
| `refactor` | Code restructure, no behavior change |
| `test` | New or updated tests |
| `chore` | CI, build, dependency, tooling |
| `perf` | Performance improvement |
| `revert` | Reverts a previous commit |

### Scope (optional)

Scopes help reviewers quickly identify the affected area:

| Scope | Applies to |
|-------|-----------|
| `ci` | GitHub Actions workflows |
| `src` | Python source in `src/` |
| `tests` | Test suite |
| `docs` | Markdown documentation |
| `css` | Stylesheet changes |
| `js` | JavaScript modules |
| `api` | Public API surface |
| `deps` | Dependency updates |

### Examples

```bash
# Feature
git commit -m "feat(src): add trajectory smoothing to iLQR solver

Adds cubic spline smoothing as a post-processing step to reduce
high-frequency oscillations in the optimized control sequence.
Closes #2919"

# Fix
git commit -m "fix(ci): increase pip install timeout to 600s

Slow CI runners occasionally timeout at 300s.
Resolves #3037"

# Docs
git commit -m "docs(api): add docstrings to ball_flight module

Closes #3052"

# Chore with Co-Author
git commit -m "chore(deps): update hypothesis to 6.152.4

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### Commit Hygiene

- **One logical change per commit.** Squash WIP commits before opening a PR.
- **No merge commits in feature branches.** Use `git rebase origin/main` to
  update a branch.
- **No force-push on shared branches.** Only force-push on your own branches
  before a PR is reviewed.

## Pull Request Workflow

### Before Opening a PR

Run the full local quality check:

```powershell
# 1. Lint
python -m ruff check .

# 2. Auto-fix lint
python -m ruff check --fix .

# 3. Format
python -m ruff format .

# 4. Type check
python -m mypy .

# 5. Tests
python -m pytest tests/ -q

# 6. JavaScript
npm test
```

All checks must pass before opening a PR. A failing PR blocks the merge queue.

### PR Title

Follow the same Conventional Commits format as commit messages:

```
docs(api): add public API reference for src/ modules (Issue #3052)
feat(src): implement adiabatic trajectory solver (Issue #2887)
fix(ci): resolve runner dispatch timeout (Issue #3037)
```

### PR Description Template

```markdown
## Summary

[One paragraph explaining what changed and why.]

## Changes

- `src/module.py`: [What changed]
- `tests/test_module.py`: [Tests added]
- `docs/api.md`: [Documentation added]

## Testing

- [ ] `python -m pytest tests/ -q` passes
- [ ] `python -m mypy .` passes
- [ ] `python -m ruff check .` passes
- [ ] JavaScript tests pass (`npm test`)

## Related Issues

Closes #<issue-number>
```

### PR Size

Keep PRs focused and reviewable:

| Size | Lines changed | Action |
|------|--------------|--------|
| Small | < 200 | Preferred |
| Medium | 200–500 | Acceptable |
| Large | 500–2000 | Add `large-pr-approved` label |
| XL | > 2000 | Split the PR |

CI may enforce a size check. The `large-pr-approved` label bypasses it when
the size is intentional (e.g., bulk rename, auto-generated content).

### Merge Strategy

**Squash merge** is preferred for feature branches to keep `main` history clean.
All commits in the branch become a single commit with the PR title as the message.

Use **merge commit** only when preserving branch history is explicitly required.

Rebase merge is not used.

## Keeping Your Branch Up to Date

Use rebase to incorporate changes from `main` without merge commits:

```bash
# Update main
git fetch origin main

# Rebase your branch onto the latest main
git rebase origin/main

# If conflicts arise, resolve then:
git add <resolved-files>
git rebase --continue

# Push the rebased branch (force required after rebase)
git push --force-with-lease origin feat/your-branch
```

**Never rebase shared branches** (branches other contributors have checked out).

## Handling Merge Conflicts

If a PR has merge conflicts, resolve them locally:

```bash
git fetch origin main
git merge origin/main

# Resolve each conflicted file
# Use VS Code or: git checkout --theirs <file> or --ours <file>

git add <resolved-files>
git commit -m "merge: resolve conflicts with main"
git push origin feat/your-branch
```

For non-code files (docs, config), prefer the incoming (`main`) version unless
the PR intentionally changed the file.

## Agent-Created Branches

This repository uses autonomous agents (Claude, Maxwell-Daemon). Their branches
follow the same conventions with agent-specific prefixes:

- `codex/<task>` — Codex-generated (blocked by governance)
- `bolt/<task>` — Bolt agent
- `palette/<task>` — Palette UX agent
- `sentinel/<task>` — Sentinel security agent
- `docs/<task>` — Documentation agent (this guide)

Agent PRs are governed by `docs/GOVERNANCE.md` and subject to the same CI gates.

## Release Process

AffineDrift does not maintain numbered releases. The `main` branch is the
authoritative deployment source. The site at AffineDrift.com deploys
automatically on every merge to `main` via `.github/workflows/deploy-website.yml`.

For significant milestone tracking, update `CHANGELOG.md` with:

```markdown
## [Unreleased]

### Added
- Wave 5 documentation: testing guide, code style guide, git workflow

### Fixed
- Link checker skips GitHub URLs and localhost

### Changed
- iLQR solver now returns convergence metadata
```

## References

- `CONTRIBUTING.md` — full contribution guide with setup instructions
- `docs/development/code-style-guide.md` — code formatting conventions
- `docs/development/testing-guide.md` — test writing guide
- `docs/GOVERNANCE.md` — agent governance policy
- `.github/workflows/ci-standard.yml` — CI pipeline definition
