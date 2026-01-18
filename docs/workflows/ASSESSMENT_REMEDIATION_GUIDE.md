# Assessment Remediation Workflow Guide

**Workflow:** Jules Assessment Remediator
**File:** `.github/workflows/Jules-Assessment-Remediator.yml`
**Status:** Production Ready
**Last Updated:** 2026-01-17

---

## Overview

The Jules Assessment Remediator is an automated workflow that identifies and fixes issues discovered during project assessments. It processes assessment-labeled GitHub issues, applies safe automated fixes, and creates pull requests for review.

### Purpose

- Automatically remediate common code quality issues identified in assessments
- Reduce manual toil for repetitive fixes (docstrings, type hints, formatting)
- Maintain consistent code quality standards
- Accelerate resolution of assessment-identified technical debt

### Key Features

- Intelligent issue selection based on priority and age
- Safe, mechanical code transformations
- Comprehensive testing before PR creation
- Dry-run mode for preview
- Automatic rollback on failures
- Integration with existing Jules agents

---

## How It Works

### Workflow Stages

#### 1. Issue Selection Phase
The workflow fetches and filters GitHub issues based on:
- **Labels:** Issues must have the `assessment` label
- **Status:** Only open issues are considered
- **Priority:** Filters by P0 (critical) and/or P1 (high) priority
- **Ranking:** P0 issues processed first, then P1, sorted by age (oldest first)
- **Limit:** Configurable maximum (1-10 issues per run, default: 5)

#### 2. Analysis Phase
For each selected issue:
- Extract issue body and metadata
- Parse remediation steps from issue description
- Identify affected files from evidence sections
- Check for dependencies between issues
- Build comprehensive context for fixes

#### 3. Remediation Phase
Apply automated fixes using Jules AI:
- **Docstrings:** Add Google-style docstrings to undocumented functions/classes
- **Type Hints:** Add type annotations to function signatures
- **Logging:** Convert print() statements to proper logging calls
- **Formatting:** Apply black, isort, and ruff formatters
- **Documentation:** Create missing README files
- **Environment:** Update .env.example with missing variables
- **Alt Text:** Add descriptive alt text to images

#### 4. Testing Phase
Verify changes don't break functionality:
- Run code formatters (black, isort, ruff)
- Execute linters and report results
- Run test suite if tests exist
- Generate quality reports

#### 5. PR Creation Phase
Package changes for review:
- Create feature branch: `auto-fix/assessment-remediation-{timestamp}`
- Commit changes with descriptive messages
- Generate PR with comprehensive description
- Add labels: `automated`, `assessment-fix`, `needs-review`
- Request review from repository owner
- Comment on all affected issues with PR link

#### 6. Reporting Phase
Document the remediation:
- Post summary to workflow run
- Comment on individual issues
- Generate metrics report
- Track success/failure rates

---

## Usage

### Manual Trigger (Recommended for First Run)

1. Navigate to **Actions** > **Jules Assessment Remediator**
2. Click **Run workflow**
3. Configure inputs:
   - **Number of issues:** 1-10 (default: 5)
   - **Priority filter:** P0, P1, or both (default: both)
   - **Dry run:** true/false (default: false)
4. Click **Run workflow**

#### Dry Run Mode

Always test with dry-run first:

```yaml
inputs:
  issue_count: '3'
  priority_filter: 'both'
  dry_run: true
```

Review the logs to see what would be changed before running in production mode.

### Scheduled Execution

The workflow runs automatically:
- **Schedule:** Weekly on Monday at 9:00 AM UTC
- **Default Settings:** 5 issues, both priorities, production mode

To modify the schedule, edit the cron expression in the workflow file:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Monday 9am UTC
```

### GitHub CLI

Trigger from command line:

```bash
# Dry run - preview changes
gh workflow run Jules-Assessment-Remediator.yml \
  -f issue_count=5 \
  -f priority_filter=both \
  -f dry_run=true

# Production run
gh workflow run Jules-Assessment-Remediator.yml \
  -f issue_count=5 \
  -f priority_filter=P0 \
  -f dry_run=false
