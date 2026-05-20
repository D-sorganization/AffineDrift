# SLO & Performance Targets

Service Level Objectives (SLOs) for AffineDrift's CI/CD pipeline, GitHub Pages
site, and Python tooling. These targets govern when incidents are escalated and
how error budgets are tracked.

> **Scope**: AffineDrift is a personal research repository, not a
> multi-tenant service. SLOs here govern the development experience and
> content availability, not customer SLAs.

---

## CI/CD Pipeline SLOs

### CI Quality Gate

| Metric | Target | Measurement window |
|--------|--------|-------------------|
| **CI pass rate** (non-draft PRs) | ≥ 95% | Rolling 30 days |
| **CI cycle time** (queue + run) | ≤ 45 minutes | P95, rolling 7 days |
| **Runner availability** | ≥ 99% | Rolling 30 days |
| **False-positive rate** (flaky tests) | ≤ 2% of CI runs | Rolling 7 days |

### Deployment Pipeline

| Metric | Target | Measurement window |
|--------|--------|-------------------|
| **Deploy success rate** | ≥ 99% | Rolling 30 days |
| **Deploy cycle time** | ≤ 15 minutes | P95, push → live |
| **Rollback capability** | Available within 5 min | Tested monthly |

---

## Site Availability SLOs

### GitHub Pages (AffineDrift.com)

| Metric | Target | Notes |
|--------|--------|-------|
| **Uptime** | ≥ 99.9% | GitHub's own SLA for Pages |
| **Response time** | ≤ 2s P95 | Measured from CDN edge |
| **Broken link rate** | 0% internal links | Enforced by CI link checker |
| **Mobile render** | All pages pass | Tested in CI via Playwright |

GitHub Pages uptime depends on GitHub's infrastructure. The 99.9% target
reflects GitHub's published SLA; incidents outside our control consume no
error budget.

---

## Python Tooling SLOs

### Test Suite

| Metric | Target | Notes |
|--------|--------|-------|
| **Test execution time** | ≤ 10 minutes | Full `pytest tests/` run |
| **Code coverage** | ≥ 90% (src/) | Enforced by coverage floor |
| **Zero flaky tests** | 0 known flaky tests | Tracked in issues |
| **Mypy strict pass rate** | 100% | Zero type errors on main |

### Benchmark Suite

| Benchmark | Baseline | Regression threshold |
|-----------|---------|---------------------|
| `double_pendulum_drift` | < 5ms | +20% triggers warning |
| `double_pendulum_mass_matrix` | < 10ms | +20% triggers warning |
| `trajectory_tracking_cost` | < 2ms | +20% triggers warning |
| `rl_funnel_simulation` | < 100ms | +30% triggers warning |

Baselines are established per machine (runner hardware). A +50% regression
triggers a blocking issue.

---

## Error Budgets

### Monthly Error Budget Calculation

```
Error Budget = (1 - SLO Target) × Period Duration

Example (CI pass rate):
  Budget = (1 - 0.95) × 30 days × 24 hours × 60 minutes
  Budget = 2,160 minutes/month of allowed CI failures
```

### Budget Consumption Tracking

Track error budget consumption monthly. If budget is > 50% consumed by
mid-month:

1. Pause non-critical feature work.
2. Focus on flaky test stabilization.
3. Review CI logs for systemic failures.

If budget is exhausted:

1. Freeze non-bugfix PRs.
2. Run a post-incident review.
3. Create action items to prevent recurrence.

---

## Capacity Planning

### Runner Capacity

Current fleet: **1 self-hosted runner** (`d-sorg-fleet`).

Scaling triggers:
- CI queue time consistently > 15 minutes → add a second runner.
- Runner CPU > 80% during normal CI → upgrade machine.
- Memory usage > 75% during test runs → optimize test parallelism or add RAM.

### Disk Usage

| Path | Current | Limit | Action |
|------|---------|-------|--------|
| Repository (git objects) | ~500MB | 2GB | Archive old branches |
| Docker image cache | ~2GB | 5GB | Prune monthly |
| Quarto render output | ~100MB | 500MB | Clean on each deploy |
| pytest cache | ~50MB | 200MB | `pytest --cache-clear` |

---

## Monitoring Checkpoints

Until automated monitoring is in place (tracked in Issue #3055), use these
manual checkpoints:

### Weekly

- [ ] Review CI pass rate for the past 7 days.
- [ ] Check for Dependabot PRs needing review.
- [ ] Verify AffineDrift.com loads without errors.
- [ ] Check GitHub Actions runner status.

### Monthly

- [ ] Calculate error budget consumption.
- [ ] Review benchmark baseline drift.
- [ ] Run `pip-audit` on current requirements.
- [ ] Test rollback procedure (revert a deploy, verify site recovers).

### On-Demand (before major changes)

- [ ] Run full test suite locally.
- [ ] Run Quarto render locally.
- [ ] Run `npm audit` for JavaScript dependencies.

---

## Alerting Thresholds

Until PagerDuty/email alerting is configured (tracked in Issue #3055), use
GitHub's native notifications:

| Event | Notification method | Priority |
|-------|-------------------|---------|
| CI failure on main | GitHub email (auto) | High — fix within 4 hours |
| Dependabot security alert | GitHub email (auto) | High — patch within 24 hours |
| Deploy failure | GitHub email (auto) | Medium — fix within 8 hours |
| Runner offline | Check manually (weekly) | Medium |
| Coverage floor drop | CI failure (auto) | Low — next sprint |

---

## SLO Review Process

Review SLOs quarterly:

1. Calculate actual performance vs. targets for the quarter.
2. Adjust targets based on observed baseline.
3. Update error budget calculations.
4. Identify SLOs that are consistently unmet and create improvement issues.

---

## References

- `docs/operations/monitoring-setup.md` — monitoring configuration
- `docs/operations/incident-response-playbooks.md` — incident response
- `docs/operations/on-call-procedures.md` — on-call rotation
- `docs/development/benchmarking.md` — benchmark baseline policy
- [GitHub Pages SLA](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages)
