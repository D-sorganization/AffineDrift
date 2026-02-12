# Website Management

## Content Workflow

1. Update source `.qmd`, `styles.css`, or canonical assets under `css/` and `js/`.
2. Keep mirrored frontend assets synchronized:
   - `python3 scripts/sync_frontend_assets.py`
3. Validate config and CSS guardrails:
   - `python3 scripts/check_quarto_render_coverage.py`
   - `python3 scripts/check_styles_budget.py`
4. Render locally (when Quarto is available):
   - `quarto preview`
   - `quarto render`
5. Validate generated output:
   - `python3 src/tools/check_site_health.py --fail-on broken`

## Frontend Asset Policy

- Canonical roots:
  - `css/*.css`
  - `js/*.js`
  - `styles.css`
- Mirrored targets in `src/` and/or `docs/` are managed by sync script.
- Known intentional divergence is documented in `scripts/sync_frontend_assets.py`.

## Artifact Policy

- See `docs/development/DOCS_ARTIFACT_POLICY.md` for source-of-truth and commit rules.

## Deployment

- CI quality gate: `.github/workflows/ci-standard.yml`
- Website deployment: `.github/workflows/deploy-website.yml`

## Troubleshooting

- If site health reports broken links, fix source links in `.qmd` first, then ensure tracked `docs/*.html` outputs are updated.
- If sync check fails, run `python3 scripts/sync_frontend_assets.py` and commit the mirrored file updates.