```

---

## Configuration

### Input Parameters

| Parameter | Type | Options | Default | Description |
|-----------|------|---------|---------|-------------|
| `issue_count` | choice | 1-10 | 5 | Number of issues to remediate |
| `priority_filter` | choice | P0, P1, both | both | Which priority levels to include |
| `dry_run` | boolean | true/false | false | Preview mode without creating PR |

### Environment Variables

Set in workflow or repository secrets:

- `JULES_API_KEY`: API key for Jules AI (required)
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `MAX_ISSUES_PER_RUN`: Safety limit (default: 10)
- `DEFAULT_ISSUE_COUNT`: Default when not specified (default: 5)

### Required Secrets

Configure in **Settings** > **Secrets and variables** > **Actions**:

1. `JULES_API_KEY`: Your Jules API key
   - Obtain from: https://jules.google.com/
   - Scope: Full access for code analysis and modification

---

## Issue Requirements

For the workflow to process an issue, it must meet these criteria:

### Required Labels

- **Primary:** `assessment` (marks issue as assessment-identified)
- **Priority:** `priority: critical` (P0) or `priority: high` (P1)

### Recommended Issue Structure

```markdown
## Issue Title
Brief description of the problem

## Priority
P0 (Critical) or P1 (High)

## Category
Code Quality / Documentation / Testing / Repository Hygiene

## Problem Description
Detailed explanation of what's wrong

## Evidence
File: `path/to/file.py`
Lines: 45-67
[Code snippet or description]

## Remediation Steps
1. Specific action to take
2. Another action
3. Expected outcome

## Impact
Description of how this affects the project

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Example Issues

**Issue #123: Missing Docstrings in Core Modules**
```markdown
Labels: assessment, priority: critical

## Problem
Core modules lack docstrings, making the codebase hard to understand.

## Evidence
File: `src/core/processor.py`
- 15 functions without docstrings
- 3 classes without class-level documentation

## Remediation
Add Google-style docstrings to all public functions and classes.

## Impact
Affects developer onboarding and code maintainability.
```

**Issue #124: Print Statements Instead of Logging**
```markdown
Labels: assessment, priority: high

## Problem
Code uses print() for output instead of proper logging.

## Evidence
File: `src/utils/helpers.py`
Lines: 12, 34, 67, 89

## Remediation
Replace print() with logging.info/warning/error as appropriate.

## Impact
Difficult to control output in production; no log levels.
```

---

## Automated Fixes

### What Gets Fixed Automatically

#### Safe Transformations (Always Applied)

1. **Missing Docstrings**
   - Adds Google-style docstrings to functions and classes
   - Includes: Description, Args, Returns, Raises sections
   - Uses code context to infer documentation

2. **Print to Logging**
   - Converts `print(msg)` to `logging.info(msg)`
   - Imports logging module if needed
   - Preserves message formatting and variables

3. **Type Hints**
   - Adds type annotations to function signatures
   - Uses standard library types (str, int, List, Dict, Optional)
   - Imports from typing module as needed

4. **Code Formatting**
   - Runs black for consistent style
   - Applies isort for import ordering
   - Executes ruff for auto-fixable linting errors

5. **Missing READMEs**
   - Creates README.md from template
   - Includes: Title, Description, Usage, Installation
   - Auto-generates from directory structure

6. **Environment Files**
   - Updates .env.example with missing variables
   - Adds placeholder values (never real secrets)
   - Documents each variable with comments

7. **Image Alt Text**
   - Adds descriptive alt text to images
   - Extracts context from filename and surrounding code
   - Uses placeholders like "Diagram of [topic]"

#### Example Transformations

**Before:**
```python
def calculate_total(items):
    print(f"Processing {len(items)} items")
    total = sum(item.price for item in items)
    print(f"Total: {total}")
    return total
```

**After:**
```python
import logging

def calculate_total(items: List[Item]) -> float:
    """Calculate the total price of items.

    Args:
        items: List of items to sum.

    Returns:
        The total price as a float.
    """
    logging.info(f"Processing {len(items)} items")
    total = sum(item.price for item in items)
    logging.info(f"Total: {total}")
    return total
```

### What Requires Manual Intervention

The workflow documents but does not fix:

