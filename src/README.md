# `src` Overview

## Purpose

Primary Python source tree for AffineDrift tooling, modeling code, and validation utilities. This code supports the website but is **not part of the website content itself** — it provides build-time tools, CI scripts, and physics simulation code.

## Relationship to Website Content

The `src/` directory contains backend tooling, not frontend content. Specifically:

| Directory             | Purpose                                                      | Relationship to Website                                       |
| --------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- |
| `src/tools/`          | CI/CD utilities (link checker, site health, LaTeX converter) | Used by CI pipeline, not rendered to website                  |
| `src/affine_control/` | Physics simulation code for golf swing dynamics              | Powers simulations; results may appear as figures in articles |
| `src/tangent_models/` | Tangent space method implementations                         | Research code; not directly rendered                          |
| `src/core/`           | Shared utilities (math, numerical methods)                   | Used by other modules                                         |
| `src/css/`, `src/js/` | Alternative frontend asset copies                            | See note below                                                |

**Note on `src/css/` and `src/js/`:** These directories contain alternative/development versions of the CSS and JS assets. The canonical versions served by the website are in the root `css/`, `js/` directories. The `src/css/` and `src/js/` versions may be more up-to-date; reconciling these is tracked in issue #1425.

## Implementation Status

- Core modules are active and exercised by CI.
- Tooling modules in `src/tools/` provide health checks and conversion utilities.

## Known Gaps

- Some subpackages still need richer usage docs and reproducible examples.
- `src/css/` vs root `css/` divergence (tracked in issue #1425)
