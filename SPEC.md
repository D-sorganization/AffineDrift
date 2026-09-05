# SPEC.md — Repository Specification Document

Last-Updated: 2026-09-03T09:00:00Z

## 1. Identity

| Field                   | Value                                            |
| ----------------------- | ------------------------------------------------ |
| **Repository Name**     | `AffineDrift`                                    |
| **GitHub URL**          | `https://github.com/D-sorganization/AffineDrift` |
| **Owner**               | D-sorganization                                  |
| **Primary Language(s)** | Python 3.12, JavaScript ES6+, Quarto             |
| **License**             | MIT                                              |
| **Current Version**     | 1.0.9                                            |
| **Spec Version**        | 1.0.290                                          |
| **Last Spec Update**    | 2026-09-03                                       |

## 2. Purpose & Mission

AffineDrift is a research platform that explores golf swing biomechanics through the lens of affine control theory. The project combines rigorous mathematical modeling with interactive educational content, publishing research-quality materials via a Quarto-based website hosted on GitHub Pages. It demonstrates how differential dynamic programming and iterative linear-quadratic regulation (iLQR) can optimize swing trajectories, while serving as an educational bridge between control theory and biomechanics for the broader scientific community.

## 3. Goals & Non-Goals

### Goals

- Model golf swings as affine controllable systems with mathematical rigor, enabling trajectory optimization via iLQR.
- Publish research-quality educational content via Quarto website (AffineDrift.com) on GitHub Pages with revision-bound route validation.
- Model golf-ball flight with velocity-dependent drag and spin-dependent Magnus lift using standard aerodynamic formulations.
- Maintain property-based testing (Hypothesis) and test coverage at or above the single floor declared in `pyproject.toml` (`[tool.coverage.report] fail_under`, currently 75%) across all critical modules.
- Present planar models within a declared model ladder; withhold quantitative 2D-to-3D claims without governed comparative datasets.
- Maintain mechanical-claim contracts keeping generalized torque distinct from power, energy, tissue load, and muscle force.
- Maintain normative induced-acceleration attribution records declaring model, coordinates, frame, contact constraints, and identifiability.
- Require executable ZTCF results to carry versioned, fail-closed intervention records freezing model authority and boundary states.
- Maintain schema-validated scientific trust panels binding accessible summaries to bounded claims, falsifiers, and uncertainty.
- Maintain fail-closed Drift-Control Ratio (DCR) validation protocols and versioned claim/critique adjudication ledgers.
- Publish evidence-linked companions to the proximal-distal technical treatment with explicit model and hypothesis boundaries.
- Pin upstream momentum-transfer agendas, timing-policy viability, and typed-slack identifiability evidence to immutable upstream commits.
- Maintain textbook bibliographies, citation integrity, and consistent algorithm notation across the series.
- Keep long-form mechanics and paired textbook arguments consistent about inverse dynamics, constraint reactions, impedance, finite-horizon control, and impact vector geometry; bind numerical examples to independently checked identities and distinguish model predictions from human evidence.
- Publish technology overviews covering launch-monitor qualification, force measurement, and markerless motion capture.
- Enforce strict repository root hygiene with an explicit allowlist gating pull requests.

### Non-Goals

- Not a production game engine (QuatEngine serves that purpose).
- Not a real-time physics simulator (UpstreamDrift provides real-time simulation).
- Not a general-purpose mathematics library.

## 4. Architecture Overview

### System Context

AffineDrift operates as an educational and publication platform within the D-sorganization fleet. Its site build and local solvers have no runtime or import dependency on external game engines. Cross-repository publications maintain a governed evidence dependency: UpstreamDrift owns executable models, scientific claims, and release records, while AffineDrift publishes explanatory and immutable projections from exact protected provider revisions. AffineDrift acts as an immutable companion consumer (`src/affine_control/programming_companion/`), validating schemas and manifests published by upstream fleet repositories without arbitrary runtime imports.

### Markerless Mocap Publication Boundary

AffineDrift owns public pedagogy, sanitized visualization, compatibility reporting, and immutable evidence projection for the cross-repository markerless mocap program. It does not own or import camera capture, synchronization, calibration, pose inference, reconstruction, or session orchestration runtime.

The versioned `affinedrift/mocap-publication-projection/v1` contract accepts only qualified Tools or UpstreamDrift releases pinned by commit and SHA-256. The executable verifier rejects moving branch links, raw video, PII, secrets, incompatible licenses, unqualified claims, and missing artifacts.

### Markerless Mocap Camera Evidence Registry

