## Summary

- What changed:
- Why:

## Validation

- [ ] Unit/integration tests added or updated
- [ ] Local checks run (`pytest`, lint, or targeted scripts)

## Merge Readiness

- [ ] Required status checks pass on the exact head
- [ ] All review threads, if any, are resolved before merge
- [ ] Optional review focus areas are listed when risk or specialized ownership warrants review
- [ ] No named maintainer approval is treated as a standing release gate

## Regression Discipline

- [ ] If this PR fixes a bug, a regression test was added in the same PR
- [ ] If no regression test was added, rationale is documented below

## Risk and Rollback

- [ ] Risk level documented (low/medium/high)
- [ ] Rollback plan documented for non-trivial changes

### Regression Test Rationale (if omitted)

- N/A

---

## Optional Reviewer Checklist

When review is requested for risk or expertise, please verify:

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
