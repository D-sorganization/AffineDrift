# PR and Branch Naming Conventions

**Status:** Standard
**Document Version:** 1.0.0
**Created:** 2026-01-21
**Last Updated:** 2026-01-21

---

## Overview

This document establishes consistent naming conventions for all automated PRs and branches created by Jules workflows. Consistency in naming enables:

- Easy identification of automated vs. manual PRs
- Quick filtering and searching
- Clear understanding of PR purpose
- Audit trail of automated changes

---

## PR Title Convention

### Format

All automated PRs MUST follow the conventional commits format:

```
{type}(jules/{worker}): {description}
```

### Components

| Component | Description | Required |
|-----------|-------------|----------|
| `type` | The type of change (see types below) | Yes |
| `jules/{worker}` | Identifies automation source | Yes |
| `description` | Brief description of changes | Yes |

### Allowed Types

| Type | Use Case | Example |
|------|----------|---------|
| `fix` | Bug fixes, CI/CD repairs, error corrections | `fix(jules/auto-repair): resolve lint errors` |
| `feat` | New features, capabilities | `feat(jules/test-gen): add unit tests for auth module` |
| `chore` | Maintenance, cleanup, refactoring | `chore(jules/custodian): refactor utils module` |
| `docs` | Documentation changes | `docs(jules/scribe): update API documentation` |
| `style` | Formatting, whitespace, no code change | `style(jules/quality): apply black formatting` |
| `refactor` | Code restructuring without behavior change | `refactor(jules/custodian): simplify error handling` |
| `test` | Adding or updating tests | `test(jules/test-gen): add integration tests` |
| `ci` | CI/CD configuration changes | `ci(jules/auto-repair): fix workflow syntax` |
| `security` | Security fixes or improvements | `security(jules/sentinel): patch dependency vulnerability` |

### Worker Identifiers

Each Jules workflow uses a specific worker identifier:

| Workflow | Worker ID | Full Scope |
|----------|-----------|------------|
| Jules-Auto-Repair | `auto-repair` | `jules/auto-repair` |
| Jules-Hotfix-Creator | `hotfix` | `jules/hotfix` |
| Jules-Assessment-Remediator | `remediation` | `jules/remediation` |
| Jules-Issue-Resolver | `resolver` | `jules/resolver` |
| Jules-PR-Compiler | `compiler` | `jules/compiler` |
| Jules-Tech-Custodian | `custodian` | `jules/custodian` |
| Jules-Documentation-Scribe | `scribe` | `jules/scribe` |
| Jules-Test-Generator | `test-gen` | `jules/test-gen` |
| Jules-Code-Quality-Fixer | `quality` | `jules/quality` |
| Jules-Sentinel | `sentinel` | `jules/sentinel` |

---

## PR Title Examples by Workflow

### Auto-Repair (CI/CD Fixes)

```
fix(jules/auto-repair): resolve failing tests in auth module
fix(jules/auto-repair): correct type errors in api handlers
fix(jules/auto-repair): fix lint errors blocking CI
```

### Hotfix Creator (Urgent Main Branch Fixes)

```
fix(jules/hotfix): urgent CI failure on main
fix(jules/hotfix): critical build error on master
```

### Assessment Remediator

```
fix(jules/remediation): address 5 assessment issues
fix(jules/remediation): resolve P0 code quality findings
chore(jules/remediation): add missing docstrings and type hints
```

### Issue Resolver

```
fix(jules/resolver): resolve daily assessment issues (2026-01-21)
fix(jules/resolver): address 3 priority issues
```

### PR Compiler

```
chore(jules/compiler): consolidate 4 code quality PRs
chore(jules/compiler): merge 3 security fix PRs
```

### Tech Custodian

```
refactor(jules/custodian): weekly refactor of utils.py
chore(jules/custodian): cleanup deprecated code in handlers
```

### Documentation Scribe

```
docs(jules/scribe): update API reference documentation
docs(jules/scribe): add missing README for services module
```

### Test Generator

```
test(jules/test-gen): add unit tests for new endpoints
test(jules/test-gen): increase coverage for auth module
```

### Code Quality Fixer

```
style(jules/quality): apply consistent formatting
fix(jules/quality): resolve linting errors
```

### Sentinel (Security)

```
security(jules/sentinel): update vulnerable dependencies
security(jules/sentinel): fix SQL injection vulnerability
```

