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
| 2026-09-10 | #4332 | Correct paired muscle-force models, activation, tendon energy and control inference with independently checked examples and figures. |
| 2026-09-10 | #4330 | Correct both motor-learning editions with distinct error models, bounded golf evidence, paired figures and worked answers. |
| 2026-09-08 | #4292 | Correct launch-monitor definitions, point and rotation kinematics, temporal uncertainty, vendor evidence, and validation-study interpretation. |
| 2026-09-08 | #4282 | Separate conservative Coriolis coupling from physical damping in the paired Physics of Golf chapter; make the state and energy mappings explicit and correct the two-joint inverse-mass example; verify publication output and integration with current main. |
| 2026-09-07 | #4254 | Replace universal heavy-hit claims with qualified contact/shaft/prestress/acoustic theory, primary-source review, cross-repository capability inventory and falsifiable research epics; add independent publication regressions. |
| 2026-09-07 | #4237 | Reconcile both stability–optimality editions: Riccati proofs and rates, shared checked numerical table, finite-horizon geometry, robustness, disturbance attenuation, estimation and golf evidence; rebuild Volume I and verify print/web. |
| 2026-09-07 | #4235 | Reconcile the complete paired variational chapter: exact remainders, ordered propagation, flow derivatives, adjoint boundary terms, checked pendulum examples, stability and numerical geometry; rebuild Volume I and verify print/web. |
| 2026-09-07 | #4233 | Reconcile all paired Physics of Golf glossary definitions across mechanics, impact, anatomy, tissue and evidence; add collision derivation and verified sources, repair aliases and reading layout, and rebuild the textbook PDF. |
| 2026-09-07 | #4231 | Correct the complete paired superposition chapter, replacing inconsistent mechanics and pendulum tables with independent verification and precise passivity, constraints, actuator and reachability conditions; rebuild Volume I. |
| 2026-09-07 | #4226 | Reconcile multibody motion, reactions, spatial conventions and segment energy through independent executable checks; repair excluded hybrid critique links under #4225 and main-health #4224. |
| 2026-09-07 | #4223 | Reconcile complete hybrid reference, critique and accessible companion through impact mechanics, event-time sensitivity, contact feasibility and executable verification; record full review and layout evidence. |
| 2026-09-07 | #4221 | Reconcile complete applications editions with kinetic-energy-consistent model, versioned rigid counterfactual, verified cross-domain derivations and evidence limits; rebuild affected PDFs and record review scope. |
| 2026-09-07 | #4219 | Correct the full contraction critique, mathematical counterexamples, noise and hybrid assumptions, unsupported evidence and mobile equations; record source and validation scope. |
| 2026-09-07 | #4217 | Complete paired linear-algebra mechanics, temporal control/observation, spectral and inverse-sensitivity derivations; rebuild Volume 0 PDF; improve mobile math and record full review evidence. |
| 2026-09-06 | #4211 | Remediate rotation converter formula and visualisation summary text color contrast for deploy axe accessibility gate (#4211). |
| 2026-09-06 | #4210 | Remediate deploy accessibility violations across remaining routes: exclude third-party iframes from axe scan, underline table cell and citation links, calibrate semantic success/error color tokens, and enforce high-contrast text in contact sidebar and brand card code (#4209). |
| 2026-09-06 | #4208 | Remediate deploy accessibility violations across routes: link underlines in bibliographies, callout/video ARIA roles, math scrollability, and token contrast (#4207). |
| 2026-09-05 | #4206 | Resolve serious and critical axe accessibility violations across 163 routes and default site verifier axe policy to fail (#4139). |
| 2026-09-06 | #4205 | Derive complete energy-transfer ledgers, correct sequencing and work-error interpretations, verify primary bibliography, and improve mobile equation and parameter-table readability. |
| 2026-09-05 | #4203 | Derive coupled air-relative ball flight, reproduce coefficient-domain examples, and correct aerodynamic evidence and conformance interpretation. |
| 2026-09-05 | #4201 | Derive coupled impact, distinguish rotation/reference experiments, and qualify closure evidence across three articles. |
| 2026-09-05 | #4199 | Rebuild tangent-reference control and mechanical cases; verify Hamiltonian/KKT signs, discrete derivatives, DDP curvature, exact orbital LQR, arm kinematics and quadrotor hover with 23 new checks and 4,029 full-suite passes. |
| 2026-09-05 | #4196 | Correct tangent-reference differentiation, moving-coordinate transport, functional sensitivity and finite swing interpretation; 20 new checks, 4,006 full-suite passes and verified web mathematics. |
| 2026-09-05 | #4195 | Correct counterfactual flow and sensitivity, input invariance, physiological inference and Koike citation across the theory series and long editions. |
| 2026-09-05 | #4193 | Derive loaded beam boundary conditions, modal normalization and reproducible flexible pendulum dynamics across three web editions. |
| 2026-09-05 | #4191 | Correct rigid–flexible golf foundations and posture-dependent coupling in three web editions |
| 2026-09-05 | #4188 | Correct concluding golf investigation protocol, shared glossary and reading lists; synchronize four case-study editions and rebuild five PDFs. |
| 2026-09-05 | #4186 | Derive learning-control convergence, transient growth, noise and filtering limits, identifiability, policy-search scope, and verified controller reuse in four editions; rebuild three PDFs and repair valid LaTeX group-ending detection under #4180. |
| 2026-09-05 | #4185 | Correct stochastic motor-control conventions, moment and task uncertainty, optimal-effort claims, original experimental scope, and first-contact risk; synchronize four editions, rebuild three PDFs, and add checked counterexamples under #4179. |
| 2026-09-05 | #4183 | Derive valid phase coordinates, virtual constraints, input authority, internal dynamics, active power, and hybrid contact conditions; synchronize four editions, rebuild three PDFs, and connect coordination to golf impact under #4177. |
| 2026-09-05 | #4182 | Derive nonlinear funnel invariance, progress and impact conditions, robust and SOS certificate limits, continuous-time verification, and output-sensitive geometry; synchronize four editions, rebuild three PDFs, and add independently checked examples under #4175. |
| 2026-09-05 | #4178 | Correct trajectory objectives, free-time scaling, PMP signs, numerical feasibility, and impact uncertainty in four editions; rebuild three PDFs and repair long-chapter visibility under #4173 and #4176; accept valid starred LaTeX operators without weakening corruption checks under #4181. |
| 2026-09-05 | #4174 | Correct orbital stability, transverse coordinates, Floquet limits, hybrid timing, transient growth, event outcomes, and LQR tube conditions; synchronize four editions, rebuild three PDFs, and add checked examples under #4171. |
| 2026-09-05 | #4172 | Correct configuration manifolds, force covectors, rotation singularities, kinetic geometry, passive energy, and attitude-control frames; synchronize four editions, rebuild three PDFs, and add reproducible checks under #4169. |
| 2026-09-05 | #4200 | Update stale E2E tests for single-column redesign and resolve touch target, contrast, and bibliography pane defects under #4140. |
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

