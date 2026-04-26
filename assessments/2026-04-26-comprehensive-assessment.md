# AffineDrift — Comprehensive A-O Health Assessment

**Date:** 2026-04-26
**Branch:** main
**HEAD:** `52fafc52f09861b6fadc18f6167cdd9341133d1e`
**Owner/Repo:** D-Sorganization/AffineDrift

## Scores

| Criterion | Name | Score | Weight | Weighted |
|-----------|------|-------|--------|----------|
| A | Project Organization | 100 | 5% | 5.00 |
| B | Documentation | 100 | 8% | 8.00 |
| C | Testing | 90 | 12% | 10.80 |
| D | Error Handling | 73.2 | 10% | 7.32 |
| E | Performance | 45 | 7% | 3.15 |
| F | Code Quality | 76 | 10% | 7.60 |
| G | Dependency Hygiene | 90 | 8% | 7.20 |
| H | Security | 59 | 10% | 5.90 |
| I | Configuration Management | 70 | 6% | 4.20 |
| J | Observability | 51 | 7% | 3.57 |
| K | Maintenance Debt | 66.4 | 7% | 4.65 |
| L | CI/CD | 100 | 8% | 8.00 |
| M | Deployment | 40 | 5% | 2.00 |
| N | Legal & Compliance | 95 | 4% | 3.80 |
| O | Agentic Usability | 90 | 3% | 2.70 |
| **Total** | | | | **83.89** |

## Findings Summary

- **P0 (Critical):** 1
- **P1 (High):** 3
- **P2 (Medium):** 3

### P0 Findings

- **[H]** [AffineDrift] 12 potential hardcoded secrets

### P1 Findings

- **[D]** [AffineDrift] 6 bare except: statements
- **[D]** [AffineDrift] 133 lint suppressions
- **[L]** [AffineDrift] No branch protection on main

### P2 Findings

- **[E]** [AffineDrift] No performance benchmarks
- **[F]** [AffineDrift] 7 TODO/FIXME items
- **[M]** [AffineDrift] No deployment artifacts


## Evidence

```json
{
  "repo": "AffineDrift",
  "owner_repo": "D-Sorganization/AffineDrift",
  "branch": "main",
  "head_sha": "52fafc52f09861b6fadc18f6167cdd9341133d1e",
  "head_date": "2026-04-26",
  "A": {
    "src_files": 206,
    "test_files": 582,
    "manifests": 3,
    "gitignore_lines": 141,
    "has_readme": 1
  },
  "B": {
    "readme_lines": 134,
    "readme_headers": 16,
    "docs_files": 148,
    "md_files": 8
  },
  "C": {
    "test_py": 166,
    "test_rs": 0,
    "src_py": 97,
    "src_rs": 0
  },
  "D": {
    "bare_except": 6,
    "except_exception": 3,
    "noqa_suppressions": 133
  },
  "F": {
    "todo_fixme": 7
  },
  "G": {
    "req_lockfiles": 1
  },
  "H": {
    "secrets_raw": 12
  },
  "I": {
    "env_example": 1
  },
  "J": {
    "logging_refs": 200,
    "metrics_refs": 73
  },
  "K": {
    "suppressions": 133
  },
  "L": {
    "workflow_files": 57
  },
  "M": {
    "dockerfile": 0
  },
  "N": {
    "license": 1
  },
  "O": {
    "claude_md": 1,
    "agents_md": 1,
    "claude_lines": 90
  }
}
```