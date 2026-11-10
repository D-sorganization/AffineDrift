# CI Workflow Hardening Gap Inventory (#5249)

| Workflow | Top-Level `permissions` | `${{ github.event.* }}` in `run:` | Unpinned `uses:` |
| --- | --- | --- | --- |
| `Jules-Redundant-Issue-Closer.yml` | `contents: read, issues: write` | none | none |
| `Jules-Redundant-PR-Closer.yml` | `contents: read, pull-requests: write, issues: write` | none | none |
| `alpha-war-calcs-integration.yml` | `contents: read` | none | none |
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
