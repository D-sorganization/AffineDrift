# Assessment & Report Retention Policy

## Overview

This policy governs retention and archival of assessment reports, CI analysis files, and other generated documents in the `docs/assessments/` directory.

## Retention Categories

### Keep Indefinitely (Permanent)
- Assessments that represent a major architectural decision or turning point
- The most recent version of each assessment type
- Reports cited by open GitHub issues

### Keep for 6 Months
- Completist reports (automated quality summaries)
- CI failure digests
- Weekly status reports

### Archive/Delete After 3 Months
- Duplicate dated versions when superseded by a newer version of the same type
- Assessment files where all issues have been closed and resolved
- PR feedback JSON files after the PR is merged

## Current Status (as of 2026-03-12)

### Assessments to Keep
- `ARCHITECTURE_QUALITY_ASSESSMENT_2026-02-12.md` — Most recent full architecture assessment
- `Adversarial_Mathematical_Assessment_2026-03-10.md` — Most recent content assessment
- `Assessment_A_Code_Structure.md` through `Assessment_H_CI_CD.md` — Original categorical assessments (keep as baseline)

### Candidates for Archival
- Multiple dated `Completist_Report_*.md` files — keep only the 3 most recent
- `PR_Feedback_*.json` files where PRs are merged — can be removed
- Duplicate assessments from the same category

## Process

1. CI/CD generates new assessments periodically
2. When a new assessment supersedes an older one of the same type, the older one should be moved to `docs/assessments/archive/`
3. Files in `archive/` are deleted after 6 months if no open issues reference them

## Relationship to GitHub Issues

Assessment files that directly generate GitHub issues should be retained until all issues they identified are closed. The mapping is maintained by the automated issue-creation workflow.