- **Architectural Changes:** Require design decisions
- **Complex Refactoring:** Spans multiple modules
- **Domain Logic:** Needs business knowledge
- **Breaking Changes:** Impact public APIs
- **Performance:** Require benchmarking
- **Security:** Need security review

These are listed in the PR description under "Manual Steps Required."

---

## Pull Request Review

### Review Checklist

When reviewing an automated remediation PR:

#### 1. Correctness Verification
- [ ] Docstrings accurately describe function behavior
- [ ] Type hints match actual function signatures
- [ ] Logging conversions preserve original functionality
- [ ] README content is accurate and helpful

#### 2. Safety Checks
- [ ] No business logic was altered
- [ ] No test assertions were modified
- [ ] No functionality was removed
- [ ] No breaking changes to public APIs
- [ ] All existing comments are preserved

#### 3. Quality Assessment
- [ ] All tests pass (check CI status)
- [ ] Linting errors addressed or justified
- [ ] Code formatting is consistent
- [ ] No unintended side effects

#### 4. Documentation Quality
- [ ] Docstrings follow Google-style guide
- [ ] READMEs include all necessary sections
- [ ] Environment variables properly documented
- [ ] Examples are clear and runnable

### Common Issues and Resolutions

| Issue | Resolution |
|-------|------------|
| Incorrect docstring | Edit the docstring directly in the PR |
| Wrong type hint | Correct the type annotation |
| Logging level incorrect | Change logging.info to appropriate level |
| README too generic | Add specific details manually |
| Missing context | Add comments or additional documentation |

### Approval Process

1. **Automated Checks:** Verify all CI checks pass
2. **Code Review:** Review changes for correctness
3. **Test Validation:** Ensure tests cover new documentation
4. **Manual Testing:** Spot-check a few changes manually
5. **Approval:** Approve and merge when satisfied

### After Merge

1. **Verify Closure:** Ensure linked issues auto-close
2. **Monitor:** Watch for any unexpected behavior
3. **Update Assessment:** Reflect improvements in assessment reports
4. **Schedule Next Run:** Plan follow-up remediation if needed

---

## Integration with Other Workflows

### Jules Control Tower

The Assessment Remediator integrates with the Control Tower but is not automatically triggered. Manual or scheduled execution only.

### Jules Documentation Scribe

- Scribe handles docstring updates on push
- Remediator handles bulk docstring additions
- Both can run independently without conflict

### Jules Test Generator

- Test Generator creates tests for new code
- Remediator runs existing tests to validate changes
- Coordinate: Run Test Generator after Remediator for coverage

### Jules Auto-Repair

- Auto-Repair fixes CI failures
- Remediator fixes assessment issues
- Different triggers and scopes, no overlap

---

## Best Practices

### Issue Management

1. **Label Consistently:** Always use `assessment` + priority labels
2. **Be Specific:** Include file paths and line numbers in evidence
3. **Provide Context:** Explain why the issue matters
4. **Link Related Issues:** Reference dependencies between issues
5. **Track Progress:** Update issues as fixes are applied

### Workflow Execution

1. **Start Small:** Run with 1-3 issues first time
2. **Use Dry Run:** Always preview changes before production run
3. **Review Carefully:** Automated fixes need human verification
4. **Merge Promptly:** Don't let PRs sit; review within 24-48 hours
5. **Monitor Impact:** Watch metrics before/after remediation

### PR Review

1. **Check Context:** Review original issues for background
2. **Spot Check:** Manually verify a sample of changes
3. **Run Locally:** Test changes on your machine if unsure
4. **Provide Feedback:** Comment on specific lines if corrections needed
5. **Approve Quickly:** Don't block on minor style preferences

### Maintenance

1. **Regular Runs:** Schedule weekly to prevent backlog
2. **Prioritize P0:** Focus on critical issues first
3. **Update Templates:** Improve PR template based on feedback
4. **Tune Prompts:** Refine Jules prompts for better results
5. **Track Metrics:** Monitor fix success rates and adjust

---

## Troubleshooting

### Workflow Fails to Find Issues

**Symptoms:** No issues selected, workflow exits early

**Causes:**
- No issues with `assessment` label
- No issues with required priority labels
- All issues already closed

