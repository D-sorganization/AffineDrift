# Broken Windows Mitigation — Issue #1699

## Executive Summary

Assessment #1699 identified 620 TRACKED_TASK markers, 1,606 TRACKED_DEFECT/XXX markers, and 1,068 incomplete markers across the codebase. This document outlines the mitigation strategy for reducing broken-window signals and improving code confidence.

## Current State Analysis

### Inventory Scan

**Active Python codebase (src/, scripts/, tests/):**
- `TRACKED_TASK` markers: 0 (clean)
- `TRACKED_DEFECT` markers: 0 (clean)
- `FIXME` comments: 1 (test documentation)
- `TODO` comments: 1 (test documentation)
- Intentional `pass` statements: 1 (appropriate exception handling)
- `NotImplementedError`: 0 (clean)

**Status: VERY HEALTHY** ✓

### Assessment Context

The assessment counted markers across:
- Generated/bundled files (node_modules, package-lock.json)
- Auto-generated content (docs/, rendered HTML)
- Configuration and data files
- Historical files and archives

These are not actionable "broken windows" in the active codebase.

## Broken Windows Prevention Policy

### 1. Production Code (src/)

**STRICT ENFORCEMENT:**
- No TODO/FIXME/HACK/XXX comments
- No NotImplementedError without external issue reference
- No intentional `pass` statements (except exception handlers)

**Enforcement:** CI will fail if violations detected

### 2. Script Code (scripts/)

**GUIDELINES:**
- Link every TODO/FIXME to a tracked GitHub issue: `# TODO (Issue #XXXX): description`
- Limit broken windows to < 3 active markers per script
- Monthly triage of open markers

**Example:**
```python
# TODO (Issue #1234): Add parallel processing when thread pool is available
def process_files(files):
    ...
```

### 3. Test Code (tests/)

**RELAXED:**
- Test-specific TODOs allowed if test-focused
- Document intent clearly: "# TODO: Add fuzzing coverage for edge case"
- Remove before code freeze

### 4. Content & Documentation

**NOT ENFORCED:**
- Quarto/Markdown authoring notes OK
- Config/data files exempt (auto-generated)

## Maintenance Program

### Weekly Triage
- Run marker inventory scan
- Flag new TODOs added without issue references
- Archive resolved items

### Monthly Review
- Count active markers by type
- Review old (> 30 days) open markers
- Escalate to issues or close

### Quarterly Assessment
- Report trend of marker counts
- Update CI enforcement rules if needed
- Celebrate closed markers

## Example Marker Formats

### Correct (Linked to Issue)
```python
# TODO (Issue #2890): Optimize FFT for large datasets
# FIXME (Issue #2891): Handle NaN gracefully in divergence calculation
```

### Acceptable (Temporary Development)
```python
# TODO: Remove debug logging before merge
# HACK: Workaround for test flakiness; replace with proper fixture
```

### NOT ACCEPTABLE (Broken Windows)
```python
# TODO fix this
# XXX this is ugly
# FIXME bad
```

## Metrics & Reporting

**Target Metrics:**
- Active broken-window markers in src/: 0
- Script markers with valid issue references: 100%
- Marker age (max): 90 days before escalation
- Monthly trend: steadily decreasing or stable

**Reporting:**
- Include in quarterly code-quality reports
- Track in team dashboards
- Celebrate milestones (e.g., "All markers resolved!")

## Next Steps

1. Implement CI check for issue-linked markers
2. Archive historical markers (before 2026-01-01)
3. Set up weekly inventory automation
4. Document marker standards in CONTRIBUTING.md

---

**Reference:** Issue #1699, Fleet Assessment: Pragmatic Broken-Windows
