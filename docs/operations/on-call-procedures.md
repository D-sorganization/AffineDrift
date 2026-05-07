# On-Call Procedures & Runbooks

Procedures for responding to infrastructure issues in the AffineDrift repository.

> **Context**: AffineDrift is a personal research repository maintained by a
> single owner. "On-call" here means the owner's responsibilities for keeping
> CI, deployment, and content integrity working. There is no pager rotation.

---

## Response SLAs

| Alert type | Detection | Response SLA | Resolution SLA |
|-----------|----------|-------------|---------------|
| CI failed on main | GitHub notification | 4 hours (business hours) | 24 hours |
| Deploy failure (site down) | GitHub notification | 4 hours | 8 hours |
| Security vulnerability (Dependabot) | GitHub notification | 24 hours | 72 hours |
| Flaky test | Manual (weekly review) | 1 week | 2 weeks |
| Runner offline | Manual check | Next business day | 48 hours |

---

## Routine Checks

### Daily (< 5 minutes)

- [ ] Check GitHub notification inbox for CI failures or Dependabot alerts.

### Weekly (< 15 minutes)

- [ ] Review CI pass rate for the past 7 days (GitHub Actions tab).
- [ ] Check for open Dependabot PRs — merge if tests pass.
- [ ] Verify AffineDrift.com loads correctly.
- [ ] Check self-hosted runner status.

```bash
# Quick status check
gh run list --repo d-sorganization/AffineDrift --limit 10
gh pr list --repo d-sorganization/AffineDrift
gh api repos/d-sorganization/AffineDrift/actions/runners | \
  python -c "import json,sys; [print(r['name'], r['status']) for r in json.load(sys.stdin)['runners']]"
```

### Monthly (< 30 minutes)

- [ ] Calculate error budget consumption (see `docs/operations/slo-targets.md`).
- [ ] Run `pip-audit --requirement requirements.txt` manually.
- [ ] Run `npm audit` manually.
- [ ] Review and close resolved GitHub issues.
- [ ] Update `CHANGELOG.md` with completed work.
- [ ] Archive stale branches older than 90 days.

```bash
# Find stale branches (not merged, last commit > 90 days ago)
git for-each-ref --sort=committerdate refs/remotes/origin \
  --format='%(committerdate:short) %(refname:short)' | \
  awk -v cutoff="$(date -d '90 days ago' +%Y-%m-%d)" '$1 < cutoff'
```

---

## Alert Response Procedures

### GitHub Notification: CI Failed

1. **Open the failing run**: click the notification link or:
   ```bash
   gh run list --repo d-sorganization/AffineDrift --limit 5
   gh run view <run_id> --log-failed 2>&1 | tail -100
   ```

