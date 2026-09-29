# Codemap — AffineDrift

This is the local navigation guide `AGENTS.md`'s fleet-managed "Repo Context
& Codemap Freshness" section points agents to. It does not replace the
architecture map; it tells you where things live and where the map itself is
kept current.

## Where the Architecture Map Lives

AffineDrift's structural map is
[`docs/architecture/C4.md`](architecture/C4.md): a Mermaid C4 System Context
view, a Container view, a Feature Map (capability → component → test
evidence), and an Architecture Change Log. It is not a static artifact —
`scripts/architecture_map_contract.py` validates its structure and
`.github/workflows/architecture-map-contract.yml` runs that validator plus
`tests/test_architecture_map_contract.py` on every PR that touches the map,
the validator, or its tests. Start there for "what talks to what" and for the
capability-to-code table.

## Directory Map

| Path | What's there |
| --- | --- |
| `src/affine_control/` | Core trajectory optimization (iLQR/DDP), dynamics, drift-control ratio analysis, falsification atlas, evidence presentation |
| `src/golf_simulation/`, `src/tangent_models/`, `src/core/`, `src/tools/` | Simulation, tangent-model, and shared core/tooling Python packages |
| `articles/`, `books/` | Quarto (`.qmd`) and LaTeX sources for textbooks, monographs, and articles |
| `content/`, `pages/`, `models/` | Presentation assets, standalone Quarto pages, and model pages |
| `critiques/`, `reports/` | Falsification ledgers, scientific critiques, and claim audit reports |
| `resources/` | Interactive simulations, bibliography viewer, learning paths |
| `references/`, `schemas/` | BibTeX bibliography databases; JSON schemas for manifests and atlases |
| `scripts/` | Content gates, validators, code generators, CI maintenance scripts |
| `tests/` | pytest, Jest, and Playwright suites (`tests/test_architecture_map_contract.py` covers the map itself) |
| `css/` / `docs/` | Canonical stylesheets and Quarto-rendered output (`docs/` is a build destination for HTML, not source — except this codemap and the other `docs/` markdown listed in `AGENTS.md`) |

For the full directory listing and CI requirements, see the "Key
Directories" and "CI Requirements" sections of `CLAUDE.md` / `AGENTS.md` at
the repo root — this file does not duplicate them.

## Refresh Mechanism

- `docs/architecture/C4.md` is enforced by CI on every touching PR (see
  above); it cannot silently go stale on the paths it watches.
- This file (`docs/codemap.md`) and the directory table above are manual —
  refresh them when a top-level directory in `CLAUDE.md`'s "Key Directories"
  list is added, removed, or repurposed.
- `.codemap/` (a generated local index cache, if a tool creates one) is
  git-ignored and must never be committed; treat it as disposable.

## Agent Discovery Path

1. Read `AGENTS.md` (or `CLAUDE.md`) at the repo root first.
2. Read `docs/architecture/C4.md` for system structure and the
   capability → component → test map.
3. Read this file (`docs/codemap.md`) for directory-level navigation.
4. If `.codemap/` exists locally, treat it as a cache — verify important
   claims against source before relying on it.
5. Fall back to `rg`/`grep` and direct file reads for anything not covered
   above, and report the gap rather than guessing.
