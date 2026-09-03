# CLAUDE.md — AffineDrift

> **GAAI Fleet Member.** GAAI framework installed in `.gaai/`. Read `.gaai/core/GAAI.md` for full governance spec.
> Rules: `@.gaai/core/contexts/rules/base.rules.md` and `@.gaai/project/contexts/rules/project.rules.md`
> All work on `main` branch. PRs target `main`.

## What This Is

Research platform, educational textbook series, and companion website exploring golf swing biomechanics through affine control theory. Content is authored in Quarto (.qmd files) and LaTeX, rendering to HTML and PDF. Combines narrative text, interactive code cells, mathematical visualizations, and executable control-theoretic models.

## Key Directories

- `articles/` — Quarto (.qmd) and LaTeX sources for articles, textbooks, and monographs
- `books/` — Book-length projects and Quarto book sources
- `content/` — Supplementary publication materials and presentation assets
- `models/` — Quarto model pages and generated programming companion catalogs (`models/programming/`)
- `pages/` — Top-level standalone Quarto pages (technology overview, manifesto, etc.)
- `critiques/` — Falsification ledgers, scientific critiques, and peer review records
- `reports/` — Scientific claim audit reports and summaries
- `resources/` — Interactive simulations, bibliography viewer, and learning paths
- `src/` — Python source code (`affine_control`, `golf_simulation`, `tangent_models`, `core`, `tools`)
- `scripts/` — Content gates, validators, code generators, and CI maintenance scripts
- `tools/` — Developer tooling and MATLAB quality utilities
- `tests/` — pytest (Python), Jest (JavaScript), and Playwright browser test suites
- `references/` — BibTeX bibliography databases
- `schemas/` — JSON schemas for companion manifests, falsification atlases, and research readiness
- `css/` — Canonical stylesheets (CSS budget enforced by CI)
- `docs/` — Destination directory for Quarto rendered output (built at deploy time)
- `config/` — Quality budgets, terminology baselines, and tree parity baselines

## Python and Tooling

- **Python 3.12**. Use `python3`.
- **Formatter:** Black (NOT Ruff format). **100-char line limit.**
- **Linter:** Ruff check.

## Development Commands

```bash
python3 -m ruff check .                               # lint
python3 -m black --check --line-length 100 .           # format check (Black!)
python3 -m black --line-length 100 .                   # auto-format
python3 -m pytest --cov                                # Python tests (floor: pyproject fail_under)
npx jest                                               # JavaScript tests
npx playwright test                                    # E2E browser tests
quarto render                                          # build the site
```

## Docker (Reproducible Environment)

Use Docker to get an environment that exactly matches CI — Python 3.12, Quarto, and Node.js 20 pre-installed.

```bash
# Build the dev image (includes all Python + JS deps)
docker build --target dev -t affinedrift:dev .

# Run pytest (default CMD)
docker run --rm affinedrift:dev

# Run Jest tests
docker run --rm affinedrift:dev npm test

# Run a shell inside the dev container
docker run --rm -it affinedrift:dev bash

# Build and serve the rendered site locally (production image)
docker build -t affinedrift:latest .
docker run --rm -p 8080:8000 affinedrift:latest
# Visit http://localhost:8080

# Or use docker-compose (wraps the production image)
docker compose up
```

The `dev` stage is the entry point for new contributors: it avoids installing Quarto, Python 3.12, and Node.js locally.

## CI Requirements (All Must Pass)

1. `ruff check` — zero violations
2. `black --check --line-length 100` — zero diffs (NOT ruff format)
3. CSS budget validation — stylesheet sizes within configured limits
4. Bibliography quality check — BibTeX well-formed, no broken refs
5. DRY adoption tracking — duplication metrics monitored
6. Module size budget — enforced per-file
7. pytest coverage at or above the single `fail_under` floor in `pyproject.toml` — coverage must not decrease
8. Jest — all JS tests pass (`js-tests` feeds the fan-in `quality-gate`)
9. Playwright E2E — full-site render, every spec on Chromium, per-route axe-core (`e2e-tests` feeds `quality-gate`)
10. CSS mirror enforcement — `css/` must be mirrored in `docs/` (never edit `docs/` CSS directly)
11. No `print()` in `src/` — use logging
12. No TODO/FIXME unless tied to a tracked GitHub issue