**Solutions:**
1. Check issue labels in GitHub Issues
2. Verify issues are open
3. Ensure priority labels are correct (case-sensitive)
4. Run `gh issue list --label assessment` to verify

### Jules Fails to Apply Fixes

**Symptoms:** Remediation phase fails, no commits made

**Causes:**
- Jules API key invalid or expired
- Prompt too complex or ambiguous
- Files locked or permission issues

**Solutions:**
1. Verify `JULES_API_KEY` secret is set correctly
2. Check workflow logs for specific error
3. Simplify by reducing issue count
4. Ensure repository permissions allow bot access

### Tests Fail After Remediation

**Symptoms:** PR created but CI checks fail

**Causes:**
- Automated fixes introduced bugs
- Type hints incompatible with test mocks
- Imports added but dependencies missing

**Solutions:**
1. Review failed tests in CI logs
2. Check if type hints conflict with test doubles
3. Manually fix issues in the PR branch
4. Push additional commits to the PR branch
5. Consider reverting specific changes if needed

### PR Not Created

**Symptoms:** Fixes applied but no PR appears

**Causes:**
- No changes made by Jules (all issues already fixed)
- Git push failed due to permissions
- PR creation failed due to API rate limits

**Solutions:**
1. Check workflow logs for git/gh errors
2. Verify bot has write permissions to repository
3. Ensure not hitting GitHub API rate limits
4. Check if branch exists but PR creation failed

### Rollback Needed

**Symptoms:** PR merged but introduced issues

**Solutions:**
1. Revert the PR: `gh pr revert [PR-NUMBER]`
2. Create fix in new PR
3. Update workflow prompts to prevent recurrence
4. Adjust issue descriptions for clarity

---

## Metrics and Monitoring

### Key Metrics

Track these metrics to assess workflow effectiveness:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Issues Remediated/Week | 5-10 | Count closed issues with `assessment-fix` label |
| Fix Accuracy | >90% | PR approval rate without requested changes |
| Time to Review | <2 days | Time from PR creation to merge |
| Test Pass Rate | 100% | CI checks pass on first try |
| Manual Steps Needed | <20% | Ratio of manual vs automated fixes |

### Monitoring Dashboard

Create a dashboard to track:

1. **Weekly Remediation Count:** Issues closed by workflow
2. **PR Merge Time:** Average time from creation to merge
3. **Fix Success Rate:** PRs merged without changes requested
4. **Issue Backlog:** Open assessment issues by priority
5. **Coverage Trend:** Code coverage improvements over time

### Reporting

Generate weekly reports:

```markdown
## Assessment Remediation Report - Week of [DATE]

### Summary
- Issues Remediated: X
- PRs Created: Y
- PRs Merged: Z
- Average Merge Time: N days

### Top Fixes Applied
1. Added docstrings to X functions
2. Converted Y print statements to logging
3. Added type hints to Z functions
4. Created N README files

### Manual Steps Pending
- Issue #XXX: Refactor module architecture
- Issue #YYY: Performance optimization needed

### Recommendations
- [Action items based on this week's data]
```

---

## Advanced Usage

### Custom Remediation Prompts

Modify the prompt in the workflow file to customize behavior:

```yaml
- name: Apply Automated Fixes
  env:
    CUSTOM_PROMPT: |
      Focus on [specific area].
      Use [specific style].
      Prioritize [specific type of fix].
```

### Priority Customization

Adjust issue selection logic:

```bash
# Prioritize by impact, not just priority label
ISSUES=$(gh issue list \
  --label assessment \
  --json number,title,labels,reactions \
  --jq 'sort_by(.reactions."+1") | reverse')
```

### Integration with External Tools

Connect to other systems:

```yaml
- name: Notify Slack
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{"text":"Assessment remediation complete: ${{ steps.pr.outputs.url }}"}'
```

### Batch Processing

Process issues in batches:

```bash
# Run workflow 3 times with different priorities
for priority in P0 P1 P2; do
  gh workflow run Jules-Assessment-Remediator.yml \
    -f priority_filter=$priority \
    -f issue_count=5
  sleep 300  # Wait 5 minutes between runs
done
```

