# CI Workflow Hardening Gap Inventory (#5249)

| Workflow | Top-Level `permissions` | `${{ github.event.* }}` in `run:` | Unpinned `uses:` |
| --- | --- | --- | --- |
| `Jules-Redundant-Issue-Closer.yml` | `contents: read, issues: write` | none | none |
| `Jules-Redundant-PR-Closer.yml` | `contents: read, pull-requests: write, issues: write` | none | none |
| `anti-phantom-merge.yml` | `contents: read, pull-requests: write, issues: read` | none | none |
| `architecture-map-contract.yml` | `contents: read` | none | none |
| `block-self-merge.yml` | `contents: read` | none | none |
| `ci-benchmarks.yml` | `contents: read` | none | none |
| `ci-standard.yml` | `contents: read` | none | none |
| `codex-review-request.yml` | `contents: read, issues: read, pull-requests: read` | none | none |
| `collate-changes.yml` | `contents: write, pull-requests: write` | none | none |
| `compile-textbooks.yml` | `contents: read` | none | none |
| `conflict-disarm.yml` | `contents: write, pull-requests: write` | none | none |
| `cross-browser-nightly.yml` | `contents: read, issues: write` | none | none |
| `deploy-website.yml` | `contents: read, pages: write, id-token: write` | none | none |
| `link-checker.yml` | `contents: read, issues: write` | none | none |
| `lint-workflow-files.yml` | `contents: read, pull-requests: write` | `L81: github.event.pull_request.number` | none |
| `local-only-runner-guard.yml` | `contents: read` | none | none |
| `release.yml` | `contents: write` | none | none |
| `spec-check.yml` | `contents: read, pull-requests: write` | `L54: github.event.pull_request.base.sha` | none |

## Summary of Findings

- **Top-level `permissions`**: All 18 workflows under `.github/workflows` explicitly declare top-level `permissions:` (`0` missing).
- **Action SHA pinning (`uses:`)**: All 18 workflows have `0` unpinned action references (`conflict-disarm.yml` references the allowed fleet reusable workflow `D-sorganization/Repository_Management/.github/workflows/reusable-conflict-disarm.yml@main`; all other actions use 40-character commit SHAs).
- **Untrusted `run:` interpolations (`${{ github.event.* }}`)**:
  - `lint-workflow-files.yml` (`L81`): interpolates `github.event.pull_request.number` (integer PR number).
  - `spec-check.yml` (`L54`): interpolates `github.event.pull_request.base.sha` (40-hex commit SHA).
  - No workflow interpolates user-controlled text fields (`issue.title`, `issue.body`, `pull_request.title`, `pull_request.body`, `comment.body`, or `head.ref`) directly into `run:`.