## Content Authoring

- Write in `.qmd` using Quarto markdown. Executable cells use `{python}` or `{javascript}` fenced blocks.
- Cross-references: `@sec-`, `@fig-`, `@eq-` syntax. New chapters need an entry in `_quarto.yml`.
- Bibliography: add entries to references dir, cite with `[@key]`.
- Images must have alt text. Math uses MathJax/KaTeX.

## Known Constraints

- **Black with 100-char lines.** Do not configure or run `ruff format` in this repo.
- **Quarto rendering** is slow (~14 min full site on the fleet runner); the E2E lane renders the full site when site-facing files change. The Quarto version is pinned once in `.quarto-version`.
- **Playwright** requires `npx playwright install` for browser binaries before first run.
- **CSS lives in two places:** edit in `css/`, CI validates that `docs/` mirrors match. Never edit rendered CSS directly.

## Logging Standard

**Source Code (src/):** Logging only. `print()` is forbidden.

```python
import logging
logger = logging.getLogger(__name__)
logger.info("message")  # Use for diagnostics
```

**Scripts & Tools:** May use `print()` for user-facing output; use logging for diagnostics.

**Tests:** Logging for diagnostics; print acceptable for test formatting.

See `.logging-standard.md` for full details.

## Coding Standards (Enforced by CI and QA)

- **DRY:** CI tracks duplication. Extract shared Quarto includes and Python utilities. No copy-paste between chapters. Reusable patterns go in `src/tools/utils/` (see `.dry-improvements.md`).
- **DbC:** Validation functions check inputs, raise clear errors with context.
- **LOD:** No method chains >2 levels. Keep rendering logic separate from content logic. Complex Python goes in importable modules, not inline in QMD.
- **TDD:** New Python utilities need pytest tests. New interactive features need Jest tests. Coverage stays above the `pyproject.toml` floor.

## Cross-Repo Dependencies

- **Programming Companion Consumer:** AffineDrift acts as an immutable companion consumer for upstream fleet packages (`src/affine_control/programming_companion/`). It consumes, validates, and pins schemas and manifests published by upstream fleet repositories (such as `UpstreamDrift`), verifying SHA-256 digests and cryptographic/schema provenance without arbitrary runtime imports.
- Shared engineering principles (DRY tracking, module budgets, root hygiene) are consistent across the fleet.

## Slash Commands

- `/gaai-deliver` — Run Delivery Loop for next ready backlog item
- `/gaai-status` — Show current backlog and memory state

## Specification

This repository's specification is defined in `SPEC.md` at the repo root.
Read SPEC.md before making any changes. Update it when your changes
affect documented functionality, features, or architecture.

## Hook bypass policy

**Never use `git commit --no-verify` or `git push --no-verify` unless the hook itself is broken** (tooling not installed, hook script crashes). It is _not_ an acceptable workaround for a hook that flags real issues.

### When a hook fails on something you didn't touch

The hook is scoped to _your diff_. If `fleet-fast-guardrails` or any other guardrail reports a violation in a file you didn't change, that's a regression — file an issue against `Repository_Management`. Bypassing locally doesn't help: the same checks run in CI's `quality-gate` and will block the PR.

### When the hook is legitimately broken

Open an issue in `Repository_Management`. If you must bypass once to land an urgent fix, include the hook error in the commit body and link the tracking issue. **Do not normalize `--no-verify` as a workaround.**

### Enforcement

Branch protection requires the CI `quality-gate` check on every PR. That check runs the same lint, format, type, and security gates as the hooks. `--no-verify` only delays feedback — it cannot land code that would have failed the hook.

For the canonical hook contract, see [`Repository_Management/docs/FLEET_HOOK_STANDARDS.md`](https://github.com/D-sorganization/Repository_Management/blob/main/docs/FLEET_HOOK_STANDARDS.md).
