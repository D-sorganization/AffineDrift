# Branch Protection Configuration for `main`

This file documents the required branch protection settings for the `main` branch.
These settings should be configured via GitHub Settings > Branches > Branch protection rules.

## Settings to Enable

### Apply to main branch

- **Require status checks to pass before merging**: ✓ Enabled

  - Require branches to be up to date before merging: ✓ Enabled
  - Status checks required:
    - `ci-standard.yml` (linting, tests, coverage)
    - Any other critical CI workflows

- **Require code reviews before merging**: ✓ Enabled

  - Number of approvals required: 1 (minimum)
  - Dismiss stale pull request approvals: ✓ Enabled
  - Require approval of most recent reviewable push: ✓ Enabled
  - Require review from code owners: (optional) ✓ Enabled if CODEOWNERS exists

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
   - Cannot merge without required reviews
   - Cannot self-approve own PR (if code owner requirement enabled)
   - Cannot force push to main

## Related Issues

- #2912: Enable branch protection on main branch
- #2918: Enforce distributed code reviews and block self-merges

## Code Review Policy

Until a CODEOWNERS file exists, require reviews from:

- At least one maintainer or senior developer
- Different person than PR author (self-merges blocked by settings)

## References

- [GitHub: Managing a branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [GitHub: Setting up branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
