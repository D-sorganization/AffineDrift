# AffineDrift build pipeline
#
# Current build strategy:
#   - css/ and js/ are the canonical source directories
#   - _site/css/ and _site/js/ are mirrors enforced by sync_frontend_assets.py
#   - Quarto renders *.qmd → _site/*.html (run: quarto render)
#
# Usage:
#   make build       Sync canonical assets to _site/ mirrors
#   make check       Verify no drift between canonical assets and mirrors
#   make lint        Run CSS and HTML linters
#   make test        Run unit and integration tests
#   make all         build + check + lint

.PHONY: all build check lint test security

all: build check lint

build:
	python3 scripts/sync_frontend_assets.py

check:
	python3 scripts/sync_frontend_assets.py --check

lint:
	npm run lint:css

test:
	python3 -m pytest tests/ --cov=src
	npm test -- --coverage

security:
	bandit -r src/ -c pyproject.toml
	pip-audit
