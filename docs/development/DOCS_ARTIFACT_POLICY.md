# Docs Artifact Policy

`docs/` is the GitHub Pages output directory and contains generated site artifacts.

## Source of Truth

- Content source: `*.qmd` and `articles/**/*.qmd`
- Frontend source: `styles.css`, `css/*.css`, `js/*.js`
- Build config source: `_quarto.yml`, `_includes/*.html`

## Generated Artifacts

- Generated HTML lives under `docs/**/*.html`
- Generated mirrors (for deployed static assets) live under `docs/css` and `docs/js`

## Update Rules

1. Update source files first.
2. Run sync and health checks:
   - `python3 scripts/sync_frontend_assets.py`
   - `python3 scripts/check_quarto_render_coverage.py`
   - `python3 src/tools/check_site_health.py --fail-on broken`
3. Commit any resulting `docs/` artifact updates together with source changes.

## Guardrails

- CI enforces:
  - frontend mirror drift check
  - Quarto render coverage check
  - CSS budget check on `styles.css`
  - broken-link blocking check