---

## PR Title for Replacement PRs

When a PR replaces a failed PR (Option C strategy), use this format:

```
fix(jules/{worker}): {description} [replaces #{original_pr}]
```

### Examples

```
fix(jules/auto-repair): resolve CI failures [replaces #42]
fix(jules/hotfix): fix build errors [replaces #156]
```

---

## Branch Naming Convention

### Format

```
jules/{worker}-{date}-{identifier}
```

### Components

| Component | Format | Example |
|-----------|--------|---------|
| `jules/` | Prefix (always) | `jules/` |
| `{worker}` | Worker identifier | `auto-repair` |
| `{date}` | Date in YYYYMMDD | `20260121` |
| `{identifier}` | Optional context | `pr42`, `main`, `lint` |

### Branch Examples by Workflow

| Workflow | Branch Pattern | Example |
|----------|----------------|---------|
| Auto-Repair | `jules/auto-repair-{date}-{context}` | `jules/auto-repair-20260121-pr42` |
| Hotfix Creator | `jules/hotfix-{date}-{branch}` | `jules/hotfix-20260121-main` |
| Assessment Remediator | `jules/remediation-{date}` | `jules/remediation-20260121` |
| Issue Resolver | `jules/resolver-{date}` | `jules/resolver-20260121` |
| PR Compiler | `jules/compiler-{date}-{category}` | `jules/compiler-20260121-quality` |
| Tech Custodian | `jules/custodian-{date}-{file}` | `jules/custodian-20260121-utils` |
| Documentation Scribe | `jules/scribe-{date}` | `jules/scribe-20260121` |
| Test Generator | `jules/test-gen-{date}-{module}` | `jules/test-gen-20260121-auth` |
| Code Quality Fixer | `jules/quality-{date}` | `jules/quality-20260121` |
| Sentinel | `jules/sentinel-{date}` | `jules/sentinel-20260121` |

---

## PR Labels

### Required Labels

All automated PRs MUST include these labels:

| Label | Purpose |
|-------|---------|
| `jules:automated` | Identifies PR as automated |
| `jules:{worker}` | Identifies the specific worker |

### Optional Labels

| Label | When to Use |
|-------|-------------|
| `needs-review` | PR requires human review before merge |
| `auto-merge` | PR can be auto-merged if CI passes |
| `urgent` | Time-sensitive fix |
| `replaces-pr` | PR supersedes another PR |
| `security` | Contains security-related changes |

### Label Examples by Workflow

```yaml
# Auto-Repair
labels: jules:automated, jules:auto-repair, needs-review

# Hotfix (urgent)
labels: jules:automated, jules:hotfix, urgent, needs-review

# Assessment Remediator
labels: jules:automated, jules:remediation, needs-review

# PR Compiler
labels: jules:automated, jules:compiler, auto-merge

# Security (Sentinel)
labels: jules:automated, jules:sentinel, security, urgent
```

---

## PR Body Structure

All automated PRs MUST include a structured body:

### Required Sections

```markdown
## Summary
{Brief description of what this PR does}

## Changes
- {Change 1}
- {Change 2}
- {Change 3}

## Generated By
- **Workflow:** {workflow_name}
- **Run:** {workflow_run_url}
- **Triggered:** {trigger_reason}

## Review Checklist
- [ ] Changes are correct and complete
- [ ] No unintended side effects
- [ ] CI checks pass
```

### Optional Sections

```markdown
## Related Issues
- Fixes #{issue_number}
- Related to #{issue_number}

## Context Preserved
{Link to archived PR context if this is a replacement PR}

## Test Results
{Summary of test execution}

## Breaking Changes
{List any breaking changes, or "None"}
```

---

## Migration from Current Naming

### Current → New Mapping

| Workflow | Current Pattern | New Pattern |
|----------|-----------------|-------------|
| Hotfix Creator | `hotfix/ci-fail-{timestamp}` | `jules/hotfix-{date}-{branch}` |
| Assessment Remediator | `auto-fix/assessment-remediation-{timestamp}` | `jules/remediation-{date}` |
| Issue Resolver | `jules/issue-resolver-{timestamp}` | `jules/resolver-{date}` |
| PR Compiler | `jules/compiled-{category}-{date}` | `jules/compiler-{date}-{category}` |
| Tech Custodian | `refactor/custodian-{date}-{file}` | `jules/custodian-{date}-{file}` |
| Documentation Scribe | `docs/update-{timestamp}` | `jules/scribe-{date}` |

