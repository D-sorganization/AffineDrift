# AffineDrift Qualitative Code Quality Assessment (2026-02-13)

## Scope
Qualitative code quality only (maintainability/coding standards/architecture discipline). Performance and security excluded.

## Scorecard (1-5)
| Criterion | Score | Notes |
|---|---:|---|
| TDD | 3.2 | Good JS/Python test suite, but E2E reliability had to be narrowed to smoke gating. |
| DbC | 3.0 | Contract layer exists (`src/core/contracts.py`) but not consistently applied across site JS/tooling boundaries. |
| LoD | 3.1 | Moderate chaining; acceptable in frontend, but some orchestration logic still traverses too deep. |
| DRY | 2.4 | Historical root/src/docs asset duplication and drift pressure. |
| Orthogonality | 2.9 | Website + tool scripts + data/infra concerns coexist with uneven separation. |
| Reversibility | 3.4 | CI + sync checks + budgets improve safety; legacy files still complicate rollback confidence. |
| Reusability | 3.0 | Some reusable modules, but several page-specific patterns remain one-off. |
| Changeability | 2.7 | Large CSS/JS files and mirrored assets increase edit coupling. |
| Decoupled | 2.8 | Partial decoupling; stronger separation needed between content, UI behavior, and tool scripts. |
| Comment Quality | 3.2 | Generally readable; still mixed in larger utility scripts. |
| Documentation | 3.5 | Extensive assessments exist; consolidation/canonical guidance still needed. |
| Architecture Quality | 2.9 | Adequate for a content-heavy site, but boundaries are still porous. |

## Evidence Snapshot
- Scale: `py=105`, `js=75`, `qmd=108`, `tests_files=46`, `md=212`.
- Debt markers: `11`.
- LoD proxy: deep chain matches `201`.
- Contract signal: `96` contract/assert hits; explicit contract tests present.
- Large files include `src/js/bibliography.js` (~696 LOC) and large style surface (`styles.css`).
- Active DRY controls exist (`scripts/sync_frontend_assets.py`, new UI/UX budget checks).

## Highest-Leverage Improvement Areas
1. Continue collapsing mirrored frontend assets into single-source ownership.
2. Break up large CSS/JS into scoped modules by feature.
3. Stabilize E2E strategy: short PR smoke + non-blocking nightly full matrix.
4. Expand DbC-style validation in tool scripts and JS boundaries.
5. Define and enforce architecture boundaries between content, rendering, and behavior layers.

## Top 10 Actionable Items
1. Remove remaining mirrored frontend files or enforce strict one-way generated mirrors.
2. Split `styles.css` into base/layout/components/page scopes with clear ownership.
3. Split `src/js/bibliography.js` into data access, render, and interaction modules.
4. Add architectural import rules for `src/core`, `src/tools`, and `src/js` boundaries.
5. Add contract checks for CLI/tool entrypoints (typed input schemas + fail-fast messages).
6. Add doc rule: every new assessment links to canonical “current” summary.
7. Keep PR E2E smoke deterministic (<5 min) and add scheduled full E2E matrix workflow.
8. Add max module size threshold and remediation checklist for over-limit files.
9. Standardize error handling pattern across JS modules (typed or classified error objects).
10. Add ADRs for major website architecture decisions (content pipeline, asset strategy, testing model).

## 30/60/90 Plan
- 30 days: finalize source-of-truth asset policy, establish architecture rules, keep smoke E2E fast.
- 60 days: modularize top CSS/JS files, add contract coverage for tool/CLI boundaries.
- 90 days: complete page/module decomposition and documentation consolidation.
