# Geometry of Motion Series Architecture and Progress Tracking

## Scope

This document is the master architecture and execution tracker for the textbook series. It maps each open issue to concrete deliverables and the repository locations that implement them.

## Series Structure

- Volume 0: mathematical primer and appendices
- Volume I: tangent-space methods for nonlinear control
- Volume II: transverse control and trajectory architecture
- Volume III: biomechanics from biology to systems
- Volume IV: human motor control and computational principles

## Canonical Source Layout

- LaTeX manuscripts: `articles/The_Geometry_of_Motion/Volume_*/`
- Website book pages: `books/*.qmd`
- Executable chapter notebooks: `notebooks/geometry_of_motion/`
- Shared tools and validators: `src/tools/`
- CI workflows: `.github/workflows/`

## Open-Issue Tracker

| Issue | Theme | Primary Deliverable Path | Status |
| --- | --- | --- | --- |
| #1267 | Executable chapter bridge | `notebooks/geometry_of_motion/` | In progress |
| #1268 | Continuous LaTeX CI/CD + releases | `.github/workflows/latex-release-volumes.yml` | In progress |
| #1269 | RL and funnel benchmark | `src/tools/trajectory_cost_benchmark.py` | In progress |
| #1274 | Volume 0 expansion | `articles/The_Geometry_of_Motion/Volume_0/` | Planned |
| #1275 | Volume 0 Python implementations | `articles/The_Geometry_of_Motion/Volume_0/` and `src/` | Planned |
| #1276 | Volume I worked implementations | `articles/The_Geometry_of_Motion/Volume_I/` and `notebooks/` | Planned |
| #1280 | DOF/curse of dimensionality thread | Volumes I-IV chapters | Planned |
| #1281 | Multi-representation treatment | Volumes 0-IV chapters and code | Planned |
| #1282 | UpstreamDrift educational integration | `docs/development/` integration docs | Planned |
| #1283 | Volume II expansion with code | `articles/The_Geometry_of_Motion/Volume_II/` | Planned |
| #1284 | Ideomotor/predictive brain treatment | Volume IV chapters | Planned |
| #1285 | Passive distributed control treatment | Volumes II-IV chapters | Planned |
| #1286 | Appendix expansion | `Volume_0/appendices/` | Planned |
| #1287 | Citation validity and traceability | `src/tools/reference_audit.py` and bibliography files | In progress |
| #1288 | Unified LaTeX style | shared style package under `The_Geometry_of_Motion/` | Planned |
| #1289 | Deduplicate textbook sources | `articles/textbook/` vs `Volume_I/` | Planned |
| #1290 | Master architecture tracking | `docs/development/geometry_of_motion_architecture.md` | Active |
| #1314 | Quarto warning cleanup | targeted article files and tests | In progress |

## Engineering Guardrails

- TDD for each new utility module and workflow checker.
- DbC: every public helper validates preconditions.
- DRY: shared parsing/benchmark helpers live under `src/tools/`.
- CI-first: workflows and validators must be test-backed.
