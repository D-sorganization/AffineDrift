# Monitoring & Observability Setup

AffineDrift's monitoring strategy covers CI/CD health, site availability,
and Python tooling quality. This document describes the current monitoring
configuration and the roadmap for expanding observability.

---

## Current Monitoring (Active)

### GitHub Actions CI

**What's monitored:** All CI pipeline runs via GitHub's built-in tooling.

**How to access:**
```bash
# Command line
gh run list --repo d-sorganization/AffineDrift --limit 20
gh run view <run_id>

# Web UI
# https://github.com/D-sorganization/AffineDrift/actions
```

**Metrics available:**
- Pass/fail status per job
- Run duration
- Failure logs
- Queue wait time (visible in job timeline)

**Notification setup:**
- GitHub sends email notifications for workflow failures by default.
- Ensure notifications are enabled: GitHub > Settings > Notifications > Actions.

---

### GitHub Pages Availability

**What's monitored:** Deployment success/failure via `deploy-website.yml` runs.

**How to verify site health:**
```bash
# Check last deploy status
gh run list --workflow deploy-website.yml --limit 5

# Quick HTTP check
curl -s -o /dev/null -w "%{http_code}" https://AffineDrift.com/
```

Expected: `200` or `301` (redirect to HTTPS).

**GitHub Pages status page:** https://www.githubstatus.com/

---

### Dependency Vulnerability Scanning

**What's monitored:** Python and JavaScript dependencies via Dependabot.

**Configuration:** `.github/dependabot.yml` (if not present, configure at
GitHub > Settings > Security > Dependabot).

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
```

**Manual scan:**
```bash
pip-audit --requirement requirements.txt
npm audit
```

---

### Code Quality Metrics

CI enforces the following quality gates on every PR:

| Gate | Tool | Threshold |
|------|------|----------|
| Lint | ruff | 0 errors |
| Format | ruff format | 0 diffs |
| Type check | mypy (strict) | 0 errors |
| Test coverage | pytest-cov | ≥ 90% src/ |
| Security scan | bandit | 0 high/critical |
| Dependency audit | pip-audit | 0 known vulns |
| Size check | CI script | No file > hard limit |

Results are visible in the GitHub Actions job log and as PR check statuses.

---

### Link Integrity

**What's monitored:** Internal Quarto cross-references and external URLs.

```bash
# Run manually
python scripts/link-checker.py --internal-only

# External URLs (slow — makes HTTP requests)
python scripts/link-checker.py --external-only
```

CI runs the internal-only check on all PRs. External URL checking is
opt-in due to flakiness of external services.

---

## Metrics Dashboard (Manual — In Progress)

Until an automated dashboard is configured, collect these metrics manually
via the weekly routine in `docs/operations/on-call-procedures.md`:

### CI Health Dashboard

```bash
#!/bin/bash
# ci-health.sh — run weekly to collect metrics
echo "=== CI Health Report $(date) ==="
echo ""
echo "Last 30 runs:"
gh run list --repo d-sorganization/AffineDrift --limit 30 \
  --json conclusion,createdAt,displayTitle \
  --jq '.[] | [.conclusion, .createdAt[:10], .displayTitle[:60]] | @tsv'

echo ""
echo "Pass rate (success / total):"
gh run list --repo d-sorganization/AffineDrift --limit 30 \
  --json conclusion \
  --jq 'group_by(.conclusion) | map({conclusion: .[0].conclusion, count: length}) | .[]'
```

### Coverage Trend

```bash
# Run locally to see coverage summary
python -m pytest tests/ --cov=src --cov-report=term-missing -q 2>&1 | tail -20
```

---

## Alerting Configuration

### Current Alerting (GitHub Notifications)

GitHub sends email notifications for:
- Workflow failures (configure in Settings > Notifications)
- Dependabot security alerts (auto-enabled)
- PR review requests

**Ensure these notification settings are active:**
- Go to GitHub > Settings > Notifications
- Check "Email" for "Actions" failures
- Check "Email" for "Security alerts"

### Future Alerting (Roadmap)

Tracked in Issue #3055. Planned setup:

```yaml
# Planned: .github/workflows/ci-health-monitor.yml
# Runs weekly and posts a summary to a GitHub issue
name: CI Health Monitor
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9am UTC
jobs:
  report:
    runs-on: d-sorg-fleet
    steps:
      - name: Collect CI metrics
        run: |
          # Collect pass rate, duration, coverage
          # Post to GitHub issue or send email
```

---

## Observability Gaps (Current)

The following observability capabilities are not yet implemented. They are
tracked in Issue #3055 for a future wave:

| Gap | Priority | Notes |
|-----|----------|-------|
| Automated weekly CI health report | Medium | Can be a GitHub Actions scheduled job |
| Historical coverage trend | Medium | Store coverage JSON artifact per run |
| Performance benchmark history | Low | Save benchmark JSON to `benchmarks/history/` |
| External URL health monitoring | Low | Scheduled link-checker run |
| GitHub Pages load time monitoring | Low | Use WebPageTest API or similar |

---

## Log Analysis

### CI Logs

```bash
# View full log for a specific run
gh run view <run_id> --log

# View only failed steps
gh run view <run_id> --log-failed

# Search logs for a pattern
gh run view <run_id> --log 2>&1 | grep -i "error\|warning\|failed"
```

### Python Application Logs

AffineDrift uses the standard `logging` module. When running locally:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
```

Key loggers to monitor:

| Logger | What it covers |
|--------|---------------|
| `src.affine_control.ddp` | DDP solver iterations and convergence |
| `src.affine_control.swing_optimizer` | Optimization pipeline |
| `src.core.optimizers.ilqr_solver` | iLQR backward/forward passes |
| `src.golf_simulation.ball_flight` | Ball flight integration |
| `src.tools.check_links` | Link checker results |

---

## Distributed Tracing (Not Implemented)

AffineDrift does not currently implement distributed tracing (no microservices).
If the codebase expands to include web API components, consider:

- **OpenTelemetry** for Python instrumentation
- **Jaeger** or **Datadog APM** for trace collection

This is tracked as a future enhancement in Issue #3055.

---

## Compliance and Audit Readiness

The following artifacts provide audit evidence:

| Artifact | Location | Purpose |
|----------|---------|---------|
| CI run history | GitHub Actions | Demonstrates quality gates pass |
| Coverage reports | CI logs | Code coverage evidence |
| Dependency audit logs | CI logs | Security compliance |
| Benchmark history | `benchmarks/` | Performance baseline evidence |
| Assessment reports | `docs/assessments/` | Periodic code quality assessments |

---

## References

- `docs/operations/slo-targets.md` — SLO definitions and error budgets
- `docs/operations/incident-response-playbooks.md` — incident response
- `docs/operations/on-call-procedures.md` — routine checks and response procedures
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [GitHub Status](https://www.githubstatus.com/)
