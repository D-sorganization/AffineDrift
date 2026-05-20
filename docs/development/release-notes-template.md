# Release Notes Template

This template is used for documenting significant changes in AffineDrift. Since
the repository deploys continuously from `main`, release notes capture milestone
progress rather than version-gated releases.

## Template

Copy the template below into `CHANGELOG.md` under `## [Unreleased]` for
in-progress work, or under a dated milestone heading for completed work.

---

```markdown
## [Wave N] — YYYY-MM-DD

### Summary

One paragraph describing the theme of this milestone and its main outcomes.

### Added

- **Feature/content**: Description. Resolves #<issue>.
- **Documentation**: What was documented. Closes #<issue>.
- **Test coverage**: What was tested. Related to #<issue>.

### Fixed

- **Bug**: What was wrong and how it was fixed. Closes #<issue>.
- **CI**: What was failing and how it was resolved. Fixes #<issue>.

### Changed

- **Refactor**: What changed (behavior unchanged). Related to #<issue>.
- **Dependency**: `package` updated from `X.Y.Z` to `A.B.C`. Closes #<dependabot-pr>.

### Deprecated

- **Feature/API**: What is deprecated and when it will be removed.

### Removed

- **Feature/API**: What was removed and why.

### Security

- **Fix**: CVE-ID or bandit finding fixed. Closes #<issue>.
```

---

## Current Entry

See [CHANGELOG.md](../../CHANGELOG.md) for the live changelog.

## Writing Good Release Notes

### Be specific and link issues

```markdown
# Good
- **iLQR convergence**: Fixed numerical instability when swing speed > 150 mph.
  Root cause: missing regularization update in backward pass. Closes #2887.

# Bad
- Fixed solver bug
```

### Group by user impact

Order entries within each section by user impact (highest first):

1. Breaking changes or major new features
2. Bug fixes that unblock work
3. Performance improvements
4. Documentation
5. Internal refactors and CI fixes

### Include upgrade notes for breaking changes

```markdown
### Changed

- **API**: `SwingOptimizer.solve()` now returns `TrajectoryResult` instead of
  `list[SwingState]`. Update call sites:

  ```python
  # Before
  states = optimizer.solve()

  # After
  result = optimizer.solve()
  states = result.states
  ```

  Closes #2919.
```

## Milestone Cadence

AffineDrift uses **Waves** to organize milestones:

| Wave | Focus |
|------|-------|
| Wave 1 | Foundation (CI, tests, baseline quality) |
| Wave 2 | Content expansion and correctness |
| Wave 3 | Operations and observability |
| Wave 4 | Production readiness and type safety |
| Wave 5 | Documentation completeness and enhancements |

Each wave closes when all EPIC issues for that wave are resolved. Wave epics
are tracked as GitHub issues with the `[EPIC]` prefix.

## Semantic Versioning Reference

While AffineDrift does not publish to PyPI, the changelog follows semantic
versioning conventions for documentation purposes:

- **MAJOR**: Breaking API change or significant content restructure
- **MINOR**: New feature, new article, or new documentation section
- **PATCH**: Bug fix, typo correction, or dependency update

## References

- `CHANGELOG.md` — live project changelog
- GitHub Releases (if used for milestone announcements)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