| 2026-09-07 | #4240 | Rebuild the paired kinetic-chain chapter around verified mechanics, evidence, energy budgets, and reproducible counterexamples. |
| 2026-09-07 | #4243 | Correct paired Physics energy-work and hip-turn citation passages; derive explicit system budgets and preserve measurement and review scope. |
| 2026-09-07 | #4246 | Reconcile the complete nonlinearity article with independent mechanics, contact and memory examples, explicit muscle input conventions, and finite-horizon golf interpretation. |
| 2026-09-07 | #4247 | Reconcile complete machine-learning print/web lessons, policy-gradient and learned-mechanics derivations, reproducible backpropagation, evidence limits and exercises. |
| 2026-09-07 | #4249 | Reconcile paired robot-model chapters, constraint and task mobility, dynamic null-space control, physical URDF examples, anthropometry and experimental identifiability. |
| 2026-09-07 | #4251 | Reconcile finite screw displacement, instantaneous twists, dual wrench transformations, reciprocal constraints, grip power and independently checked linkage statics in both introductory editions. |

> For the complete historical change log (v1.0.173 – v1.0.278), see [CHANGELOG.md](CHANGELOG.md).

| 2026-09-07 | #4257 | Rebuild paired contraction proofs and metric/controller/noise hypotheses; replace unsupported golf robustness claims with checked mechanics and explicit experimental questions. |

