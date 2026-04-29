# Branch Protection Rules for `main`

This document describes the branch protection rules enforced on the `main` branch of AffineDrift to ensure code quality, security, and process integrity.

## Rules

### Pull Request Requirements

- **Require a pull request before merging**: All changes to `main` must go through a pull request.
- **Required approving reviews**: At least 1 approval from a reviewer other than the PR author is required.
- **Dismiss stale pull request reviews**: Old reviews are automatically dismissed when new commits are pushed after approval.

### Status Checks

The following GitHub Actions workflow must pass before merge:

- **CI Standard** (`CI Standard`): Comprehensive quality gates including:
  - Python linting (Ruff)
  - Code formatting check (Black)
  - Type checking (mypy)
  - Test coverage (pytest with 50%+ minimum)
  - JavaScript tests (Jest)
  - E2E tests (Playwright)
  - HTML/CSS validation
  - Custom quality checks (CSS budget, DRY adoption, module size, etc.)

See `.github/workflows/ci-standard.yml` for the full CI/CD pipeline.

### Admin Enforcement

- **Enforce for administrators**: Branch protection rules apply to repository administrators as well, ensuring consistent enforcement.

### Force Pushes

- **Allow force pushes**: Disabled — force pushes to `main` are not allowed.

### Deletions

- **Allow deletions**: Disabled — the `main` branch cannot be deleted.

## Rationale

These rules enforce the contributing policies documented in `CONTRIBUTING.md`:

1. **Code Review** — At least one independent reviewer must approve all changes
2. **Status Checks** — All automated quality gates must pass
3. **Stale Review Dismissal** — Reviews are re-evaluated when material changes are pushed
4. **Admin Accountability** — No exceptions for administrators; all rules apply uniformly

## Manual Bypass (Emergency Only)

If an emergency bypass is required (e.g., critical security hotfix):

1. Repository administrator can temporarily disable branch protection via GitHub UI
2. Document the reason and timeline in the commit message
3. Re-enable protection immediately after merge
4. Post-mortem: discuss with team why normal process couldn't be followed

## Related Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines and review policy (lines 275-290)
- **[.github/workflows/ci-standard.yml](.github/workflows/ci-standard.yml)** — CI/CD pipeline configuration

## Enabling Branch Protection

To enable or update these rules programmatically:

```bash
# Enable branch protection using gh CLI
gh api repos/OWNER/REPO/branches/main/protection \
  --method PUT \
  --input branch_protection_config.json
```

Configuration JSON structure:
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI Standard"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "restrictions": null
}
```

## Verification

To verify current branch protection settings:

```bash
gh api repos/OWNER/REPO/branches/main/protection
```

Expected key settings:
- `required_pull_request_reviews.required_approving_review_count` = 1
- `required_pull_request_reviews.dismiss_stale_reviews` = true
- `required_status_checks.strict` = true
- `required_status_checks.contexts` includes "CI Standard"
- `enforce_admins.enabled` = true
- `allow_force_pushes.enabled` = false
- `allow_deletions.enabled` = false
