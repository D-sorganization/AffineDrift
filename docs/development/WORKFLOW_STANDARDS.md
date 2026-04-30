# GitHub Actions Workflow Standards

> Fleet CI/CD reliability and cost-control guidelines (Issue #1327)

## Required Elements for All Push/PR-Triggered Workflows

### 1. Concurrency Groups

Every workflow triggered by `push`, `pull_request`, or a combination MUST include a
concurrency group to cancel in-progress runs when a new commit is pushed:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Exception:** Workflows triggered only by `workflow_call` do not need their own concurrency
group (it is managed by the caller workflow).

**Exception for deploy workflows:** The `deploy` job in `deploy-website.yml` uses
`cancel-in-progress: false` to prevent mid-deployment cancellation:

```yaml
concurrency:
  group: ${{ github.workflow }}-deploy-${{ github.ref }}
  cancel-in-progress: false
```

### 2. Trigger Scope

Use path filters where applicable to avoid running expensive jobs on unrelated changes:

```yaml
on:
  push:
    paths:
      - "articles/**"
      - ".github/workflows/compile_textbooks.yml"
```

### 3. Permissions

All workflows should declare explicit minimum permissions:

```yaml
permissions:
  contents: read        # default; sufficient for most checks
  pages: write          # only if deploying to GitHub Pages
  id-token: write       # only if using OIDC
  pull-requests: write  # only if posting PR comments
```

Do not rely on repository-level permission defaults.

### 4. Timeout

Jobs that run external tools (LaTeX compilation, Quarto render, network calls) should set
an explicit timeout to prevent runaway billing:

```yaml
jobs:
  my-job:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Set appropriately for the expected runtime
```

### 5. Caching

Use `actions/cache` or built-in cache options (e.g., `setup-python@v6 cache: pip`) to
avoid re-downloading dependencies on every run. This can reduce run time by 50-80%.

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"
```

## Workflow Catalog

| File | Trigger | Concurrency | Status |
|------|---------|-------------|--------|
| `ci-standard.yml` | push, PR | ✅ | ✅ |
| `deploy-website.yml` | push main, dispatch | ✅ | ✅ |
| `compile_textbooks.yml` | push, PR (paths) | ✅ | ✅ |
| `quarto-syntax-check.yml` | push, PR, schedule | ✅ | ✅ |
| `latex-release-volumes.yml` | push main (paths) | ⚠️ missing | To fix |
| `Jules-Cleaner.yml` | PR closed | ⚠️ missing | To fix |
| `Jules-*` (workflow_call only) | workflow_call | N/A | OK |
| `Code-Metrics.yml` | schedule | Optional | OK |

## Cost-Control Patterns

### Schedule Optimization

Nightly or weekly schedules should run off-peak (UTC midnight or early morning) to
reduce queue wait times. Standard schedule for this fleet:

```yaml
schedule:
  - cron: "0 8 * * 0,4"  # Twice weekly: Sunday and Thursday at 08:00 UTC
```

Avoid `cron: "*/5 * * * *"` (every 5 minutes) — always use at minimum hourly intervals
for non-critical polling.

### External API Rate Limits

Workflows calling the GitHub API (via `gh` CLI or REST) should implement exponential
backoff with a maximum of 5 retries. The `Jules-*` workflows should handle rate limiting
gracefully rather than failing.

### Artifact Retention

Use short retention for large artifacts (LaTeX PDFs, test reports):

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: my-artifact
    path: output/
    retention-days: 7  # default is 90 days
```

## Reliability Checklist

Before adding a new workflow:

- [ ] Does it have a concurrency group (if triggered by push/PR)?
- [ ] Does it have explicit minimum permissions?
- [ ] Does it use path filters to avoid unnecessary runs?
- [ ] Does it have a timeout on expensive jobs?
- [ ] Does it cache dependencies?
- [ ] Does it have a `workflow_dispatch` trigger for manual re-runs?
- [ ] Are any secrets used minimal-scope (PAT with only needed permissions)?

## Credential Rotation

Bot tokens and app secrets should be rotated on a quarterly schedule. After rotation:

1. Update the secret in GitHub repository settings
2. Verify by triggering a `workflow_dispatch` dry run on any workflow that uses the token
3. Document the rotation date in this file

**Last rotation:** N/A (not yet established)
**Next scheduled rotation:** 2026-06-01