`data/markerless_mocap/camera_evidence_registry_v1.json` is the canonical AffineDrift camera-selection evidence surface. The strict `affinedrift/mocap-camera-evidence-registry/v1` schema requires dated primary sources, explicit evidence classes, review expiry, and default-deny procurement.

The public guide at `articles/markerless-mocap-camera-selection.qmd` records shop evaluations for cameras (FLIR BFS-U3-16S2C-CS, Basler a2A1920-160ucBAS, Allied Vision Alvium, LUCID Triton2, ZED X One GS) scoped strictly to camera bodies. Tools owns camera adapters; UpstreamDrift owns physical qualification and operator workflows.

### Module Map

```
AffineDrift/
├── src/
│   ├── affine_control/          # Swing optimization, control algorithms, companion consumer
│   ├── core/                    # Constants, contracts (DbC), optimizers (iLQR), protocols
│   ├── tangent_models/          # Tangent space and hyperplane mathematical methods
│   ├── golf_simulation/         # Ball flight, clubs, course, putting, terrain simulation
│   └── tools/                   # CI/CD utilities, site health, and code quality checkers
├── scripts/                     # Content gates, validators, generators, and CI scripts
├── articles/                    # Research articles, Quarto (.qmd), and LaTeX source books
├── books/                       # Comprehensive textbook projects
├── content/                     # Supplementary publication materials and presentations
├── models/                      # Quarto model pages and generated programming catalogs
├── critiques/                   # Falsification ledgers, scientific critiques, and peer review
├── reports/                     # Claim audit reports and verification summaries
├── resources/                   # Interactive simulations, bibliography viewer, learning paths
├── schemas/                     # Strict JSON schemas for contracts, manifests, and registries
├── references/                  # Canonical BibTeX bibliography databases
├── tests/                       # Pytest, Jest, and Playwright test suites
├── css/                         # Canonical stylesheets (CSS budget enforced)
├── docs/                        # Quarto rendered output directory (built at deploy time)
├── config/                      # Quality budgets, terminology baselines, tree parity
└── .github/workflows/           # 12 active CI/CD and governance workflows
```

### Key Components

| Component             | Location                                    | Purpose                                                                |
| --------------------- | ------------------------------------------- | ---------------------------------------------------------------------- |
| Swing Optimizer       | `src/affine_control/swing_optimizer.py`     | iLQR-based trajectory optimization for golf swings                     |
| DDP Mock              | `src/affine_control/ddp.py`                 | DDP mock placeholder; iLQR is the active optimizer                     |
| Companion Consumer    | `src/affine_control/programming_companion/` | Immutable consumer for upstream companion packages and manifests       |
| Core Optimizers       | `src/core/optimizers/`                      | iLQR solver implementations (`ilqr_solver.py`, `optimizer_factory.py`) |
| Design Contracts      | `src/core/contracts/`                       | Design-by-contract assertions (`definitions.py`, `validators.py`)      |
| Golf Simulation       | `src/golf_simulation/`                      | Aerodynamic ball flight, clubs, course, terrain, and putting physics   |
| Tangent Models        | `src/tangent_models/`                       | Tangent space and hyperplane mathematical abstractions                 |
| Root Hygiene Checker  | `scripts/check_root_hygiene.py`             | Validates root allowlist and blocks untracked/stray clutter            |
| Site Health Monitor   | `src/tools/check_site_health.py`            | Automated website health and performance checks                        |
| Code Quality Analyzer | `src/tools/code_quality_check.py`           | AST-based Python code quality analysis                                 |
| Rotation Converter    | `js/rotation-converter.js`                  | Interactive 3D rotation visualization and converter                    |

## 5. Desired Functionality

### Core Features