| 2026-09-07 | #4259 | Rebuild paired articulated-body derivations, independently checked tree dynamics, contact and impact distinctions, and constrained golf-delivery interpretation. |
| 2026-09-07 | #4262 | Rebuild configuration-space charts, kinematic inverses, workspace and controllability distinctions; add checked examples and connect grip geometry to feasible golf delivery. |
| 2026-09-07 | #4263 | Reconcile Lagrangian inertia, force and energy conventions; correct conservation and integration claims with verified rod dynamics and golf power accounting. |
| 2026-09-07 | #4267 | Close cross-article cluster gaps from issue #3903: wire intentional-constraint-collapse and passive-distributed-control into the proximal-distal program, link both research reviews back into the article cluster, connect secondary-axis-stability and strokes-gained-limitations into the impact/putting cluster both ways, and give the technology articles the canonical Related Concepts component with fully-resolving links. |
| 2026-09-07 | #4264 | Reconcile counterfactual interventions, directional and event-conditioned control authority, energy balances and the paired double-pendulum example. |
| 2026-09-08 | #4271 | Add series navigation sidebars and wire the tangent-space hyperplanes cluster; refresh trust-surface and claim-audit digests for the wired sources. |
| 2026-09-07 | #4269 | Wire lateral markdown content links into all Build-section pages (models, repositories, tools) and three isolated articles; connect every model↔repository pair with the canonical Related Articles component. |
| 2026-09-08 | #4272 | Correct state completeness, acceleration geometry, stability, sensing and sampled-control claims with independently checked physical examples in both editions. |

| 2026-09-08 | #4275 | Correct exponential/logarithm branches, rigid-motion translation, coordinate-rate Jacobians, BCH and geodesic claims with independently verified examples and golf-delivery sensitivity. |
| 2026-09-08 | #4274 | Reconcile recursive dynamics frames, force propagation, spatial acceleration, inertia, contact feasibility and computational claims with independently checked golf-model examples. |

| 2026-09-08 | #4278 | Reconcile the complete-swing synthesis with constrained input gain, event-sensitive delivery, shaft dynamics, collision energy and explicit evidence limits. |
| 2026-09-08 | #4280 | Correct tangent-space foundations, dimensioned examples, residual bounds, moving-coordinate sensitivity, optimization and hybrid-event interpretations. |

| 2026-09-08 | #4283 | Reconcile paired spine anatomy, coordinate conventions, coupled dynamics, tissue-load inference and golf injury evidence with dimensioned checks. |
| 2026-09-08 | #4286 | Correct propagated residual bounds, adaptive-control and evidence claims across the advanced article and three companions; add independently checked flow, interval, norm, stability and statistical examples. |
| 2026-09-08 | #4289 | Reconcile rotation frames, Euler-rate maps, quaternion conversion and interpolation across both textbook editions; add golf-task sensitivity, independent checks and complete exercises. |

