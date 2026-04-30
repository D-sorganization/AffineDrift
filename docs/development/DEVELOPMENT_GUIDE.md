# Development Guide

## Environment

- Python: `3.12`
- Node.js: `20.x`
- Quarto CLI: required for local site render (`quarto preview`, `quarto render`)

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
```

## Core Validation Commands

```bash
ruff check src tests scripts
npm test -- --runInBand
python3 scripts/sync_frontend_assets.py --check
python3 scripts/check_quarto_render_coverage.py
python3 scripts/check_styles_budget.py
python3 src/tools/check_site_health.py --fail-on broken
```

## Notes

- `docs/` contains tracked build outputs for GitHub Pages.
- Canonical frontend asset sync is enforced by `scripts/sync_frontend_assets.py`.
- Quarto recursive render coverage is enforced by `scripts/check_quarto_render_coverage.py`.
- CSS growth and `!important` usage are constrained by `scripts/check_styles_budget.py`.
- If Quarto-generated outputs are updated, rerun health checks before commit.
