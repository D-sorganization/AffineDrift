# AffineDrift build pipeline
#
# Current build strategy:
#   - css/ and js/ are the canonical source directories
#   - docs/css/ and docs/js/ are mirrors enforced by sync_frontend_assets.py
#   - Quarto renders *.qmd → docs/*.html (run: quarto render)
#
# Usage:
#   make build       Sync canonical assets to docs/ mirrors
#   make check       Verify no drift between canonical assets and mirrors
#   make lint        Run CSS and HTML linters
#   make test        Run unit and integration tests
#   make all         build + check + lint

.PHONY: all build check lint test

all: build check lint

build:
	python3 scripts/sync_frontend_assets.py

check:
	python3 scripts/sync_frontend_assets.py --check

lint:
	npm run lint:css

test:
	python3 -m pytest tests/ --cov=src --cov-fail-under=50
	npm test -- --coverage
