## Summary

- What changed:
- Why:

## Validation

- [ ] Unit/integration tests added or updated
- [ ] Local checks run (`pytest`, lint, or targeted scripts)

## Review Readiness

- [ ] Independent reviewer requested and is not the PR author
- [ ] PR author will not self-approve or self-merge
- [ ] Latest material commit will be reviewed by someone other than its pusher
- [ ] All review threads will be resolved before merge
- [ ] Review focus areas listed (correctness, tests, security, maintainability, ownership)
- [ ] Ownership and reviewer-rotation needs documented for cross-module changes
- [ ] Material follow-up commits will re-request review before merge

## Regression Discipline

- [ ] If this PR fixes a bug, a regression test was added in the same PR
- [ ] If no regression test was added, rationale is documented below

## Risk and Rollback

- [ ] Risk level documented (low/medium/high)
- [ ] Rollback plan documented for non-trivial changes

### Regression Test Rationale (if omitted)

- N/A

---

## Reviewer Checklist

**Note:** This PR requires approval from a reviewer other than the author. Please verify:

- [ ] Code style and formatting pass all linting checks (`ruff`, `mypy`)
- [ ] Type hints are present and correct
- [ ] All new functions have docstrings
- [ ] Tests are added/updated and passing
- [ ] No `print()` statements (use `logging`)
- [ ] Error handling is specific (no bare `except:`)
- [ ] Performance implications considered
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with target branch

See [CONTRIBUTING.md — Code Review Guidelines](../CONTRIBUTING.md#code-review-guidelines) for detailed review expectations.
