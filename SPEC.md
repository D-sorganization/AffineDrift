# SPEC.md — Repository Specification Document

Last-Updated: 2026-04-11T21:44:03Z

<!--
  TEMPLATE VERSION: 1.0.0
  LAST UPDATED: 2026-03-30

  This is the canonical specification template for all repositories in the
  D-sorganization fleet. Every repo MUST have a SPEC.md at its root.

  INSTRUCTIONS:
  1. Copy this template to the root of your repository as SPEC.md
  2. Fill in every section — leave nothing as "[TODO]"
  3. Keep this document updated with every PR that changes functionality
  4. CI will block merges if SPEC.md is stale (source changed but spec didn't)

  AUDIENCE: This document is designed for both human developers AND AI agents.
  Write clearly, use concrete examples, and avoid ambiguity.
-->

## 1. Identity

| Field                   | Value                                            |
| ----------------------- | ------------------------------------------------ |
| **Repository Name**     | `AffineDrift`                                    |
| **GitHub URL**          | `https://github.com/D-sorganization/AffineDrift` |
| **Owner**               | D-sorganization                                  |
| **Primary Language(s)** | Python 3.12, JavaScript ES6+, Quarto             |
| **License**             | MIT                                              |
| **Current Version**     | 1.0.7                                            |
| **Spec Version**        | 1.0.42                                           |
| **Last Spec Update**    | 2026-04-11                                       |

## 2. Purpose & Mission

AffineDrift is a research platform that explores golf swing biomechanics through the lens of affine control theory. The project combines rigorous mathematical modeling with interactive educational content, publishing research-quality materials via a Quarto-based website hosted on GitHub Pages. It demonstrates how differential dynamic programming and iterative linear-quadratic regulation (iLQR) can optimize swing trajectories, while serving as an educational bridge between control theory and biomechanics for the broader scientific community.

## 3. Goals & Non-Goals

### Goals

- Model golf swings as affine controllable systems with mathematical rigor, enabling optimization through advanced control algorithms
- Publish and maintain research-quality educational content via Quarto website (AffineDrift.com) on GitHub Pages
- Implement swing trajectory optimization using differential dynamic programming (DDP) and iLQR solvers
- Model golf-ball flight with velocity-dependent drag and spin-dependent Magnus lift using the standard projected-area aerodynamic formulation
- Achieve and maintain >50% test coverage with property-based testing (Hypothesis) across all critical modules
- Provide comprehensive educational resources that bridge control theory and applied biomechanics
- Maintain textbook bibliographies and chapter citations with explicit scientific sourcing for biomechanics, multibody dynamics, geometry, and control-theory claims
- Present the textbook volumes with shared algorithm and pseudocode conventions so implementation guidance is consistent across the series

### Non-Goals

- Not a production game engine (QuatEngine serves that purpose)
- Not a real-time physics simulator (UpstreamDrift provides real-time simulation)
- Not a general-purpose mathematics library

## 4. Architecture Overview

### System Context

AffineDrift operates as a standalone research and education platform within the D-sorganization fleet. It complements but does not depend on QuatEngine (game engine) or UpstreamDrift (real-time physics simulator). The platform produces research content and optimization algorithms that can be consumed by educational institutions, biomechanics researchers, and control theory practitioners. It integrates with GitHub Pages for deployment and GitHub Actions for continuous integration, deployment, and automated quality assurance.

### Module Map

```
AffineDrift/
├── src/
│   ├── affine_control/          # Swing optimization and control algorithms
│   │   ├── swing_optimizer.py   # DDP and iLQR solvers for swing trajectories
│   │   ├── ddp_solver.py        # Differential dynamic programming implementation
│   │   ├── residuals.py         # Optimization residual calculations
│   │   └── swing_types.py       # Swing model definitions and types
│   ├── core/                    # Foundational abstractions and utilities
│   │   ├── constants.py         # Physical and mathematical constants
│   │   ├── contracts.py         # Design-by-contract specifications
│   │   ├── optimizers.py        # iLQR optimizer implementations
│   │   └── protocols.py         # Type protocols and interfaces
│   └── tangent_models/          # Tangent space and hyperplane methods
│       ├── tangent_space.py     # Tangent space mathematics
│       └── examples.py          # Example implementations and tutorials
├── src/tools/                   # CI/CD utilities and build tools
│   ├── link_checker.py          # Validate links in documentation
│   ├── site_health.py           # Monitor website health metrics
│   └── code_quality_ast.py      # AST-based code quality analysis
├── tests/                       # Test suite (80+ test files)
│   ├── test_affine_control/     # Physics and optimization tests
│   ├── test_core/               # Core module tests
│   ├── test_tangent_models/     # Tangent space method tests
│   ├── test_tools/              # Tool and CI/CD tests
│   ├── test_content/            # Content structure and validation
│   └── test_integration/        # Cross-module integration tests
├── js/                          # JavaScript interactive features
│   ├── rotation-converter/      # 3D rotation visualization
│   ├── search.js                # Site search functionality
│   └── interactive-viz.js       # Mathematical visualizations
├── css/                         # Canonical stylesheets (CSS budget enforced)
│   ├── main.css                 # Primary stylesheet
│   ├── typography.css           # Typography and layout
│   └── responsive.css           # Responsive design rules
├── content/                     # Quarto markdown source files (.qmd)
│   ├── index.qmd                # Homepage
│   ├── getting-started.qmd      # Getting started guide
│   └── [other pages]            # Additional educational content
├── articles/                    # Research articles (.qmd format)
│   ├── swing-modeling.qmd       # Core swing modeling article
│   ├── optimization-theory.qmd  # Optimization theory and methods
│   └── [other articles]         # Additional research content
├── books/                       # Quarto book projects
│   └── control-theory-guide.qmd # Comprehensive control theory textbook
├── .github/workflows/           # 54 GitHub Actions workflows
│   ├── ci-standard.yml          # Main CI pipeline
│   ├── deploy-website.yml       # Quarto site build and deployment
│   ├── test-coverage.yml        # Test coverage reporting
│   ├── link-check.yml           # Link validation
│   ├── css-budget.yml           # CSS size enforcement
│   └── [other workflows]        # Jules agents, specialized tests, etc.
├── scripts/                     # Content and repository maintenance utilities
│   ├── check_bibliography_quality.py # Bibliography structure and metadata validation
│   ├── check_qmd_citation_keys.py    # Quarto citation-key integrity scan for site content
│   ├── cli_output.py                 # Explicit stdout/stderr helpers for intentional CLI contracts
│   └── README.md                # Script usage and CI-facing documentation
├── tests/                       # Additional test organization
│   └── e2e/                     # End-to-end Playwright tests
├── _quarto.yml                  # Quarto configuration
├── pyproject.toml               # Python project metadata and dependencies
├── package.json                 # JavaScript dependencies
├── SPEC.md                      # This specification document
└── README.md                    # Project overview and quick start
```

### Key Components

| Component             | Location                                | Purpose                                                    |
| --------------------- | --------------------------------------- | ---------------------------------------------------------- |
| Swing Optimizer       | `src/affine_control/swing_optimizer.py` | DDP and iLQR-based trajectory optimization for golf swings |
| DDP Solver            | `src/affine_control/ddp_solver.py`      | Core differential dynamic programming algorithm            |
| Core Constants        | `src/core/constants.py`                 | Physical and mathematical constants used throughout        |
| iLQR Optimizer        | `src/core/optimizers.py`                | Iterative linear-quadratic regulation solver               |
| Tangent Space Models  | `src/tangent_models/`                   | Tangent space and hyperplane mathematical abstractions     |
| Link Checker          | `src/tools/link_checker.py`             | CI/CD tool for validating documentation links              |
| Site Health Monitor   | `src/tools/site_health.py`              | Automated website health and performance checks            |
| Code Quality Analyzer | `src/tools/code_quality_ast.py`         | AST-based Python code quality analysis                     |
| Rotation Converter    | `js/rotation-converter/`                | Interactive 3D rotation visualization and converter        |
| Search Functionality  | `js/search.js`                          | Full-text search across website content                    |
| Quarto Configuration  | `_quarto.yml`                           | Website build and rendering configuration                  |
| Test Suite            | `tests/`                                | 80+ pytest and Jest test files                             |

## 5. Desired Functionality

### Core Features

| #   | Feature                                 | Status | Description                                                                                                                                                                                                                                                                                                                      |
| --- | --------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | Quarto Website Rendering and Deployment | ✅     | Renders Quarto markdown (.qmd) source files into static HTML and deploys to GitHub Pages                                                                                                                                                                                                                                         |
| F2  | Affine Control Theory Swing Optimizer   | ✅     | Implements DDP and iLQR algorithms to optimize golf swing trajectories as affine controllable systems                                                                                                                                                                                                                            |
| F3  | Tangent Space and Hyperplane Models     | ✅     | Provides mathematical models for tangent space methods with educational examples                                                                                                                                                                                                                                                 |
| F4  | Interactive JavaScript Visualizations   | ✅     | Rotation converter, search interface, and mathematical visualization components                                                                                                                                                                                                                                                  |
| F5  | Mathematical Notation Rendering         | ✅     | Supports MathJax and KaTeX for rendering LaTeX equations in web content, with `ui/lazy` enabled for performance and LaTeX cleanup that preserves escaped percent signs while removing real comments                                                                                                                              |
| F6  | Property-Based Testing with Hypothesis  | ✅     | Comprehensive property-based testing strategy using Hypothesis framework                                                                                                                                                                                                                                                         |
| F7  | CSS Budget Enforcement                  | ✅     | Automated CI enforcement of CSS file size limits to maintain performance                                                                                                                                                                                                                                                         |
| F8  | Mirror Validation                       | ✅     | Ensures duplicate stylesheets match canonical versions across the codebase                                                                                                                                                                                                                                                       |
| F9  | GitHub Actions Automation               | ✅     | 54 CI/CD workflows including Jules automation agents for code analysis and deployment; third-party actions are pinned to immutable SHAs where practical                                                                                                                                                                          |
| F10 | Progressive Web App Support             | ✅     | Service worker and manifest for PWA capabilities with bounded offline caching and update notices (offline access, installability)                                                                                                                                                                                                |
| F11 | Textbook Compilation Pipeline           | ✅     | Quarto pipeline to compile educational materials into publishable textbook format                                                                                                                                                                                                                                                |
| F12 | Textbook claim guardrail                | ✅     | PR CI blocks newly added unsupported quantitative or study claims in textbook content unless they include a citation or an explicit illustrative caveat                                                                                                                                                                          |
| F13 | PR site-build and dependency-audit gate | ✅     | `ci-standard.yml` caches Python dependencies, audits Python dependencies with blocking `pip-audit`, measures coverage across the full `src/` tree, renders the Quarto site in PR CI, syncs frontend assets, and runs Playwright smoke tests against the generated docs, including workflow-file changes in CI triggers           |
| F14 | Bibliography duplicate-alias guardrail  | ✅     | Reference-integrity tests require duplicate bibliography records to carry an explicit legacy-compatibility note instead of silently diverging                                                                                                                                                                                    |
| F15 | Textbook bibliography synchronization   | ✅     | The Geometry of Motion and The Physics of Golf keep chapter-level citations synchronized with shared bibliography sources in `references/affine-drift.bib` and the book-specific `.bib` files                                                                                                                                    |
| F16 | Website citation-resolution guardrail   | ✅     | PR CI scans website `.qmd` sources, resolves their configured bibliography files, and fails when citation keys do not map to a known bibliography entry                                                                                                                                                                          |
| F17 | Textbook algorithm convention sharing   | ✅     | `geometry_of_motion.sty` exposes shared algorithm and pseudocode primitives so implementation-oriented chapters use one consistent notation and formatting style                                                                                                                                                                 |
| F18 | Textbook applied-optimization guidance  | ✅     | Volume I uses the canonical 12-file include list in `volume0.qmd`, and Volume II renders from monolithic `volume2_content.qmd`; both volumes include implementation-grade pseudocode for DDP/iLQR, direct collocation, funnel synthesis, ILC, and trajectory-library adaptation, plus a bounded treatment of evolutionary search |
| F19 | Script CLI output contracts             | ✅     | Maintenance scripts route intentional terminal output through `scripts/cli_output.py`, making stdout/stderr behavior explicit and easier to test without weakening logging semantics                                                                                                                                             |
| F20 | RL benchmark modular split              | ✅     | `src/tools/rl_funnel_benchmark.py` now stays under the repo file-size budget by delegating dynamics, controllers, and simulation concerns to focused helper modules while preserving the benchmark module's public API, including caller-provided reference trajectory timesteps                                                 |
| F21 | Tooling Demeter facades                 | ✅     | Link and site-health utilities isolate DOM/path traversal behind small façade objects so repository-governance checks depend on narrower interfaces instead of nested reach-through                                                                                                                                              |
| F22 | Wrist-model Qt module split             | ✅     | The legacy `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` launcher now delegates geometry, kinematics, Qt canvas rendering, and window assembly to focused modules under `src/tools/wrist_universal_joint`, keeping the entrypoint thin while preserving its public surface                                |
| F23 | Analysis helper fallback logging        | ✅     | `src/tools/utils/analysis_utils.py` logs recoverable parse and file-read failures at debug level when it falls back to zeroed or empty analysis results, keeping repository-quality scans observable without turning invalid files into hard failures                                                                            |
| F24 | Developer test target coverage          | ✅     | `make test` runs Python `src/` coverage and JavaScript coverage so local developer checks exercise both primary test stacks before code reaches CI                                                                                                                                                                               |
| F25 | Core algorithm regression coverage      | ✅     | Executable pytest coverage exercises the actual iLQR optimizer and RL funnel controller modules, including optimization progress, input validation, setpoint control, trajectory tracking control, and weight-matrix shape validation                                                                                            |
| F25 | Workflow event-payload hardening        | ✅     | Comment, issue, and PR-body GitHub event payloads are passed through workflow `env:` values and shell-safe handling instead of being interpolated directly into `run:` scripts                                                                                                                                                   |
| F26 | Wrist universal-joint ratio consistency | ✅     | The wrist universal-joint tools use the Cardan/Hooke transmission denominator without a square root, standardize ratio call sites with keyword arguments, and keep Streamlit cache decorators typed for mypy                                                                                                                     |
| F27 | Batch converter package imports         | ✅     | Batch LaTeX conversion entrypoints import converter classes through package-qualified `src.tools.*` paths so they work under pytest and module execution                                                                                                                                                                         |
| F28 | Physics of Golf numeric consistency     | ✅     | Critical textbook checks pin the chapter 3 double-pendulum numerical example to the documented `M2 = 1.5 kg` parameter set so rendered values do not drift from the stated model                                                                                                                                                 |
| F29 | Wrist-model figure lifecycle            | ✅     | Wrist-model Streamlit visualizations create Matplotlib figures through the object-oriented `Figure` API and avoid resource-caching array-backed plot functions                                                                                                                                                                   |
| F30 | Assessment category mappings            | ✅     | Repository assessment helpers keep `ASSESSMENT_DEFINITIONS` names synchronized with canonical A-N category labels so generated reports and category lookups use consistent terminology.                                                                                                                                          |
| F31 | Dependency pinning and tool isolation   | ✅     | Root Python requirements use exact pins for reproducible CI installs while the Streamlit wrist tool keeps its optional UI-specific requirements in its local requirements file.                                                                                                                                                  |
| F32 | Stimpmeter-calibrated putting physics   | ✅     | Putting roll simulation and round-level putt speed estimation share the USGA Stimpmeter launch-speed deceleration formula, with regression coverage for Stimp 10 stopping distance.                                                                                                                                              |
| F33 | Round putting simulator injection       | ✅     | `RoundSimulator` accepts an optional prebuilt `PuttingSimulator` so tests and callers can provide calibrated green physics without relying on inline flat-green construction.                                                                                                                                                    |
| F34 | RL funnel benchmark result sharing      | ✅     | RL funnel benchmark result structures and result-formatting helpers are exposed through `src/rl_funnel` so benchmark callers can use one shared result surface instead of duplicating lightweight reporting models.                                                                                                                 |

### API / Interface Contract

**Python API:**

- `affine_control.swing_optimizer.SwingOptimizer` — Main optimization interface
  - Constructor requires a real `ddp_solver` unless `SwingOptimizationConfig.allow_mock_solver=True` explicitly opts into the documented mock implementation for test-only usage
  - `optimize(...)` may execute the mock solver only after that explicit opt-in
  - `optimize(swing_model, constraints) -> OptimizedTrajectory` — Run trajectory optimization
- `core.optimizers.iLQR` — iLQR solver
  - `solve(dynamics, cost_fn, initial_trajectory) -> Solution` — Compute optimal trajectory
- `golf_simulation.ball_flight.BallFlightDynamics` — Golf-ball flight integrator
  - Uses Reynolds-dependent drag and spin-parameter lift to compute aerodynamic forces during free flight
- `tangent_models.TangentSpaceModel` — Tangent space abstraction
  - `project(vector) -> Vector` — Project to tangent space

**JavaScript API:**

- `RotationConverter` — Interactive 3D rotation tool
  - `convert(matrix, target_format) -> string` — Convert rotation representations
- `SearchIndex.query(term) -> SearchResults` — Full-text search across content

**CLI Tools:**

- `link-checker.py` — Validate all documentation links
- `site-health.py` — Generate health report on website assets
- `code-quality-ast.py` — Analyze Python code structure and metrics
- `scripts/cli_output.py` — Shared helper for scripts that intentionally emit user-facing stdout/stderr lines as part of their CLI contract

**Website (HTTP):**

- GitHub Pages deployment at `AffineDrift.com`
- Service worker handles offline content caching
- All pages render with MathJax notation support

**Textbook Bibliographies:**

- `references/affine-drift.bib` is the shared canonical bibliography source for the site and textbook projects
- `articles/The_Geometry_of_Motion/geometry_of_motion.bib` and `articles/The_Physics_of_Golf/golf_physics.bib` contain book-specific bibliography entries used by Quarto renders
- Chapter sources in both textbook projects are expected to cite foundational literature for geometric mechanics, multibody dynamics, parallel mechanisms, motor control, and impedance-control claims

## 6. Data & Configuration

### Input Data

| Input                    | Format                 | Source                               | Schema                                                   |
| ------------------------ | ---------------------- | ------------------------------------ | -------------------------------------------------------- |
| Swing Trajectories       | YAML / JSON            | User-defined or benchmark datasets   | Defines initial position, velocity, torques, constraints |
| Mathematical Examples    | Quarto Markdown        | `articles/` and `books/` directories | Standard Quarto with LaTeX and code cells                |
| Website Content          | Quarto Markdown (.qmd) | `content/`, `articles/`, `books/`    | Quarto markdown with YAML frontmatter                    |
| Configuration Parameters | YAML                   | `_quarto.yml`, `.github/workflows/`  | Quarto and GitHub Actions configuration                  |

### Output Data

| Output                       | Format              | Destination                      | Description                                         |
| ---------------------------- | ------------------- | -------------------------------- | --------------------------------------------------- |
| Optimized Swing Trajectories | NumPy arrays / JSON | Memory or file system            | Joint angles, velocities, and torques over time     |
| Optimization Reports         | JSON                | User-defined or CI logs          | Convergence metrics, final cost, solver statistics  |
| Static Website               | HTML + CSS + JS     | GitHub Pages (`AffineDrift.com`) | Rendered Quarto site with interactive features      |
| Test Reports                 | JSON / HTML         | GitHub Actions artifacts         | Coverage reports, test results, performance metrics |
| Code Quality Reports         | JSON / Text         | CI logs and artifacts            | Linting results, type checking errors, AST analysis |

### Configuration

**Quarto Configuration** (`_quarto.yml`):

- Website title, author, and metadata
- Output format (HTML for GitHub Pages)
- Theme and CSS customization
- MathJax and KaTeX rendering settings
- Navigation menu structure

**GitHub Actions Secrets:**

- GitHub Pages deployment token (auto-configured)

**Python Configuration** (`pyproject.toml`):

- Python version: 3.12
- Core runtime dependencies pinned to exact versions in `requirements.txt`
- Test discovery paths
- Coverage configuration (minimum 50%)

**Code Quality Settings:**

- **ruff** — Linting rules in `pyproject.toml` under `[tool.ruff]`
- **black** — 100-character line limit (NOT ruff format)
- **mypy** — Type checking enabled for all src/ modules
- **No print() in src/** — Only logging module permitted

## 7. Testing Specification

### Testing Strategy

AffineDrift follows a **test pyramid** strategy: unit tests form the base (fast, numerous), integration tests verify module interactions, and end-to-end tests validate user-facing workflows. The project uses **property-based testing** (Hypothesis) to ensure mathematical correctness across parameter spaces. All code in `src/` must maintain >50% coverage minimum. Critical physics and optimization modules target 80%+ coverage.

### Test Organization

| Category                         | Location                                                                       | Framework             | Markers                    |
| -------------------------------- | ------------------------------------------------------------------------------ | --------------------- | -------------------------- |
| Unit                             | `tests/test_affine_control/`, `tests/test_core/`, `tests/test_tangent_models/` | pytest                | `@pytest.mark.unit`        |
| Integration                      | `tests/test_integration/`                                                      | pytest                | `@pytest.mark.integration` |
| Content/Structure                | `tests/test_content/`                                                          | pytest                | `@pytest.mark.content`     |
| Specialized (DbC, RL benchmarks) | `tests/test_specialized/`                                                      | pytest                | `@pytest.mark.specialized` |
| JavaScript/Bibliography          | `tests/`                                                                       | Jest                  | N/A                        |
| End-to-End                       | `tests/e2e/`                                                                   | Playwright (Chromium) | N/A                        |

### Coverage Requirements

| Scope           | Minimum | Current | Enforced By                                 |
| --------------- | ------- | ------- | ------------------------------------------- |
| Overall src/    | 50%     | ~90%    | CI (`pytest --cov=src --cov-fail-under=50`) |
| affine_control/ | 70%     | ~70%    | Critical module coverage gate               |
| core/           | 70%     | ~70%    | Critical module coverage gate               |
| tools/          | 60%     | ~90%    | CI plus critical module coverage gate       |

### Required Test Scenarios

- [x] Unit creation with valid physics parameters returns expected optimization trajectory
- [x] DDP solver converges on benchmark swing problems within tolerance
- [x] iLQR solver produces lower-cost trajectories than initial guess
- [x] Tangent space projections maintain mathematical properties (linearity, completeness)
- [x] Quarto website renders without build errors
- [x] CSS file size stays within enforced budget limits
- [x] All documentation links are valid (no 404s)
- [x] MathJax and KaTeX equations render correctly in browser
- [x] Interactive visualizations (rotation converter) load and function without JS errors
- [x] Smoke tests on Chromium pass for critical pages
- [x] Property-based tests with Hypothesis verify DDP convergence across parameter ranges
- [x] Design-by-contract assertions enforce preconditions and postconditions
- [x] Website `.qmd` citations resolve against project or page bibliography files, excluding Quarto cross-references such as `@eq-` and `@sec-`

## 8. Quality Standards

### Code Quality Tools

| Tool       | Version | Purpose                          | Blocking?           |
| ---------- | ------- | -------------------------------- | ------------------- |
| ruff       | Latest  | Linting (multiple rules)         | Yes                 |
| black      | Latest  | Code formatting (100-char lines) | Yes                 |
| mypy       | Latest  | Static type checking             | Yes                 |
| pytest     | Latest  | Testing framework                | Yes                 |
| pytest-cov | Latest  | Coverage measurement             | Yes                 |
| Hypothesis | Latest  | Property-based testing           | No (optional depth) |
| Jest       | Latest  | JavaScript testing               | Yes                 |
| Playwright | Latest  | E2E testing (Chromium)           | Yes                 |

### Design Principles

- **TDD (Test-Driven Development)**: Enforced for new features; PR must include tests before implementation merges
- **Design by Contract (DbC)**: Preconditions and postconditions on core optimization functions; enforced with assertions and Pydantic models
- **DRY (Don't Repeat Yourself)**: CSS mirror validation ensures stylesheets are not duplicated; AST analysis flags code duplication
- **Orthogonality**: Modules are decoupled; affine_control, core, and tangent_models have minimal coupling; tools are independent

### CI/CD Pipeline

| Workflow                  | Trigger         | Purpose                                                                                         | Blocking?          |
| ------------------------- | --------------- | ----------------------------------------------------------------------------------------------- | ------------------ |
| `ci-standard.yml`         | Push/PR to main | Lint, type-check, blocking dependency audit, full-`src/` coverage, site render, E2E smoke tests | Yes                |
| `deploy-website.yml`      | Merge to main   | Build Quarto site, deploy to GitHub Pages                                                       | Yes                |
| `test-coverage.yml`       | Push/PR         | Report coverage metrics                                                                         | Yes (50% minimum)  |
| `link-check.yml`          | Push/PR         | Validate all links in content                                                                   | Yes                |
| `css-budget.yml`          | Push/PR         | Enforce CSS file size limits                                                                    | Yes                |
| `module-size-budget.yml`  | Push/PR         | Enforce Python module complexity                                                                | Yes                |
| `dry-tracker.yml`         | Nightly         | Identify code duplication patterns                                                              | No (informational) |
| `Jules automation agents` | Various         | Automated code review, refactoring suggestions                                                  | No (informational) |

## 9. Dependencies

### Runtime Dependencies

| Package        | Version | Purpose                                                              |
| -------------- | ------- | -------------------------------------------------------------------- |
| numpy          | 2.4.4   | Numerical computations for trajectory optimization                   |
| scipy          | 1.17.1  | Scientific algorithms (optimization, linear algebra)                 |
| matplotlib     | 3.10.8  | Plotting and visualization of swing trajectories                     |
| pydantic       | 2.12.5  | Data validation and runtime type checking                            |
| PyYAML         | 6.0.3   | YAML configuration file parsing                                      |
| beautifulsoup4 | 4.14.3  | HTML parsing for link checking and site analysis                     |
| requests       | 2.33.1  | HTTP requests for external data fetching                             |
| streamlit      | 1.56.0  | Interactive dashboard for visualization _(optional tool dependency)_ |

### Development Dependencies

| Package    | Version  | Purpose                          |
| ---------- | -------- | -------------------------------- |
| pytest     | 8.3.5    | Testing framework                |
| pytest-cov | 7.1.0    | Coverage reporting               |
| hypothesis | 6.151.12 | Property-based testing library   |
| ruff       | 0.15.9   | Linting and code quality         |
| black      | 26.3.1   | Code formatting (100-char lines) |
| mypy       | 1.20.0   | Type checking                    |
| jest       | Latest   | JavaScript testing framework     |
| playwright | Latest   | Browser automation for E2E tests |

### Fleet Dependencies

| Repo          | Relationship            | Description                                               |
| ------------- | ----------------------- | --------------------------------------------------------- |
| QuatEngine    | Referenced in non-goals | Game engine; AffineDrift does not depend on it            |
| UpstreamDrift | Referenced in non-goals | Real-time physics simulator; AffineDrift is complementary |

## 10. Deployment & Operations

### How to Run

```bash
# Prerequisites
- Python 3.12 or later
- Node.js 20 or later
- Quarto 1.6.39 or later
- Git

# Installation
git clone https://github.com/D-sorganization/AffineDrift.git
cd AffineDrift
pip install -r requirements.txt
pip install -r src/tools/wrist_universal_joint/requirements.txt  # optional, for Streamlit wrist tool
npm install

# Running tests
pytest tests/ --cov=src --cov-fail-under=50
npm run test  # JavaScript tests
npx playwright test  # E2E tests

# Running optimization example
python -m affine_control.swing_optimizer --config=example_swing.yaml

# Building website locally
quarto render

# Running CI tools
python src/tools/link_checker.py
python src/tools/site_health.py
python src/tools/code_quality_ast.py
```

### Build Artifacts

| Artifact             | Format          | Destination                                 |
| -------------------- | --------------- | ------------------------------------------- |
| Static Website       | HTML + CSS + JS | GitHub Pages (AffineDrift.com)              |
| Test Reports         | JSON + HTML     | GitHub Actions artifacts and CI logs        |
| Coverage Reports     | LCOV + HTML     | CI artifacts (coverage.xml)                 |
| Quarto Book          | PDF + HTML      | GitHub Pages and releases                   |
| Optimization Results | JSON            | File system or cloud storage (user-defined) |

## 11. Roadmap & Open Issues

### Current Phase

**Active Development & Maintenance**: AffineDrift is a mature research platform with core functionality complete (v1.0.0). Current focus is on expanding educational content, maintaining test coverage above 50%, and refining the optimization algorithms based on real-world validation data. The project serves as both a research artifact and an educational resource.

### Planned Work

| Priority | Item                                                              | Target Date |
| -------- | ----------------------------------------------------------------- | ----------- |
| P0       | Maintain test coverage >50% across all PRs                        | Ongoing     |
| P1       | Publish research paper on affine swing modeling                   | Q2 2026     |
| P1       | Expand tangent space examples and tutorials                       | Q2 2026     |
| P2       | Optimize iLQR solver performance for real-time feedback           | Q3 2026     |
| P2       | Add interactive swing trajectory editor to website                | Q3 2026     |
| P3       | Support additional swing types (left-handed, alternative stances) | Q4 2026     |

### Known Limitations

- **Real-time Performance**: Current optimizers are designed for batch analysis, not real-time control (handled by UpstreamDrift)
- **Physical Accuracy**: Models assume rigid-body dynamics; soft-tissue deformation not modeled
- **Browser Support**: Progressive Web App features require modern browsers (ES6+, Service Worker API)
- **Content Rendering**: Complex 3D visualizations limited to JavaScript WebGL (no headless rendering)
- **Optimization Convergence**: DDP solver may not converge for highly nonlinear swing models; iLQR is more robust but slower

## 12. Change Log

| Date       | Version | Changes                                                                                                                                                                                                                                                                                                                                                                      |
| ---------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-04-11 | 1.0.42  | refactor(rl_funnel): documented the shared benchmark-result surface that centralizes `BenchmarkResult` and `format_results` for RL funnel benchmarking.                                                                                                                                                                                                                     |
| 2026-04-11 | 1.0.41  | refactor(simulation): allowed `RoundSimulator` to receive an injected `PuttingSimulator`, preserving the default flat-green path while enabling calibrated putting physics in tests and callers.                                                                                                                                                                             |
| 2026-04-11 | 1.0.40  | fix(physics): corrected putting deceleration to use the Stimpmeter stopping-distance formula in both direct putting simulation and round-level putt speed estimation, with regression coverage for Stimp 10 rollout distance.                                                                                                                                                |
| 2026-04-11 | 1.0.39  | test(algorithms): replaced placeholder algorithm smoke checks with executable coverage for the iLQR optimizer and RL funnel controllers, including finite-control and validation assertions.                                                                                                                                                                                 |
| 2026-04-11 | 1.0.38  | chore(deps): pinned root Python dependencies exactly and isolated the optional Streamlit wrist-tool requirements in the tool-local requirements file while preserving documented setup steps.                                                                                                                                                                                |
| 2026-04-11 | 1.0.37  | fix(assessment): synchronized `ASSESSMENT_DEFINITIONS` category names with the canonical A-N `CATEGORIES` map and added regression coverage for report-label consistency.                                                                                                                                                                                                    |
| 2026-04-11 | 1.0.35  | fix(pwa): bounded the service-worker cache and surfaced update notices so stale offline content refreshes visibly without unbounded storage growth                                                                                                                                                                                                                           |
| 2026-04-11 | 1.0.34  | fix(wrist): switched wrist-model Matplotlib helpers from pyplot state to object-oriented `Figure` construction and removed resource caching from array-backed plot functions.                                                                                                                                                                                                |
| 2026-04-11 | 1.0.33  | fix(ci): removed duplicate requirements installation from `ci-standard.yml`, enabled pip caching, allowed workflow-only changes to trigger CI, aligned PR auto-labeler path rules with the repository layout, and cleaned stale SPEC conflict markers.                                                                                                                       |
| 2026-04-11 | 1.0.32  | chore(deps): pinned previously unpinned root requirements and moved streamlit out of core requirements into the wrist tool optional requirements file.                                                                                                                                                                                                                       |
| 2026-04-11 | 1.0.31  | fix(latex): documented the tcolorbox package loading contract to avoid option-clash failures in the golf physics PDF build.                                                                                                                                                                                                                                                  |
| 2026-04-11 | 1.0.30  | fix(logging): made `setup_logging()` import-order safe by avoiding root `basicConfig()` calls for named loggers while preserving root configuration for script entry points.                                                                                                                                                                                                 |
| 2026-04-11 | 1.0.30  | fix(tools): preserved escaped LaTeX percent signs during comment cleanup and added regression coverage for `\%` content followed by trailing comments                                                                                                                                                                                                                        |
| 2026-04-11 | 1.0.29  | fix(critical): hardened workflow event payload handling, corrected wrist universal-joint ratio semantics, refreshed the chapter 3 double-pendulum numeric example, and restored package-qualified batch converter imports                                                                                                                                                    |
| 2026-04-11 | 1.0.27  | fix(tools): prevented display math created from LaTeX `equation` environments in `src/tools/latex_to_html.py` from being wrapped twice, and added a regression test for the single-wrapper output                                                                                                                                                                            |
| 2026-04-11 | 1.0.26  | fix(testing): made `make test` run Python coverage before JavaScript coverage and removed the bare `pass` coverage exclusion so stubs remain visible in reports                                                                                                                                                                                                              |
| 2026-04-11 | 1.0.25  | fix(tools): made RL benchmark comparison honor the caller-provided `dt` when generating reference trajectories and added regression coverage for the reference time grid                                                                                                                                                                                                     |
| 2026-04-09 | 1.0.24  | docs(articles): Refined the Layman's Terms section in Contraction_Tangent_CRITIC.qmd to use relatable analogies and improve clarity                                                                                                                                                                                                                                          |
| 2026-04-07 | 1.0.19  | chore(types): annotated the remaining public Python functions in `src/` and `scripts/`, added an AST regression test to keep return annotations from drifting, and closed the final actionable slice of assessment issue #2241 after auditing stale print/config findings                                                                                                    |
| 2026-04-07 | 1.0.18  | fix(scripts): replaced remaining raw script-level `print()` calls with explicit stdout/stderr helpers, made maintenance scripts import-safe with `main()` entry points, and added CLI-output regression tests for the affected utilities                                                                                                                                     |
| 2026-04-07 | 1.0.17  | fix(ci): documented the explicit `SwingOptimizer` mock-solver opt-in at construction time, widened `ci-standard.yml` coverage enforcement to the full `src/` tree, and made the main `pip-audit` gate blocking                                                                                                                                                               |
| 2026-04-05 | 1.0.15  | security(xss): Prevented XSS in polynomial evaluation by explicitly stripping allowed math variables/functions and validating the remainder strictly via regex before `new Function` evaluation in `grip_angle_simulator.html`                                                                                                                                               |
| 2026-04-08 | 1.0.23  | security(xss): Fixed DOM-based XSS vulnerability in `.qmd` history list components by replacing `innerHTML` with `document.createElement` and safe text assignment                                                                                                                                                                                                           |
| 2026-04-06 | 1.0.16  | ci(content): added citation-resolution checks for website `.qmd` sources, covering root and nested Quarto bibliography files and excluding Quarto cross-references from unresolved-key failures                                                                                                                                                                              |
| 2026-04-04 | 1.0.13  | security(xss): Fixed XSS vulnerability in `notes-workspace.js` by avoiding `document.write` with string interpolation and safely assigning `value` property                                                                                                                                                                                                                  |
| 2026-04-05 | 1.0.15  | fix(tools): made `fix_html.py` repo-root portable with explicit input/output resolution and dry-run support                                                                                                                                                                                                                                                                  |
| 2026-04-04 | 1.0.15  | perf(frontend): Apply resize:none to auto-growing textareas managed by `initAutoGrowTextareas()` to prevent user manual resizing which conflicts with JS logic                                                                                                                                                                                                               |
| 2026-04-04 | 1.0.14  | perf(frontend): Replaced DOM-based escapeHtml with Regex string replacement in JS to avoid layout thrashing and reduce memory allocations                                                                                                                                                                                                                                    |
| 2026-04-05 | 1.0.15  | security(xss): Fixed XSS vulnerability in `notes-workspace.js` popout feature by removing `document.write` template literal evaluation.                                                                                                                                                                                                                                      |
| 2026-04-03 | 1.0.12  | security(matlab): Fixed path escaping vulnerability in `matlab_quality_check.py` by properly escaping single quotes for MATLAB strings instead of aggressively removing characters                                                                                                                                                                                           |
| 2026-04-01 | 1.0.10  | security(links): Added `rel="noopener noreferrer"` to `target="_blank"` links generated by `latex_utils.py` and `bibliography.js` to mitigate reverse tabnabbing vulnerabilities                                                                                                                                                                                             |
| 2026-04-06 | 1.0.16  | Added repository-wide Quarto citation-key integrity validation in `ci-standard.yml`, documented `scripts/check_qmd_citation_keys.py`, and updated review-bot workflow handling so trusted automated reviewers do not fail PR automation                                                                                                                                      |
| 2026-03-30 | 1.0.9   | fix(html): corrected malformed HTML structure in Wrist_Universal_Claude.html — removed stray </p> tags after list elements and fixed <p> tags improperly wrapping <ul>/<ol> block content                                                                                                                                                                                    |
| 2026-03-30 | 1.0.6   | fix(ci): aligned regression tests with current workflows — mock-solver guard asserted at optimize() per SwingOptimizer contract; test_deployment_integrity updated to match Quarto render action in ci-standard.yml; added dotenv-example removal step before E2E render; updated torque-generator docstrings in Universal_Joint_Model_Enhanced.py                           |
| 2026-03-30 | 1.0.6   | A-N Assessment remediation (issue #2012): auto-formatted 10 files to comply with black 100-char limit; added missing docstrings to priority_score, **post_init**, \_requires_token, create_issue, sha256, sync_one, main, **init**, \_handle_text/\_code_block/\_inline_code/\_display_math/\_inline_math, setup_logging_with_timestamp, find_markdown_files across scripts/ |
| 2026-03-30 | 1.0.5   | Performance fix: replaced O(n²) list.index() loop in putt simulator with enumerate() for linear-time hole-score lookups in round_simulator.py                                                                                                                                                                                                                                |
| 2026-03-30 | 1.0.4   | Fixed remaining CI failures in batch-4 PR: replaced bare HTML TODO comments with inline caveat phrasing ("illustrative", "depends on", etc.) in ch16, ch18--ch31 qmd files and ch14--ch16, ch19 tex files to satisfy checker window requirements                                                                                                                             |
| 2026-03-30 | 1.0.3   | Added TODO(citation) markers and humble qualifiers for unsourced numerical claims in ch14--ch31 LaTeX chapters of The Physics of Golf — issues #1881, #1882, #1883, #1884, #1885, #1886, #1887, #1888, #1889, #1890, #1892, #1893, #1894, #1895, #1896, #1897, #1898, #1899 (batch 2)                                                                                        |
| 2026-03-30 | 1.0.2   | Added caveat phrasing and improved humble language for uncited numerical claims in ch02, ch03, ch04, ch07, ch10, ch11, ch13, ch18, ch19, ch20, ch21, ch23, ch25, ch26, ch29, ch31, and glossary of The Physics of Golf (content audit wave 2; issues #2007--#2011)                                                                                                           |
| 2026-03-30 | 1.0.2   | Added citation markers, TODO notes, and humble phrasing for unsourced numerical claims and study references in ch22--ch31, glossary.qmd (The Physics of Golf), and 01-throwing-away-target.qmd (The Geometry of Motion) — issues #1921, #1922, #1924, #1925, #1926, #1927, #1928, #1929, #1930, #1931, #1932, #1948 (batch 4)                                                |
| 2026-03-30 | 1.0.1   | Improve accessibility for Critics Corner with aria-controls                                                                                                                                                                                                                                                                                                                  |
| 2026-03-30 | 1.0.1   | Added citation markers, TODO notes, and humble phrasing for unsourced claims in chapters 1--13 of The Physics of Golf (issues #1868--#1880, batch 1)                                                                                                                                                                                                                         |
| 2026-03-30 | 1.0.1   | Added citation markers (TODO comments) and humble qualifiers to unsourced numerical claims in ch01--ch21 of The Physics of Golf — issues #1900--#1920 (batch 3)                                                                                                                                                                                                              |
| 2026-03-30 | 1.0.0   | Consolidated frontend scroll event handlers via `requestAnimationFrame`                                                                                                                                                                                                                                                                                                      |
| 2026-03-30 | 1.0.0   | Documented PR CI dependency-audit plus rendered-site E2E gate, mock-solver opt-in behavior at `SwingOptimizer.optimize`, and bibliography duplicate-alias integrity guardrails                                                                                                                                                                                               |
| 2026-03-28 | 1.0.0   | Initial SPEC.md specification for AffineDrift v1.0.0 — all core features documented and implemented                                                                                                                                                                                                                                                                          |

---

<!--
  SPEC MAINTENANCE RULES:

  1. WHEN TO UPDATE: Any PR that adds, removes, or changes functionality
     described in this spec MUST include a corresponding spec update.

  2. WHO UPDATES: The PR author (human or agent) is responsible.

  3. CI ENFORCEMENT: The spec-check workflow will flag PRs where source
     files changed but SPEC.md did not. This is a blocking check.

  4. REVIEW: Spec changes should be reviewed with the same rigor as code.

  5. VERSION: Bump the Spec Version field when making substantive changes.
     Use semver: major (structure change), minor (new features), patch (corrections).
-->
