# Workflow Inventory

This directory contains the 12 GitHub Actions workflow files for the AffineDrift
repository. Edits are governed by
[`Repository_Management/docs/architecture/WORKFLOW_GOVERNANCE.md`](https://github.com/D-sorganization/Repository_Management/blob/main/docs/architecture/WORKFLOW_GOVERNANCE.md):
keep changes minimal, never rename a workflow file or the `quality-gate` job,
and reference the governing campaign issue in the PR body.

## Merge-blocking

| Workflow                      | Purpose                                                                                                                                                                                                                                              | Triggers                                         |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `ci-standard.yml`             | `static-checks` (lint, format, mypy, ~30 repository gates), `tests` (pytest), `js-tests` (Jest), `e2e-tests` (full-site render, Playwright, axe-core), `website-lint`, and the fan-in `quality-gate` job that the ruleset requires (#4126).             | `push` to `main`, pull requests, manual dispatch |
| `local-only-runner-guard.yml` | `Reject hosted runner routing` — required by the `block-hosted-runner-merge` ruleset; runs on `ubuntu-latest` as the canary that must work when the fleet is down.                                                                                    | Pull requests, manual dispatch                   |
| `spec-check.yml`              | Blocks a PR that changes `src/`, `tests/`, `pyproject.toml`, or `package.json` without touching `SPEC.md`, unless labelled `spec-exempt`. Lives in its own workflow file, so it cannot be a `needs` dependency of `quality-gate`.                    | Pull requests                                    |

## Deployment

| Workflow             | Purpose                                                                                                                                                                                | Triggers                          |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `deploy-website.yml` | Pre-render gates, Quarto render, sitemap/RSS, CSS bundle, revision-bound manifest, claim-audit coverage, every-route + visual verification, GitHub Pages deploy, live re-verification. | `push` to `main`, manual dispatch |

## Advisory (not required)

| Workflow                  | Purpose                                                                                             | Triggers                                             |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `compile-textbooks.yml`   | `latexmk` builds of the LaTeX books with page-count floors and bibliography completeness checks.    | `articles/**` `.tex`/`.sty`/`.bib` changes, dispatch |
| `ci-benchmarks.yml`       | pytest-benchmark smoke run with a PR comment.                                                       | `push`, pull requests, dispatch                      |
| `link-checker.yml`        | Internal link check on PRs (blocking within the workflow); external URLs on schedule, non-blocking. | PRs touching md/qmd, daily 02:00 UTC, dispatch       |
| `lint-workflow-files.yml` | actionlint-style validation of workflow files with a PR comment.                                    | Pull requests                                        |
| `anti-phantom-merge.yml`  | Governance guard against merges whose diff does not match the review.                               | Pull request events                                  |
| `block-self-merge.yml`    | Governance guard against self-merged PRs.                                                           | Pull request events                                  |

## Housekeeping

| Workflow                           | Purpose                              | Triggers      |
| ---------------------------------- | ------------------------------------ | ------------- |
| `Jules-Redundant-Issue-Closer.yml` | Closes duplicate agent-filed issues. | Every 6 hours |
| `Jules-Redundant-PR-Closer.yml`    | Closes superseded agent PRs.         | Every 3 hours |

## Notes

- Every workflow routes through the `pick-runner` dispatcher (`d-sorg-fleet` when
  `RUNNER_TARGET=local` or the repository is non-public; otherwise `ubuntu-latest`).
- Issue #2915 removed 16 obsolete workflows; #4126 turned `quality-gate` into a
  fan-in job and rewrote this inventory (it previously claimed three workflows).
