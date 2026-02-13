# UI/UX Modernization Plan (2026-02-12)

Scope: Modernize AffineDrift UI/UX to improve clarity, responsiveness, and maintainability while preserving existing design language and Quarto compatibility.

## Objectives

1. Remove fragile inline interaction patterns from core pages and shared modules.
2. Improve homepage layout/navigation behavior for desktop and mobile.
3. Reduce maintainability risk by enforcing UI anti-pattern budgets in CI.
4. Add lightweight UX regression checks so layout and behavior changes are safer.

## Workstreams

### WS1 - Interaction Architecture Cleanup

- Replace inline `onclick` handlers in shared JS-rendered UI with delegated listeners.
- Extract `index.qmd` inline `<script>` into a dedicated module.
- Keep behavior parity (sidebar toggle, mobile drawer, overlay close).

Deliverables:
- `js/home.js`
- `index.qmd` script removal and module hook
- `src/js/global-search.js` and `src/js/metrics.js` inline handler cleanup

### WS2 - Core Layout and Navigation Modernization

- Simplify homepage nav behavior and remove icon `innerHTML` swaps.
- Ensure mobile drawer state model is explicit and keyboard-safe.
- Improve maintainability of repeated toggling logic via reusable functions.

Deliverables:
- Refactored home interactions with reusable helpers
- Updated CSS selectors as needed for state-based toggles

### WS3 - UI Maintainability Guardrails

- Add automated scanner for inline UI anti-patterns:
  - `style="..."`
  - inline `<script>` blocks in key pages
  - inline event handlers (`onclick=`, etc.)
- Enforce baseline budget in CI to prevent regression growth.

Deliverables:
- `config/ui_ux_budget.json`
- `scripts/check_ui_ux_budget.py`
- CI/deploy workflow integration

### WS4 - UX Regression Safety Net

- Add focused E2E checks for:
  - homepage mobile menu open/close behavior
  - global search modal open/close behavior
  - notes workspace open + save flow

Deliverables:
- Playwright test updates under `tests/e2e/`

## Issue Mapping

- Issue A: Inline interaction cleanup and script extraction ([#1138](https://github.com/D-sorganization/AffineDrift/issues/1138))
- Issue B: Homepage/mobile navigation modernization ([#1139](https://github.com/D-sorganization/AffineDrift/issues/1139))
- Issue C: UI anti-pattern budget + CI enforcement ([#1140](https://github.com/D-sorganization/AffineDrift/issues/1140))
- Issue D: UX regression tests for critical flows ([#1141](https://github.com/D-sorganization/AffineDrift/issues/1141))

## Completion Criteria

1. All four issues are implemented and closed.
2. `npm test -- --runInBand` passes.
3. Targeted Python coverage gate passes (existing CI requirement).
4. New UI budget check passes locally and in CI.
5. PR is green and merged to `main`.
