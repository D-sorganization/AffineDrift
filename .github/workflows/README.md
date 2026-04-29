# Workflow Inventory

This directory currently contains 19 GitHub Actions workflow files plus a
`templates/` helper directory. Issue #2915 proposes a larger consolidation to
3-5 workflows; this inventory is the first reviewable slice. It documents the
current behavior and identifies candidates for later consolidation without
changing any workflow behavior.

## Categories

- **Core**: required for pull-request or production safety today.
- **Optional**: useful automation, reporting, or manual operations that should
  not be required for every pull request.
- **Review-needed**: overlapping, legacy, generated, or externally coupled
  workflow that needs an owner decision before consolidation or removal.

## Current Workflows

| Workflow | Category | Purpose | Triggers | Consolidation notes |
| --- | --- | --- | --- | --- |
| `ci-standard.yml` | Core | Main quality gate for Python, JavaScript, E2E, website linting, Rust, and local-only workflow checks. | `push` to `main`, pull requests, manual dispatch. | Keep as the primary CI workflow. Candidate host for `quarto-syntax-check.yml` after confirming required-check names and path filters. |
| `deploy-website.yml` | Core | Builds the Quarto website and deploys to GitHub Pages. | `push` to `main`, manual dispatch. | Keep separate from PR CI because it writes Pages artifacts and deploys production output. |
| `spec-check.yml` | Core | Enforces SPEC freshness on pull requests unless `spec-exempt` is present. | Pull requests. | Keep separate while SPEC governance remains an independent required gate. |
| `quarto-syntax-check.yml` | Core | Fast syntax scan for Quarto content. | `push` to `main`/`master`, pull requests, scheduled Sunday/Thursday run. | Candidate to fold into `ci-standard.yml` if the scheduled audit and required-check behavior are preserved. |
| `compile_golf_textbook.yml` | Optional | Compiles the Physics of Golf LaTeX textbook and publishes an artifact/release on merge. | Pushes and pull requests touching `articles/The_Physics_of_Golf/**`, manual dispatch. | Textbook build overlaps with other PDF publishing workflows; compare outputs before consolidating. |
| `compile_textbooks.yml` | Optional | Compiles Geometry of Motion LaTeX volumes and combined PDFs. | Pushes and pull requests touching `articles/The_Geometry_of_Motion/**`, manual dispatch. | Overlaps with `latex-release-volumes.yml` and `publish-textbooks-on-merge.yml`; consolidate only after mapping release artifacts. |
| `latex-release-volumes.yml` | Optional | Builds Geometry of Motion volume PDFs and uploads release artifacts. | Pushes and pull requests touching Geometry of Motion volumes, manual dispatch. | Candidate to merge into a single textbook publishing workflow with `publish-textbooks-on-merge.yml`. |
| `publish-textbooks-on-merge.yml` | Optional | Publishes Geometry of Motion LaTeX and Quarto textbook outputs after merges. | Pushes to `main` touching Geometry of Motion content, manual dispatch. | Likely should become the canonical textbook publishing workflow if it supersedes `compile_textbooks.yml` and `latex-release-volumes.yml`. |
| `quarto-pdf-render.yml` | Optional | Renders Quarto PDF outputs for article/book changes and uploads artifacts. | Pushes and pull requests touching Quarto/book inputs, manual dispatch. | Overlaps with textbook publishing and website rendering; keep separate until artifact ownership is clear. |
| `pr-auto-labeler.yml` | Optional | Applies labels to pull requests based on changed files and content patterns. | Pull requests. | Low-cost workflow; can stay separate or move into `ci-standard.yml` if required-check noise is acceptable. |
| `stale-cleanup.yml` | Optional | Marks and closes stale issues/PRs through `actions/stale`. | Scheduled Sunday/Thursday run, manual dispatch. | Keep separate from CI; it mutates issue/PR state. |
| `ci-failure-digest.yml` | Optional | Creates scheduled CI observability and agent metrics reports. | Scheduled Sunday/Thursday run, manual dispatch. | Reporting workflow; can consolidate with other scheduled observability jobs if retained. |
| `Code-Metrics.yml` | Optional | Generates complexity, duplication, and summary metrics. | Scheduled Sunday/Thursday run, manual dispatch. | Candidate to combine with `Pragmatic-Programmer-Review.yml` or another scheduled code-health report. |
| `Pragmatic-Programmer-Review.yml` | Optional | Runs a pragmatic code review report and can create issues. | Reusable workflow call, manual dispatch, scheduled Sunday/Thursday run. | Keep while externally called; if not called by other workflows, consolidate with metrics/reporting. |
| `Comment-to-Issue-Converter.yml` | Review-needed | Converts review comments into GitHub issues and archives comment metadata. | Pull request lifecycle events, review comments, manual dispatch. | Mutates repository state and creates issues; needs owner review before removal or merge into comment handling. |
| `PR-Comment-Responder.yml` | Review-needed | Collects PR comments into `.jules/pending/pr_comments.json` for later processing. | Issue comments and pull request review comments. | Appears coupled to Jules comment-processing infrastructure; document owner and active processor before retaining. |
| `Bot-CI-Trigger.yml` | Review-needed | Finds bot-authored PRs without checks and triggers `ci-standard.yml` or pushes empty commits. | Bot pull requests, scheduled Sunday/Thursday run, manual dispatch. | High-risk automation because it can push to branches; review whether current `ci-standard.yml` triggers make it obsolete. |
| `Maintenance-Global-Control.yml` | Review-needed | Pauses or resumes workflow files by renaming `.yml` files under `.github/workflows`. | Manual dispatch. | High-risk self-mutating workflow; consider replacing with repository environment controls or documented manual operations. |
| `Manual-Run-All.yml` | Review-needed | Dispatches a set of Jules-named workflows. | Manual dispatch. | References workflow IDs that are not present in this directory; likely stale unless those workflows exist elsewhere. |