| #   | Feature                                 | Status | Description                                                                                                                                                                                                                                                                  |
| --- | --------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | Quarto Website Rendering and Deployment | ✅     | Renders Quarto markdown (.qmd) and LaTeX into static HTML/PDF; deploys to GitHub Pages.                                                                                                                                                                                      |
| F2  | Affine Control Theory Swing Optimizer   | ✅     | Implements iLQR solver with backward pass, regularization, and line search.                                                                                                                                                                                                  |
| F3  | Tangent Space and Hyperplane Models     | ✅     | Mathematical models for tangent space methods with educational examples.                                                                                                                                                                                                     |
| F4  | Interactive JavaScript Visualizations   | ✅     | Rotation converter, search interface, and mathematical visualization components.                                                                                                                                                                                             |
| F5  | Mathematical Notation Rendering         | ✅     | MathJax and KaTeX support for rendering LaTeX equations in web content.                                                                                                                                                                                                      |
| F6  | Property-Based Testing with Hypothesis  | ✅     | Property-based testing for physics and numerical solvers across parameter spaces.                                                                                                                                                                                            |
| F7  | CSS Budget Enforcement                  | ✅     | Automated CI enforcement of stylesheet size limits to maintain performance.                                                                                                                                                                                                  |
| F8  | Mirror Validation                       | ✅     | Ensures duplicate stylesheets and assets match canonical versions across the codebase.                                                                                                                                                                                       |
| F9  | GitHub Actions Automation               | ✅     | 12 production workflows with third-party actions pinned to immutable commit SHAs.                                                                                                                                                                                            |
| F10 | Progressive Web App Support             | ✅     | Service worker and web manifest for offline access and installability.                                                                                                                                                                                                       |
| F11 | Textbook Compilation Pipeline           | ✅     | Compiles LaTeX books with latexmk, strict error stops, and page-count floors.                                                                                                                                                                                                |
| F12 | Textbook Claim Guardrail                | ✅     | CI blocks unsupported quantitative claims in textbook content without citations.                                                                                                                                                                                             |
| F13 | PR Site Build & Dependency Audit        | ✅     | Checks coverage, runs `pip-audit`, validates sitemap, and executes Playwright smoke tests.                                                                                                                                                                                   |
| F14 | Bibliography Duplicate-Alias Guardrail  | ✅     | Reference-integrity tests require duplicate bibliography records to carry compatibility notes.                                                                                                                                                                               |
| F15 | Bibliography Synchronization            | ✅     | Synchronizes chapter-level citations with shared references in `references/affine-drift.bib`.                                                                                                                                                                                |
| F16 | Citation Resolution Guardrail           | ✅     | CI validates that all QMD citation keys map to known entries in configured .bib files.                                                                                                                                                                                       |
| F17 | Textbook Algorithm Convention Sharing   | ✅     | Shared algorithm and pseudocode style macros across textbook volumes.                                                                                                                                                                                                        |
| F18 | Verified Container Build Inputs         | ✅     | Pins Python base image, verifies Quarto checksum, and generates build provenance records.                                                                                                                                                                                    |
| F19 | Script CLI Output Contracts             | ✅     | Maintenance scripts route terminal output through `scripts/cli_output.py`.                                                                                                                                                                                                   |
| F20 | Stimpmeter-Calibrated Putting Physics   | ✅     | Putting roll simulation sharing USGA Stimpmeter deceleration models.                                                                                                                                                                                                         |
| F21 | Opt-In Performance Benchmark Suite      | ✅     | `benchmarks/` provides pytest-benchmark timing checks for stable computational paths.                                                                                                                                                                                        |
| F22 | Distributed Review Guard                | ✅     | `block-self-merge.yml` blocks PR authors from self-approving changes.                                                                                                                                                                                                        |
| F23 | Programming Companion Consumer          | ✅     | Validates and pins immutable upstream companion packages and manifests from UpstreamDrift.                                                                                                                                                                                   |
| F24 | Software Freshness Dashboard            | ✅     | `data/companion/pins.json` + generated `/models/programming/freshness.html`; every UpstreamDrift SHA linked from the site is reconciled by `scripts/check_companion_pins.py`, which respects `_quarto.yml` render exclusions and resolves include partials to the rendered pages that publish them (#4027, #4123, #4142, #4145). |
| F24 | Scientific Claim-Audit Inventory        | ✅     | Governed route classification, digest binding, and audit reports for all public claims.                                                                                                                                                                                      |
| F25 | Repository Root Hygiene Enforcement     | ✅     | CI quality gate (`scripts/check_root_hygiene.py`) enforces strict root allowlist.                                                                                                                                                                                            |

## 6. Data & Configuration

### Input & Output Data

- **Input**: Swing trajectories (YAML/JSON), Quarto Markdown (.qmd), LaTeX book sources (.tex), configuration parameters (`_quarto.yml`).
- **Output**: Optimized swing trajectories (NumPy/JSON), static website (HTML/CSS/JS in `docs/`), test and coverage reports (`coverage.xml`), claim-audit reports.

### Configuration

- **Quarto** (`_quarto.yml`): Output directory `docs`, theme, navigation dropdowns (`Read`, `Technology`, `Build`, `Connect`), MathJax/KaTeX configuration.
- **Python** (`pyproject.toml`): Python 3.12, 100-character line length (Black), Ruff lint rules, Mypy type-checking, pytest configuration.
- **Root Allowlist** (`scripts/check_root_hygiene.py`): Enforces allowed files and directories in repository root.

## 7. Testing Specification

### Strategy & Requirements

AffineDrift follows a test pyramid: fast unit tests, integration tests, property-based tests (Hypothesis), JavaScript tests (Jest), and browser end-to-end tests (Playwright).

- Minimum `src/` coverage: the `pyproject.toml` `fail_under` floor (75%; measured 92.6% on 2026-09-03), enforced by `pytest --cov=src` — no CLI ever restates the number (#4126).
- Critical physics and optimization modules maintain >=70% coverage.
- Code quality gates: `ruff check .`, `black --check --line-length 100 .`, `mypy .`.

### Required Scenarios

- [x] iLQR solver converges and produces lower-cost trajectories than zero-control rollout.
- [x] Quarto website renders without build errors and passes title, math, and cross-reference checks.
- [x] CSS budgets and stylesheet mirror parity pass validation.
- [x] Website citations resolve against configured BibTeX files.
- [x] Playwright smoke tests pass on desktop and mobile viewports.
- [x] Programming companion consumer validates manifests and rejects conflicting/unverified packages.
- [x] The active pin is the provider-published, attested `upstreamdrift-companion-<sha>` artifact (`data/companion/active-lock.json` + `acquisition.json`); `models/programming/*` regenerate from it, never from the fixture, while a pin exists.
- [x] Root hygiene allowlist passes with zero untracked or forbidden artifacts.

## 8. Quality Standards

- **Code Quality Tools**: Ruff (linting), Black (formatting at 100 chars), Mypy (type checking), Pytest (testing), Jest (JS), Playwright (E2E).
- **Design Principles**: Test-Driven Development (TDD), Design by Contract (DbC), Don't Repeat Yourself (DRY), Law of Demeter (LoD).
- **Logging**: Use `logging` in `src/`. `print()` is forbidden in application code.

## 9. Dependencies

- Quarto 1.8.26, pinned once in `.quarto-version` (CI, deploy-website.yml, and the Dockerfile read it; #4126).

- **Runtime**: `numpy>=2.0.0`, `scipy>=1.14.0`, `matplotlib>=3.9.0`, `pydantic>=2.8.0`, `PyYAML>=6.0.1`, `requests>=2.32.0`, `beautifulsoup4>=4.12.0`.
- **Development**: `pytest>=8.0.0`, `pytest-cov>=5.0.0`, `hypothesis>=6.100.0`, `ruff>=0.5.0`, `black>=24.0.0`, `mypy>=1.10.0`.
- **Fleet Dependencies**: UpstreamDrift (governed evidence provider for executable models, companion manifests, and benchmark releases).

## 10. Deployment & Operations

### Build & Test Commands

```bash
# Lint and format checks
ruff check .
black --check --line-length 100 .
mypy src/ scripts/

# Run tests and root hygiene
pytest tests/ --cov=src
python scripts/check_root_hygiene.py

# Render Quarto website
quarto render
```

### Build Artifacts

Static website in `docs/`, public site manifest (`docs/public-site-manifest.json`), coverage report (`coverage.xml`), and claim-audit inventory reports.

## 11. Roadmap & Open Issues

- **Active Development**: Maintain coverage above the `pyproject.toml` floor, refine affine swing optimization models, expand educational textbook materials.
- **Current Priorities**: Complete programming companion consumer integration (#4022-#4030), maintain root hygiene allowlists (#4128), execute reader validation protocols (#4088).
- **Known Boundaries**: Real-time simulation is delegated to UpstreamDrift; DDP backward pass is a gated mock; markerless mocap runtime capture is external.

## 12. Change Log

Rows are keyed by pull request, not by a serial spec version: `| YYYY-MM-DD | #<pr> | summary |`. Add exactly one row for your own pull request and do not renumber anybody else's; the `Spec Version` field in section 1 is bumped at release time by `scripts/bump_spec_version.py`, never by an individual pull request. See [Repository_Management#1520](https://github.com/D-sorganization/Repository_Management/issues/1520).

The `Archived entry (spec X.Y.Z)` paragraphs below are frozen: they are the pre-#1520 serial-versioned narrative entries, kept verbatim for traceability. Do not add new ones — new detail goes in the row summary or the pull request.

| Date       | PR    | Changes    |
| ---------- | ----- | ---------- |
| 2026-09-05 | #4183 | Derive valid phase coordinates, virtual constraints, input authority, internal dynamics, active power, and hybrid contact conditions; synchronize four editions, rebuild three PDFs, and connect coordination to golf impact under #4177. |
| 2026-09-05 | #4182 | Derive nonlinear funnel invariance, progress and impact conditions, robust and SOS certificate limits, continuous-time verification, and output-sensitive geometry; synchronize four editions, rebuild three PDFs, and add independently checked examples under #4175. |
| 2026-09-05 | #4178 | Correct trajectory objectives, free-time scaling, PMP signs, numerical feasibility, and impact uncertainty in four editions; rebuild three PDFs and repair long-chapter visibility under #4173 and #4176; accept valid starred LaTeX operators without weakening corruption checks under #4181. |
| 2026-09-05 | #4174 | Correct orbital stability, transverse coordinates, Floquet limits, hybrid timing, transient growth, event outcomes, and LQR tube conditions; synchronize four editions, rebuild three PDFs, and add checked examples under #4171. |
| 2026-09-05 | #4172 | Correct configuration manifolds, force covectors, rotation singularities, kinetic geometry, passive energy, and attitude-control frames; synchronize four editions, rebuild three PDFs, and add reproducible checks under #4169. |
| 2026-09-05 | #4170 | Derive curve geometry, physical force, constrained timing, moving frames, and transverse dynamics with reproducible counterexamples; synchronize four editions, rebuild three PDFs, and qualify golf inference under #4168. |
| 2026-09-05 | #4167 | Rebuild motion-control foundations around impact outcomes, feasible trajectories, timing, metrics, stability, and robust tubes; correct repeated input-rank claims, synchronize four editions, rebuild four PDFs, and add reproducible examples under #4166. |
| 2026-09-05 | #4165 | Correct aerodynamic force and inverse-dynamics signs, distributed shaft loads, air-relative power, reproducible forward counterfactuals, ball flight, and environmental sensitivity; synchronize print/web, regenerate the PDF, add numerical checks and a shared plot, and remove an unverified reference under #4164. |
| 2026-09-05 | #4163 | Rebuild the long inverse-dynamics chapter with complete spatial recursion, measurement rank, calibrated sensors, muscle-inference scope, uncertainty, and forward counterfactuals; synchronize print/web and correct incoming explanations under #4161. |
| 2026-09-05 | #4162 | Rebuild the Physics parallel-mechanisms chapter with correct closure rank, load identification, hand/ground wrench and energy balances; synchronize print/web, add a shared graph and numerical checks, and correct two repeated spine-loop statements under #4160. |
| 2026-09-05 | #4153 | Correct long-form mechanics, inverse dynamics, optimal control, passive stabilization, impact, underactuation, variational residuals, constrained geometry, and superposition; synchronize paired editions, regenerate five PDFs, and document the continuing corpus audit under epic #4009. |
| 2026-09-05 | #4159 | Correct the contraction reference's metric and Riccati certificates, optimization, muscle/task dynamics, noise, and hybrid-event treatment; regenerate paired LaTeX, add reproducible counterexamples, and preserve historical critique context under #4158. |
| 2026-09-05 | #4146 | chore(spec): re-vendor spec-changelog helpers and worktree-relative merge driver installer from Repository_Management (#4146) |
| 2026-09-03 | #4144 | fix(companion, #4142): resolve companion pin routes through Quarto includes so `scripts/check_companion_pins.py` maps underscore-prefixed partials to the rendered pages that transitively include them, unblocking the `Deploy Website` job and the generated freshness dashboard |
| 2026-09-03 | #1520 | Key SPEC.md change-log rows by pull request instead of the next free serial spec version; add `scripts/check_spec_changelog.py` and `shared_scripts/spec_changelog.py`; make `Spec Version` release-derived via `scripts/bump_spec_version.py`; register the `spec-rows` union merge driver |
| 2026-09-02 | #4128 | Governance and Root Hygiene Cleanup (spec 1.0.288) |
| 2026-09-01 | #4104 | Live-Only Observable Retry Closure (spec 1.0.278) |
Archived entry (spec 1.0.288): Governance and Root Hygiene Cleanup (#4128)

Removes root sprawl, stray and duplicate agent assets, and deprecated review files.
Enforces an explicit repository root allowlist via `scripts/check_root_hygiene.py`.
Relocates historical changelog entries to `CHANGELOG.md` and updates `CLAUDE.md` to
accurately describe the repository layout and the immutable companion consumer role.

Archived entry (spec 1.0.278): Live-Only Observable Retry Closure

Corrects the first #4104 implementation without changing the site or its
scientific content. Local and pre-deployment verification again default to one
attempt; only the revision-matched live gate opts into two retries.

> For the complete historical change log (v1.0.173 – v1.0.278), see [CHANGELOG.md](CHANGELOG.md).
