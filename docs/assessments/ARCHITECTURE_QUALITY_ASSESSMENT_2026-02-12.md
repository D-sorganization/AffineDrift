# Architecture and Quality Assessment - AffineDrift

Date: 2026-02-12
Scope: website architecture and engineering quality against DRY, DbC, TDD, Orthogonality, Reversibility, Reusability, Changeability, Law of Demeter, Project Organization, Code Comment Quality, Documentation, with explicit focus on layout stability and Quarto rendering reliability.

## Executive Summary
AffineDrift has substantial content depth and useful tooling, but the website stack has high drift risk due to duplicated frontend surfaces, brittle CSS override patterns, and non-enforcing site health checks.

Most urgent priorities:
1. Enforce canonical frontend asset flow and eliminate source/output drift
2. Make site health checks blocking and resolve existing broken links
3. Reduce layout fragility in CSS and simplify Quarto asset injection
4. Correct documentation/runtime guidance drift

## Snapshot Metrics
- GitHub workflows: 54
- Quarto pages (`*.qmd`): 108
- Python files: 100
- Python test files: 28
- JS files: 70
- CSS/SCSS files: 31
- Tracked generated HTML in `docs/`: 109

## Criteria Scores (1-10)
| Criterion | Score | Notes |
|---|---:|---|
| DRY | 4 | Duplicate frontend trees and generated/source overlap |
| DbC | 6 | Contracts module exists, but runtime/version consistency issues remain |
| TDD | 5 | JS tests are healthy; Python tests fail under common local interpreter mismatch |
| Orthogonality | 3 | Frontend and build responsibilities overlap across root/src/docs |
| Reversibility | 6 | Legacy/archives preserved, but increase operational noise |
| Reusability | 5 | Some modular JS and tool utilities; duplication limits reuse confidence |
| Changeability | 3 | Large style layer + many overrides create high regression risk |
| Law of Demeter | 5 | Mixed concern boundaries; moderate traversal/coupling patterns |
| Project Organization | 3 | Source vs generated vs archive boundaries are not cleanly enforced |
| Code Comment Quality | 7 | Generally clear and helpful comments/docstrings |
| Documentation | 3 | README/testing docs reference non-existent paths/workflows |

## Evidence Highlights
- Canonical render pipeline cannot be locally validated without Quarto binary in env (`quarto: command not found` during audit).
- `_quarto.yml` manually enumerates deep render paths and injects substantial inline script/style metadata: `_quarto.yml:4`, `_quarto.yml:102`, `_quarto.yml:206`
- Source/output drift:
  - `js/startup-launcher.js` differs from `src/js/startup-launcher.js`
  - `js/bibliography.js` differs from `src/js/bibliography.js`
  - `script.js` differs from `docs/script.js`
- Layout fragility signals:
  - `styles.css` ~3349 lines
  - 200+ `!important` usages
  - Repeated high-specificity Quarto override sections (`styles.css:83`, `styles.css:155`, `styles.css:2721`)
- Site integrity check currently non-blocking by implementation behavior; script reports but does not fail on broken/orphaned links.
- Current health run found 5 broken links and 23 orphaned pages.
- Docs drift:
  - Missing workflow references from README (`.github/workflows/quarto-publish.yml`, `.github/workflows/deploy.yml`)
  - Missing docs references (`docs/development/WEBSITE_MANAGEMENT.md`, `docs/development/DEVELOPMENT_GUIDE.md`)
- Python runtime mismatch surfaced by tests:
  - Python 3.10 collection error on 3.12-style syntax in `src/core/contracts.py:292`

## Tracking Issues (Created)
- [#1122](https://github.com/D-sorganization/AffineDrift/issues/1122) Define canonical frontend source-of-truth and enforce asset sync
- [#1123](https://github.com/D-sorganization/AffineDrift/issues/1123) Make site health checks enforceable and fail builds on integrity regressions
- [#1124](https://github.com/D-sorganization/AffineDrift/issues/1124) Resolve current broken internal links and validate tool page routing
- [#1125](https://github.com/D-sorganization/AffineDrift/issues/1125) Reduce layout fragility in `styles.css` and remove high-risk override patterns
- [#1126](https://github.com/D-sorganization/AffineDrift/issues/1126) Simplify and harden `_quarto.yml` asset/script injection path
- [#1127](https://github.com/D-sorganization/AffineDrift/issues/1127) Refresh README and testing docs to match actual repo/workflow topology
- [#1128](https://github.com/D-sorganization/AffineDrift/issues/1128) Align Python runtime expectations across code, tests, and local dev
- [#1129](https://github.com/D-sorganization/AffineDrift/issues/1129) Rationalize docs output tracking strategy (`docs/` as generated artifact)
- [#1130](https://github.com/D-sorganization/AffineDrift/issues/1130) Stabilize Quarto render coverage for nested article trees

## Phased Execution Plan
1. Pipeline safety and drift control
   - #1122, #1123, #1124
2. Layout/render stabilization
   - #1125, #1126, #1130
3. Documentation and runtime consistency
   - #1127, #1128
4. Artifact governance
   - #1129