## Template Directory

| Path | Status | Notes |
| --- | --- | --- |
| `templates/assessment-fix-template.md` | Review-needed | Mentions `Jules Assessment Remediator` and `.github/workflows/Jules-Assessment-Remediator.yml`, which is not present in this directory. |
| `templates/test-remediation-workflow.sh` | Review-needed | Test helper for `Jules-Assessment-Remediator.yml`; no current workflow file with that name exists in this directory. |

## Consolidation Candidates

1. **Keep the core set stable first**: `ci-standard.yml`, `deploy-website.yml`,
   and `spec-check.yml` should remain separate until branch protection and
   deployment requirements are verified.
2. **Merge fast Quarto checks carefully**: `quarto-syntax-check.yml` may fit in
   `ci-standard.yml`, but only after preserving any required check names and the
   scheduled syntax scan.
3. **Create one textbook publishing lane**: compare artifacts from
   `compile_textbooks.yml`, `latex-release-volumes.yml`,
   `publish-textbooks-on-merge.yml`, `compile_golf_textbook.yml`, and
   `quarto-pdf-render.yml`. Consolidation should be artifact-driven rather than
   filename-driven.
4. **Collapse scheduled reports**: `ci-failure-digest.yml`, `Code-Metrics.yml`,
   and `Pragmatic-Programmer-Review.yml` all run on the same Sunday/Thursday
   cadence and may share a reporting workflow if issue-creation behavior is
   retained.
5. **Audit Jules-coupled workflows before deletion**:
   `Manual-Run-All.yml`, `PR-Comment-Responder.yml`, and the files under
   `templates/` reference Jules workflow names or queues that are not present in
   the current workflow set.
6. **Review self-mutating workflows separately**: `Bot-CI-Trigger.yml`,
   `Maintenance-Global-Control.yml`, and `Comment-to-Issue-Converter.yml` can
   push commits or create issues. They should not be removed or merged without a
   run-history and permission review.