---

## Security Considerations

### Secrets Management

- **Never commit secrets:** .env files should only have placeholders
- **Use GitHub Secrets:** Store API keys in repository secrets
- **Rotate regularly:** Update JULES_API_KEY every 90 days
- **Limit scope:** Jules key should have minimum required permissions

### Code Review Requirements

- **Always review:** Never auto-merge remediation PRs
- **Two-person rule:** Consider requiring 2 reviewers for P0 fixes
- **Check dependencies:** Review any new imports or dependencies
- **Verify tests:** Ensure test coverage hasn't decreased

### Branch Protection

Ensure main branch has:
- Require PR reviews before merging
- Require status checks to pass
- Require branches to be up to date
- No force pushes allowed

---

## FAQ

### Q: Can I run this on private repositories?

**A:** Yes, the workflow works with private repos. Ensure your Jules API key has access to private repositories if using Jules Cloud.

### Q: What if Jules makes incorrect changes?

**A:** Review the PR carefully. You can:
- Request changes and ask Jules to fix (push to PR branch)
- Make manual corrections in the PR
- Close the PR and adjust the workflow prompts

### Q: Can I customize which fixes are applied?

**A:** Yes, modify the remediation prompt in the workflow file to focus on specific types of fixes.

### Q: How do I prevent certain files from being modified?

**A:** Add file exclusions to the Jules prompt:
```
Exclude files matching: tests/*, vendor/*, generated/*
```

### Q: Can I run this on a specific directory only?

**A:** Yes, modify the workflow to scope to specific paths:
```yaml
env:
  TARGET_PATH: 'src/core'
```

### Q: What's the cost of running this workflow?

**A:** Costs include:
- GitHub Actions minutes (free tier: 2000 min/month)
- Jules API usage (check Jules pricing)
- Minimal compute for linting/testing

### Q: How often should I run remediation?

**A:** Recommended: Weekly for active projects, bi-weekly for stable projects.

### Q: Can I revert changes after merging?

**A:** Yes, use `gh pr revert [PR-NUMBER]` to create a revert PR.

---

## Changelog

### v1.0.0 (2026-01-17)
- Initial release
- Support for docstrings, type hints, logging, formatting
- Dry-run mode
- Integration with Jules Control Tower
- Comprehensive testing and reporting

---

## Support and Feedback

### Getting Help

1. **Documentation:** This guide and workflow comments
2. **Workflow Logs:** Check Actions tab for detailed logs
3. **Issue Tracker:** Report bugs in repository issues
4. **Community:** Discuss in repository discussions

### Reporting Issues

When reporting workflow issues, include:
- Workflow run URL
- Input parameters used
- Error messages from logs
- Expected vs actual behavior

### Feature Requests

Submit feature requests with:
- Use case description
- Expected behavior
- Impact on workflow efficiency

---

## Contributing

### Improving the Workflow

1. Fork the repository
2. Modify `.github/workflows/Jules-Assessment-Remediator.yml`
3. Test with dry-run mode
4. Submit PR with description of changes
5. Include example run showing improvement

### Updating Documentation

1. Edit this guide: `docs/workflows/ASSESSMENT_REMEDIATION_GUIDE.md`
2. Update examples with real scenarios
3. Add troubleshooting cases
4. Submit PR with changes

---

## Related Resources

### Documentation
- [Jules Documentation](https://jules.google.com/docs)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [AffineDrift Assessment Guide](../assessments/README.md)

### Workflows
- `.github/workflows/Jules-Control-Tower.yml` - Orchestration
- `.github/workflows/Jules-Auto-Repair.yml` - CI failure fixes
- `.github/workflows/Jules-Documentation-Scribe.yml` - Docstring updates
- `.github/workflows/Jules-Test-Generator.yml` - Test creation

### Templates
- `.github/workflows/templates/assessment-fix-template.md` - PR template
- `.github/ISSUE_TEMPLATE/assessment-issue.md` - Issue template (if exists)

---

## License

This workflow is part of the AffineDrift project and is subject to the repository's license terms.

---

**Last Updated:** 2026-01-17
**Maintained By:** AffineDrift Team
**Version:** 1.0.0
