# Workflow Inventory

This directory contains the 3 core GitHub Actions workflow files for the AffineDrift repository.

As part of the consolidation effort in Issue #2915, 16 obsolete, overlapping, or legacy generated workflows were removed.

## Core Workflows

| Workflow             | Purpose                                                                                               | Triggers                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `ci-standard.yml`    | Main quality gate for Python, JavaScript, E2E, website linting, Rust, and local-only workflow checks. | `push` to `main`, pull requests, manual dispatch. |
| `deploy-website.yml` | Builds the Quarto website and deploys to GitHub Pages.                                                | `push` to `main`, manual dispatch.                |
| `spec-check.yml`     | Enforces SPEC freshness on pull requests unless `spec-exempt` is present.                             | Pull requests.                                    |

## Notes

- All scheduled metrics, redundant documentation builds, and complex comment-processing workflows have been decommissioned to reduce maintenance burden and CI congestion.
- `ci-standard.yml` now serves as the single source of truth for code quality and test validation.
