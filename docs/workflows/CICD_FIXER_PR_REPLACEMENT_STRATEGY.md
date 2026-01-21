# CI/CD Fixer: PR Replacement Strategy

**Status:** Recommended Implementation
**Document Version:** 1.0.0
**Created:** 2026-01-21
**Last Updated:** 2026-01-21

---

## Overview

This document outlines the recommended strategy for handling CI/CD failures in existing PRs without creating PR proliferation. The chosen approach is **Option C: PR Replacement Strategy** - create a new PR with fixes and auto-close the original PR while preserving context.

---

## Problem Statement

### Current Behavior

When CI fails on an existing PR, the control tower workflows can:
1. **Auto-Repair:** Push fixes directly to the branch (works for non-protected branches)
2. **Hotfix Creator:** Create a new `hotfix/*` branch and PR (creates PR proliferation)

### Issues with Current Approach

- Multiple PRs accumulate when fixes fail repeatedly
- Original PR context (comments, reviews, discussions) can be lost
- Confusion about which PR to review and merge
- Stale branches accumulate without cleanup

---

## Recommended Solution: PR Replacement Strategy

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    PR Replacement Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PR #42 (feature/my-change → main)                             │
│           │                                                     │
│           ▼                                                     │
│     CI Fails ❌                                                 │
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────┐                    │
│  │  1. Catalog PR #42 Context             │                    │
│  │     - Comments                         │                    │
│  │     - Reviews                          │                    │
│  │     - Discussion threads               │                    │
│  │     - Linked issues                    │                    │
│  │     - Commit history                   │                    │
│  └────────────────────────────────────────┘                    │
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────┐                    │
│  │  2. Create Fix Branch                  │                    │
│  │     jules/fix-pr-42-YYYYMMDD-HHMM     │                    │
│  │     - Cherry-pick all commits from #42 │                    │
│  │     - Apply CI/CD fixes               │                    │
│  │     - Run tests to verify             │                    │
│  └────────────────────────────────────────┘                    │
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────┐                    │
│  │  3. Create New PR #43                  │                    │
│  │     - Title: fix(ci): {original} [PR#42]│                   │
│  │     - Body: Links to original PR       │                    │
│  │     - Body: Context preservation note  │                    │
│  │     - Body: Link to archived context   │                    │
│  └────────────────────────────────────────┘                    │
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────┐                    │
│  │  4. Close Original PR #42              │                    │
│  │     - Comment: "Superseded by #43"     │                    │
│  │     - Link to new PR                   │                    │
│  │     - Link to archived context         │                    │
│  └────────────────────────────────────────┘                    │
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────┐                    │
│  │  5. Cleanup (Optional)                 │                    │
│  │     - Delete old branch                │                    │
│  │     - Archive context file committed   │                    │
│  └────────────────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Context Preservation:** All PR comments, reviews, and discussions are archived to a markdown file before closing
2. **Clear Lineage:** New PR explicitly references the original PR it replaces
3. **Single Active PR:** Only one PR exists for review at any time
4. **Clean History:** All original commits preserved plus fix commits
5. **Automated Cleanup:** Old branches deleted after successful replacement

---

## Context Preservation

### What Gets Archived

The workflow should capture and archive the following from the original PR:

```markdown
# Archived PR Context: #{original_pr_number}

## Original PR Details
- **Title:** {original_title}
- **Author:** {author}
- **Created:** {created_at}
- **Branch:** {head_branch} → {base_branch}
- **Closed:** {closed_at}
- **Superseded By:** #{new_pr_number}

## Commits
| SHA | Author | Message | Date |
|-----|--------|---------|------|
| abc123 | @user | feat: add feature | 2026-01-20 |
| def456 | @user | fix: address review | 2026-01-21 |

## Comments
### Comment by @reviewer at 2026-01-20 14:32
> This looks good but consider adding error handling for edge cases.

### Comment by @author at 2026-01-20 15:10
> Good point, I've added a try/catch block.

## Reviews
### Review by @reviewer - Changes Requested (2026-01-20)
**Status:** Changes Requested

**Comments:**
- `src/main.py:42` - Consider using logging instead of print
- `src/utils.py:15` - Missing type hint

### Review by @reviewer - Approved (2026-01-21)
**Status:** Approved

## Linked Issues
- Closes #123 - Add user authentication
- Related to #100 - Security improvements

## CI/CD Failure Details
- **Failed Run:** {workflow_run_url}
- **Failure Reason:** {failure_summary}
- **Fixed In:** #{new_pr_number}
```

### Archive Location

Archives should be stored at:
```
docs/pr-archives/pr-{number}-archive.md
```

This location:
- Is committed to the repository for permanent record
- Is easily searchable
- Maintains audit trail of all PR transitions

---

## Implementation Requirements

### Workflow Changes Needed

1. **Add PR Context Cataloger Step**
   - Fetch all PR comments via GitHub API
   - Fetch all reviews and review comments
   - Extract linked issues from PR body
   - Capture commit history
   - Generate markdown archive file

2. **Add PR Replacement Logic**
   - Create new branch from main
   - Cherry-pick commits from original PR
   - Apply CI/CD fixes
   - Create new PR with proper naming (see naming conventions)

3. **Add Original PR Closure**
   - Add comment linking to new PR
   - Add comment linking to archive
   - Close PR via API
   - Optionally delete branch

4. **Add Cleanup Automation**
   - Delete stale branches after 7 days
   - Remove branches whose PRs are closed

### Required Permissions

```yaml
permissions:
  contents: write        # Create branches, commit archives
  pull-requests: write   # Create/close PRs, add comments
  issues: write          # Update linked issues
```

### API Calls Required

```bash
# Fetch PR details
gh pr view {pr_number} --json title,body,author,createdAt,headRefName,baseRefName,commits,comments,reviews

# Fetch PR comments
gh api repos/{owner}/{repo}/issues/{pr_number}/comments

# Fetch PR review comments
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments

# Fetch PR reviews
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews

# Close original PR
gh pr close {pr_number} --comment "Superseded by #{new_pr_number}"

# Delete branch
gh api -X DELETE repos/{owner}/{repo}/git/refs/heads/{branch_name}
```

---

## New PR Body Template

```markdown
## CI/CD Fix: Replaces PR #{original_pr_number}

This PR supersedes #{original_pr_number} which failed CI/CD checks.

### Original PR
- **Title:** {original_title}
- **Author:** @{original_author}
- **Branch:** `{original_branch}`

### What Changed
- All commits from #{original_pr_number} are preserved
- Added CI/CD fixes:
  - {fix_description_1}
  - {fix_description_2}

### Context Preserved
The original PR's comments, reviews, and discussions have been archived:
- [PR #{original_pr_number} Archive](../docs/pr-archives/pr-{original_pr_number}-archive.md)

### CI/CD Failure Fixed
- **Failed Run:** {workflow_run_url}
- **Root Cause:** {failure_reason}
- **Fix Applied:** {fix_summary}

### Review Notes
- Please review the CI/CD fix commits (marked with `fix(ci):` prefix)
- Original code changes were previously reviewed in #{original_pr_number}
- Check the archive for any unresolved review comments

---

Closes #{original_pr_number}
{linked_issues}
```

---

## Error Handling

### Scenario: Cherry-Pick Conflicts

If cherry-picking commits causes conflicts:
1. Log the conflict details
2. Create PR with conflict markers
3. Add label `needs-manual-resolution`
4. Comment on PR explaining the conflict
5. Do NOT close the original PR until resolved

### Scenario: Original PR Already Merged

If the original PR was merged while the workflow runs:
1. Abort the replacement process
2. Log that PR was merged
3. No cleanup needed

### Scenario: Original PR Closed by User

If the user closed the original PR:
1. Check if it was closed without merging
2. If so, still proceed with fix PR
3. Update archive to note manual closure

---

## Rollback Procedure

If the replacement PR introduces issues:

1. **Revert the replacement PR:**
   ```bash
   gh pr revert {new_pr_number}
   ```

2. **Reopen original PR:**
   ```bash
   gh pr reopen {original_pr_number}
   ```

3. **Add comment explaining rollback:**
   ```bash
   gh pr comment {original_pr_number} --body "Reopened after rollback of #{new_pr_number}"
   ```

---

## Success Criteria

The implementation is successful when:

- [ ] Original PR context is fully archived before closure
- [ ] New PR clearly references the original PR
- [ ] All original commits are preserved
- [ ] CI/CD fixes are applied and passing
- [ ] Original PR is closed with clear supersession message
- [ ] No orphaned branches remain
- [ ] Archive is committed and searchable

---

## Future Enhancements

1. **Smart Merge Strategy:** Detect if simple rebase is sufficient vs. full replacement
2. **Review Transfer:** Automatically request reviews from original reviewers
3. **Label Preservation:** Copy labels from original PR to new PR
4. **Metrics Dashboard:** Track replacement success rates
5. **Notification System:** Alert original author about PR replacement

---

## Related Documents

- [PR Naming Conventions](./PR_NAMING_CONVENTIONS.md)
- [Assessment Remediation Guide](./ASSESSMENT_REMEDIATION_GUIDE.md)
- [Control Tower Overview](../../.github/workflows/Jules-Control-Tower.yml)

---

**Maintained By:** AffineDrift Team
**Document Owner:** DevOps
