# Branch Protection Configuration for `main`

This file documents the required branch protection settings for the `main` branch.
These settings should be configured via GitHub Settings > Branches > Branch protection rules.

## Current API-Observed Contract

The active repository `Protect Main` ruleset was read through the GitHub API on
2026-08-25. It requires a pull request and blocks deletion and non-fast-forward
updates. Its approval count is deliberately zero; it does not require code-owner,
last-push, stale-review, or named-reviewer approval. Organization rules and
required status checks remain additive. Do not treat a named maintainer review
as a standing release gate.

## Settings to Enable

### Apply to main branch

- **Require status checks to pass before merging**: ✓ Enabled

  - Require branches to be up to date before merging: ✓ Enabled
  - Status checks required:
    - `ci-standard.yml` (linting, tests, coverage)
    - Any other critical CI workflows

- **Require a pull request before merging**: ✓ Enabled

  - Number of approvals required: 0
  - Named maintainer approval: not required
  - Optional reviews may be requested for risk, expertise, or unresolved feedback

- **Require status checks from required contexts**:

  - Allow dismissal: ✓ Restricted to administrators
  - Require branches to be up to date before merging: ✓ Enabled

- **Restrict who can push to matching branches**: ✓ Enabled

  - Allow: administrators only (or appropriate team)

- **Require conversation resolution before merging**: ✓ Enabled

- **Require signed commits**: (optional) ✓ Enabled for production-ready repos

- **Require branches to be up to date before merging**: ✓ Enabled

### Do NOT Allow

- ✗ Bypass pull request requirements for administrators
- ✗ Force pushes to main
- ✗ Deletion of main branch

## Implementation Steps

1. Go to: https://github.com/D-sorganization/AffineDrift/settings/branches
2. Click "Add rule" or edit existing "main" rule
3. Enter branch name pattern: `main`
4. Enable all settings listed in "Settings to Enable" above
5. Click "Create" or "Save changes"

## Verification

After enabling, test with a PR:

1. Create feature branch from main
2. Make a commit
3. Push and open PR
4. Verify:
   - Status checks must pass before merge button appears
   - Required status checks must pass
   - No named maintainer approval is requested when the live approval count is zero
   - Cannot force push to main

## Related Issues

- #2912: Enable branch protection on main branch
- #2918: Historical distributed-review enforcement proposal; live zero-approval policy supersedes its review-count target

## Code Review Policy

Review is optional and risk-driven. A reviewer may be requested for specialized
ownership, security, or unresolved design feedback, but no individual—including
`@dieterolson`—is a standing release dependency. Required CI and normal protected
merge behavior remain mandatory.

## References

- [GitHub: Managing a branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [GitHub: Setting up branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
