# Workflow Trigger Assessment Report

**Date:** 2026-01-26
**Status:** Critical Issues Identified
**Scope:** CI/CD Pipeline Trigger Analysis

---

## Executive Summary

Analysis of 52 GitHub Actions workflows revealed critical issues preventing full CI/CD pipeline execution on bot-created PRs. The primary cause is GitHub's security feature that prevents `GITHUB_TOKEN`-authenticated actions from triggering new workflow runs.

---

## Workflows Analyzed

| Category | Count | Examples |
|----------|-------|----------|
| CI/CD Core | 4 | ci-standard, deploy-website, codeql, quarto-syntax-check |
| Jules Automation | 35 | Control-Tower, Auto-Repair, PR-AutoFix, Assessment-Generator |
| Maintenance | 8 | stale-cleanup, PR-Cleanup, Bot-CI-Trigger |
| Metrics/Reporting | 5 | Code-Metrics, agent-metrics-dashboard, ci-failure-digest |

---

## Critical Issues

### Issue 1: GITHUB_TOKEN Limitation (Severity: Critical)

**Problem:** Bot-created PRs don't trigger CI workflows due to GitHub's infinite loop prevention.

When workflows create PRs using `GITHUB_TOKEN`, new workflow runs are NOT triggered. This is by design to prevent infinite loops.

**Affected Scenarios:**
- PRs created by `github-actions[bot]`
- PRs from Control Tower workers (Assessment Generator, Auto-Repair, etc.)
- Any automated PR creation

**Current Mitigation:** `Bot-CI-Trigger.yml` attempts to:
1. Detect bot PRs without CI runs
2. Trigger CI via `workflow_dispatch`
3. Fallback: empty commit push

**Gap:** If `BOT_PAT` secret is not configured (or misconfigured), it falls back to `GITHUB_TOKEN` which won't trigger new runs.

**Required Fix:**
```yaml
# BOT_PAT secret must have these permissions:
# - repo (full control)
# - workflow (update workflows)
```

---

### Issue 2: Branch-Restricted Workflow Triggers (Severity: Medium)

**Problem:** Several workflows only trigger on PRs to `main/master`, missing feature branch PRs.

| Workflow | Current Trigger | Impact |
|----------|----------------|--------|
| `quarto-syntax-check.yml` | `pull_request: branches: [main, master]` | Won't run on feature branch PRs |
| `codeql.yml` | `pull_request: branches: [main]` | Security scans skip feature PRs |
| `Code-Metrics.yml` | `pull_request: branches: [main]` | No metrics on feature PRs |

**Contrast - Correct Pattern:** `ci-standard.yml` uses:
```yaml
on:
  pull_request:  # No branch filter = runs on ALL PRs
```

---

### Issue 3: Cascading Dependency Chain (Severity: High)

**Problem:** Workflows depend on `CI Standard` running first. If it doesn't trigger, the entire downstream chain fails.

```
CI Standard (must run first)
    │
    ├── Jules-Control-Tower (workflow_run: CI Standard)
    │       ├── Jules-Auto-Repair (when CI fails)
    │       ├── Jules-Test-Generator (when PR opened)
    │       └── Other workers...
    │
    └── Jules-PR-AutoFix (workflow_run: CI Standard)
```

---

### Issue 4: Concurrency Group Cancellation (Severity: Low)

**Problem:** Rapid pushes to the same branch cancel in-progress CI runs.

**In `ci-standard.yml`:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Impact:** If a bot pushes a fix while CI is running, the original CI run is cancelled, potentially leading to race conditions.

---

## Recent Fix Attempts

| Date | Commit | Description |
|------|--------|-------------|
| 2026-01-25 | `cb67058` | fix: workflow YAML fixes and unique branch timestamps |
| 2026-01-25 | `89f15e1` | fix: replace broken Jules workflows with working alternatives |
| 2026-01-25 | `4a280b1` | fix: Add checks:read permission, fix Auto-Repair |
| 2026-01-25 | `65b3e82` | fix: use BOT_PAT for auto-assign workflow |
| 2026-01-25 | `66f8c3f` | fix: shift all schedules to overnight PST |
| 2026-01-25 | `d1fa71f` | fix: downgrade github-script v8 to v7 |

---

## Overnight Schedule Analysis

The Control Tower orchestrates overnight workflows on this schedule (PST):

| Time (PST) | Cron (UTC) | Workflow |
|------------|------------|----------|
| Midnight | `0 8 * * *` | Assessment Generator |
| 12:30 AM | `30 8 * * *` | Code Quality Reviewer |
| 1:00 AM | `0 9 * * *` | Completist |
| 2:30 AM | `30 10 * * *` | Sentinel |
| 3:00 AM | `0 11 * * *` | Auto-Refactor |
| 4:00 AM | `0 12 * * *` | PR Compiler |
| 5:00 AM | `0 13 * * *` | Auto-Rebase |

**Status:** Schedule appears correctly configured with appropriate spacing.

---

## Recommendations

### Priority 1: Verify BOT_PAT Secret (Critical)

Ensure the `BOT_PAT` repository secret is configured with:
- `repo` scope (full control of private repositories)
- `workflow` scope (update GitHub Action workflows)

### Priority 2: Standardize PR Triggers (Medium)

Remove branch restrictions from PR triggers for consistency:

```yaml
# Change from:
pull_request:
  branches: [main]

# To:
pull_request:  # Runs on ALL PRs
```

**Files to update:**
- `.github/workflows/quarto-syntax-check.yml`
- `.github/workflows/codeql.yml`
- `.github/workflows/Code-Metrics.yml`

### Priority 3: Add Diagnostic Logging (Low)

Enhance `Bot-CI-Trigger.yml` with better logging to track:
- Which PRs are detected without CI
- Success/failure of trigger attempts
- Token permission issues

### Priority 4: Consider Concurrency Changes (Low)

For critical CI runs, consider:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false  # Let runs complete
```

---

## Verification Checklist

- [ ] Verify `BOT_PAT` secret exists in repository settings
- [ ] Verify `BOT_PAT` has `repo` and `workflow` scopes
- [ ] Test manual trigger of `Bot-CI-Trigger` workflow
- [ ] Monitor next overnight run cycle for failures
- [ ] Check GitHub Actions usage limits haven't been exceeded

---

## Appendix: Workflow Trigger Summary

### Workflows with `pull_request` trigger (run on PRs)
- `ci-standard.yml` - All PRs
- `quarto-syntax-check.yml` - PRs to main/master only
- `codeql.yml` - PRs to main only
- `Code-Metrics.yml` - PRs to main only
- `Bot-CI-Trigger.yml` - All PRs
- `pr-auto-labeler.yml` - All PRs
- `Jules-Control-Tower.yml` - All PRs
- `Comment-to-Issue-Converter.yml` - All PRs

### Workflows with `workflow_run` trigger (depend on other workflows)
- `Jules-PR-AutoFix.yml` - After CI Standard
- `Jules-Control-Tower.yml` - After CI Standard

### Workflows with `schedule` trigger (cron-based)
- `Jules-Control-Tower.yml` - Multiple overnight schedules
- `Bot-CI-Trigger.yml` - Every 15 minutes
- `stale-cleanup.yml` - Daily at 1 AM PST
- `Jules-Completist.yml` - Daily at 1 AM UTC
- `Jules-DRY-Orthogonality.yml` - Daily at 4 AM PST

---

*Report generated by workflow analysis on 2026-01-26*
