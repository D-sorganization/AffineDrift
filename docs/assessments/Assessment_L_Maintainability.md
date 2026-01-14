# Assessment L Results: Long-Term Maintainability

## Executive Summary

The repository is generally healthy but shows signs of organic growth (mixed `tools/`, legacy `archive/`). The strong reliance on AI agents (`AGENTS.md`) is a double-edged sword: it enforces structure but creates a complex set of rules that might be hard for new human maintainers to internalize.

## Top Risks

1.  **Directory Clutter (Severity: LOW)**: `tools/` and `archive/`.
2.  **Agent-Specific Docs (Severity: LOW)**: Documentation tailored for AI might drift from reality if not updated by humans.
3.  **Custom Build Logic (Severity: MEDIUM)**: `build-html.py` is a custom artifact that requires maintenance.

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Tech Debt              | 8/10  | Low debt, mostly cleanup needed.                   | Cleanup `tools/`.                         |
| Code readability       | 9/10  | High (Python).                                     | N/A                                       |
| Bus Factor             | 7/10  | Custom scripts reduce maintainability.             | Simplify/Standardize.                     |

**Weighted Score: 8/10**

## Refactoring Plan

**Quick Wins**
1.  **Archive Cleanup**: Evaluate if `archive/` is needed in the repo or can be moved to a separate branch/repo.
2.  **Refactor Tools**: Execute the plan to split `tools/`.

**Strategic Fixes**
1.  **Simplify Build**: Move as much logic as possible from `build-html.py` back into standard Quarto features (e.g. Listings, Templates).
