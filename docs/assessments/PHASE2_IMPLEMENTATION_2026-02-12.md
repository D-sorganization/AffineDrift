# AffineDrift Phase 2 Implementation Log

Date: 2026-02-12
Scope: Follow-up implementation after architecture assessment backlog creation.

## Implemented in This Phase

### Issue #1126 - Simplify and harden Quarto config

- Reduced manual `project.render` enumeration in `_quarto.yml` to:
  - `*.qmd`
  - `articles/**/*.qmd`
- Extracted large inline header block into `_includes/site-head.html`
- Extracted inline footer script block into `_includes/site-after-body.html`
- Kept `mathjax-loader` include explicit in `_quarto.yml`

### Issue #1130 - Stabilize nested render coverage

- Added validation script: `scripts/check_quarto_render_coverage.py`
- Enforced in CI:
  - `.github/workflows/ci-standard.yml`
  - `.github/workflows/deploy-website.yml`

### Issue #1125 - Layout fragility control

- Added CSS budget config: `config/css_quality_budget.json`
- Added budget checker: `scripts/check_styles_budget.py`
  - Guards maximum line count for `styles.css`
  - Guards `!important` count growth
- Enforced in CI:
  - `.github/workflows/ci-standard.yml`
  - `.github/workflows/deploy-website.yml`

### Issue #1129 - Docs artifact governance

- Added policy doc: `docs/development/DOCS_ARTIFACT_POLICY.md`
- Linked and reflected in:
  - `README.md`
  - `docs/development/DEVELOPMENT_GUIDE.md`
  - `docs/development/WEBSITE_MANAGEMENT.md`

## Validation Commands

```bash
python3 scripts/check_quarto_render_coverage.py
python3 scripts/check_styles_budget.py
python3 scripts/sync_frontend_assets.py --check
PYTHONPATH=. python3 src/tools/check_site_health.py --fail-on broken
npm test -- --runInBand
```