2. **Classify the failure** using the table in
   [PB-001](incident-response-playbooks.md#pb-001-ci-pipeline-failure).

3. **Check if main is broken** (not just the PR):
   ```bash
   gh run list --repo d-sorganization/AffineDrift --branch main --limit 5
   ```

4. **Fix and push**. Target resolution within the SLA window.

---

### GitHub Notification: Dependabot Security Alert

1. Open the Dependabot alert from the notification.
2. Read the CVE description and severity.
3. Check if the vulnerable code path is exercised in AffineDrift:
   - High/Critical → patch within 24 hours.
   - Medium → patch within 72 hours.
   - Low → next sprint.
4. Merge the Dependabot PR if CI passes, or apply a manual fix.
5. Close the alert after the fix is merged.

---

### GitHub Notification: Deploy Failed

Deploy failures appear as failed `deploy-website.yml` runs.

1. Check deploy logs:
   ```bash
   gh run list --repo d-sorganization/AffineDrift --workflow deploy-website.yml --limit 5
   gh run view <run_id> --log-failed
   ```

2. Common causes:
   - Quarto render failure (see [PB-003](incident-response-playbooks.md#pb-003-quarto-build-failure)).
   - GitHub Pages quota exceeded (rare).
   - Authentication failure for Pages deployment.

3. The site remains on the previous deploy until a successful redeploy.

---

### Runner Offline

1. Check runner status:
   ```bash
   gh api repos/d-sorganization/AffineDrift/actions/runners
   ```

2. If offline: restart the runner service on the host machine.
   See [PB-002](incident-response-playbooks.md#pb-002-runner-outage).

3. If machine is unreachable: follow the re-registration procedure in PB-002.

---

## Escalation Decision Tree

```
Alert received
    │
    ├─ Site down (AffineDrift.com returns 5xx)?
    │      └─ Yes → Deploy failure path → PB-003
    │
    ├─ CI failing on main?
    │      └─ Yes → High priority → fix within 4 hours
    │
    ├─ CI failing only on PRs?
    │      └─ Yes → Medium priority → fix before merging the PR
    │
    ├─ Security alert (Dependabot)?
    │      ├─ Critical/High → 24-hour response
    │      └─ Medium/Low → next sprint
    │
    └─ Flaky tests?
           └─ Track in issue → fix within 2 weeks
```

---

## Communication Templates

### For GitHub Issues (public)

When filing an issue for an incident:

```markdown
## Incident Report — [Brief Title]

**Date:** YYYY-MM-DD
**Duration:** X hours
**Impact:** CI blocked / Site unavailable / Deploys failing

### What happened

[One paragraph description]

### Resolution

[What was done to fix it]

### Prevention

- [ ] [Action item]
```

### PR Description for Incident Fix

```markdown
## Summary

Fixes [describe the incident] that caused [impact].

## Root Cause

[Brief root cause description]

## Changes

- `file.py`: [What changed and why]

## Testing

- [ ] Reproduces locally before fix
- [ ] Does not reproduce after fix
- [ ] All CI checks pass

Closes #<incident-issue>
```

---

## Runbooks

### Runbook: Add a New Self-Hosted Runner

1. Go to GitHub > Repository > Settings > Actions > Runners > New self-hosted runner.
2. Select OS: Linux.
3. Follow the displayed registration steps on the target machine.
4. Start the runner:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```
5. Verify it appears online:
   ```bash
   gh api repos/d-sorganization/AffineDrift/actions/runners
   ```
6. Tag the runner with `d-sorg-fleet` label to match CI workflow routing.

---

### Runbook: Purge Stale Branches

```bash
# Dry-run: show branches that would be deleted
git fetch --all --prune

# For merged branches only:
git branch -r --merged origin/main | \
  grep -v "origin/main" | \
  grep -v "origin/HEAD" | \
  sed 's|origin/||' | \
  xargs -n 1 echo "Would delete: "

# Actually delete (requires confirmation per branch):
git branch -r --merged origin/main | \
  grep -v "origin/main" | \
  grep -v "origin/HEAD" | \
  sed 's|origin/||' | \
  xargs -n 1 git push origin --delete
```

---

### Runbook: Emergency Content Rollback

If a bad article or broken content was deployed:

```bash
# Find the last good deploy commit
gh run list --workflow deploy-website.yml --json conclusion,headSha,createdAt | \
  python -c "import json,sys; runs=json.load(sys.stdin); [print(r['headSha'][:8], r['conclusion'], r['createdAt']) for r in runs]"

# Revert to the last good commit (creates a revert PR)
git revert <bad-commit-sha>
git push origin main
```

GitHub Pages will redeploy automatically from the new main commit.

---

### Runbook: Rotate a Compromised Credential

If a secret is believed to be compromised:

1. **Immediately revoke** the credential at the source (GitHub, API provider).
2. Generate a new credential.
3. Update the GitHub repository secret:
   - Settings > Secrets and variables > Actions > Update.
4. Verify CI passes with the new credential.
5. If the credential was committed to git history:
   ```bash
   # Use git filter-repo to purge from history
   pip install git-filter-repo
   git filter-repo --path-glob '*.env' --invert-paths
   git push --force origin main
   ```
   Note: This rewrites history. Coordinate with all contributors before doing this.

---

## References

- `docs/operations/incident-response-playbooks.md` — detailed playbooks
- `docs/operations/slo-targets.md` — SLO definitions and error budgets
- `docs/operations/troubleshooting-guide.md` — error lookup
- `docs/development/security-guidelines.md` — security policies
- [GitHub Pages status](https://www.githubstatus.com/)
- [GitHub Actions billing](https://github.com/settings/billing/summary)