### PR Title Migration

| Workflow | Current Title | New Title |
|----------|---------------|-----------|
| Hotfix | `Urgent: Fix CI failure on main` | `fix(jules/hotfix): CI failure on main` |
| Assessment | `[Auto-remediation] Fix top 5 issues` | `fix(jules/remediation): address 5 assessment issues` |
| Issue Resolver | `Issue Resolution - 2026-01-21` | `fix(jules/resolver): resolve daily assessment issues (2026-01-21)` |
| PR Compiler | `[Compiled] code_quality: 3 PRs` | `chore(jules/compiler): consolidate 3 code quality PRs` |
| Tech Custodian | `chore: weekly refactor of app.py` | `refactor(jules/custodian): weekly refactor of app.py` |
| Doc Scribe | `docs: update metadata` | `docs(jules/scribe): update metadata` |

---

## Validation Rules

### PR Title Validation

PRs created by Jules workflows MUST:

1. Start with a valid type (`fix`, `feat`, `chore`, `docs`, `style`, `refactor`, `test`, `ci`, `security`)
2. Include scope in format `(jules/{worker})`
3. Have a description after the colon
4. Be under 100 characters total
5. Not include emojis (keep machine-readable)

### Branch Name Validation

Branches created by Jules workflows MUST:

1. Start with `jules/`
2. Include a valid worker identifier
3. Include date in YYYYMMDD format
4. Use only lowercase letters, numbers, and hyphens
5. Be under 60 characters total

### Regex Patterns

```regex
# PR Title
^(fix|feat|chore|docs|style|refactor|test|ci|security)\(jules\/[a-z-]+\): .{1,70}(\s\[replaces #\d+\])?$

# Branch Name
^jules\/[a-z-]+-\d{8}(-[a-z0-9-]+)?$
```

---

## Implementation Checklist

When updating workflows to use new naming conventions:

- [ ] Update branch name generation
- [ ] Update PR title generation
- [ ] Update PR label assignment
- [ ] Update PR body template
- [ ] Add validation step (optional but recommended)
- [ ] Update documentation references
- [ ] Test with dry-run before production

---

## Enforcement

### Recommended: PR Title Linter

Add a GitHub Action to validate PR titles:

```yaml
name: PR Title Check
on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  check-title:
    if: startsWith(github.head_ref, 'jules/')
    runs-on: ubuntu-latest
    steps:
      - name: Validate Jules PR Title
        run: |
          TITLE="${{ github.event.pull_request.title }}"
          if ! echo "$TITLE" | grep -qE '^(fix|feat|chore|docs|style|refactor|test|ci|security)\(jules\/[a-z-]+\):'; then
            echo "ERROR: PR title does not follow Jules naming convention"
            echo "Expected format: {type}(jules/{worker}): {description}"
            exit 1
          fi
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    Jules PR Naming Quick Reference              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PR TITLE FORMAT:                                               │
│  {type}(jules/{worker}): {description}                         │
│                                                                 │
│  TYPES: fix | feat | chore | docs | style | refactor |         │
│         test | ci | security                                    │
│                                                                 │
│  WORKERS: auto-repair | hotfix | remediation | resolver |      │
│           compiler | custodian | scribe | test-gen |           │
│           quality | sentinel                                    │
│                                                                 │
│  BRANCH FORMAT:                                                 │
│  jules/{worker}-{YYYYMMDD}-{identifier}                        │
│                                                                 │
│  LABELS (required):                                             │
│  jules:automated, jules:{worker}                               │
│                                                                 │
│  EXAMPLES:                                                      │
│  Title:  fix(jules/auto-repair): resolve lint errors           │
│  Branch: jules/auto-repair-20260121-pr42                       │
│  Labels: jules:automated, jules:auto-repair, needs-review      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

- [CI/CD Fixer PR Replacement Strategy](./CICD_FIXER_PR_REPLACEMENT_STRATEGY.md)
- [Assessment Remediation Guide](./ASSESSMENT_REMEDIATION_GUIDE.md)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

---

**Maintained By:** AffineDrift Team
**Document Owner:** DevOps