| 2026-09-08 | #4300 | Correct paired PoE chapter ordering, space/body and point Jacobians, task singularities, metric/force duality, null-space and humanoid closure examples; independently verify all exercises and rebuild Volume 0. |
| 2026-09-08 | #4296 | Reconcile paired biology chapters with explicit muscle-tendon state, HKB phase stability, synergy evidence limits, impedance and a proven coupling condition; rebuild Volume IV and correct reading-page theme contrast. |
| 2026-09-08 | #4293 | Reconcile inverse-dynamics manuscripts, original contact and aerodynamic examples, wrench transport, constrained input allocation, power and effort inference; regenerate PDF companions and replace stale HTML with a reading guide. |
| 2026-09-08 | #4302 | Add the C2 controlled category vocabulary (config/categories.yml) applied site-wide and the C3 site link gate (include-aware link resolution, related-coverage, orphan detection, path-style normalization, category validation) wired into link-checker --site-gate and CI, with a committed related-coverage baseline. |
| 2026-09-08 | #4298 | Qualify paired Chapter 29 grip, constraint, friction, stability and shaft-acoustic claims with independent numerical counterexamples and verified publication output. |
| 2026-09-08 | #4304 | Reconcile wrist constraint reactions, power, grip and face-angle sensitivity across article and print companions; correct Cardan transmission, dimensional plots and interactive input handling with independent mechanics checks. |
| 2026-09-09 | #4306 | Reconcile paired computational-brain chapters with delayed activation, output sensitivity, impedance energy, constrained synergies and qualified neural evidence; independently verify fourteen exercises and rebuild the print book. |
| 2026-09-09 | #4310 | Reconcile paired swing-plane geometry, contact impulse, launch optimization and uncertainty; independently verify eight exercises, preserve web mathematics and rebuild the print book. |
| 2026-09-09 | #4312 | Reconcile launch-monitor observability, spin reconstruction, point-referenced motion, ordered rotations and contact-model uncertainty; add independent counterexamples and accessible scientific figures. |
| 2026-09-09 | #4314 | Reconcile paired interdisciplinary chapters with explicit control, impedance, material, collision and evidence models; add verified derivations, shared figures and eight worked answers. |
| 2026-09-09 | #4317 | Correct paired soft-tissue, pressure, inertia and energy models with bounded primary evidence, two reproducible figures and seven independently checked worked exercises. |
| 2026-09-09 | #4319 | Correct paired spatial-algebra, physical-inertia and recursive-dynamics derivations; add independent energy checks, shared routines, two figures and fifteen worked answers. |
| 2026-09-09 | #4321 | Correct paired energy-transfer, segment/interface power, metric cancellation, moving-constraint, lag and collision ledgers with two reproducible figures and six independently verified worked answers. |
| 2026-09-09 | #4323 | Correct rotation conversion singularities, frame/quaternion conventions, input validity and golf interpretation with tested Python/browser implementations and complete responsive web review. |
| 2026-09-09 | #4325 | Correct motion-capture geometry, timing, anatomical inference, correlated uncertainty and scientific interpretation with verified primary claims and independently checked examples. |
| 2026-09-09 | #4329 | Repair nonlinear-control explanations with keyboard-native disclosure markup, theme-aware titles and qualified mechanical interpretation. |

| 2026-09-10 | #4335 | Correct paired shaft beam, modal, coupled-input and energy models; distinguish relative recoil from measured fitting outcomes with two reproducible figures and six worked answers. |

| 2026-09-10 | #4337 | Correct paired passive-control energy, drift and stability arguments; distinguish intrinsic mechanics from delayed feedback with a reproducible damping figure and 12 worked exercises. |
| 2026-09-10 | #4339 | Correct the complete DCR article with explicit scaling, coordinate and capacity assumptions, reproducible counterexamples and finite-time impact sensitivity. |
| 2026-09-10 | #4344 | Correct paired fascia mechanics and biological evidence; keep bound DCR reviews outside pruned deployment output (#4342). |

| 2026-09-10 | #4346 | Re-derive complete triple-pendulum dynamics, release and power accounting with verified examples and bounded wrist-control evidence. |

| 2026-09-10 | #4348 | Correct brain-control prediction, inverse feasibility, delayed response and neuroscience evidence with ten worked answers and complete paired reading. |

| 2026-09-10 | #4350 | Correct paired affine dynamics, drift capacity, energy and optimality with complete worked examples and verified vector fields. |
| 2026-09-10 | #4351 | Rebuild paired constraint dynamics, interface power, reaction loads and capture with verified examples and complete worked answers. |
