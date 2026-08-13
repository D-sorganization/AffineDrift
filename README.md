# AffineDrift

[![Quarto Syntax Check](https://github.com/D-sorganization/AffineDrift/actions/workflows/quarto-syntax-check.yml/badge.svg)](https://github.com/D-sorganization/AffineDrift/actions/workflows/quarto-syntax-check.yml)
[![Quarto](https://img.shields.io/badge/built%20with-Quarto-blue.svg)](https://quarto.org/)

AffineDrift is a scientific writing and modeling portfolio for golf mechanics,
multibody dynamics, and nonlinear control. It publishes source-bounded
exposition, model notes, critique responses, and links to executable companion
work rather than presenting a finished theory as a settled result.

The site is intended for technical reviewers who want to see how assumptions,
derivations, references, simulations, and open limitations are tracked together.
The established material is the underlying mathematics and mechanics literature;
the AffineDrift contribution is the application, synthesis, and review workflow
around golf swing models.

## What Is Here

- **Textbook-style expositions**: [The Physics of Golf](articles/The_Physics_of_Golf/quarto/index.qmd) and [The Geometry of Motion](articles/The_Geometry_of_Motion/quarto/index.qmd) organize the main mechanics and control narratives.
- **Source maps and references**: [PARAMETERS.md](PARAMETERS.md), the [bibliography](resources/bibliography.qmd), and development notes identify symbols, units, citations, and repository status.
- **Executable model path**: the site links to the [Golf Modeling Suite](models/models.qmd) page and the related implementation repository, [UpstreamDrift](https://github.com/D-sorganization/UpstreamDrift).
- **Critique and limitation tracking**: [Critiques & Responses](critiques/index.qmd) records objections, assumptions, and evidence gaps alongside the main presentation.
- **Validation artifacts**: CI, Quarto syntax checks, tests, repository inventories, and assessment reports document what is mechanically checked and what remains editorial or exploratory.

## What Is Validated

AffineDrift validates syntax, links, front matter, tests, and selected repository
quality gates through local scripts and GitHub Actions. Some pages also include
explicit provenance notes that distinguish standard control-theory facts from
AffineDrift's golf-specific interpretations.

The validation does not prove that every biomechanical interpretation is true in
vivo. Treat model-dependent quantities, optimization narratives, and proposed
golf-specific metrics as hypotheses unless a page ties them to a cited source,
an executable model, or a stated numerical experiment.

## For Technical Reviewers

Start with these paths:

- [The Physics of Golf](articles/The_Physics_of_Golf/quarto/index.qmd) for the most direct mechanics exposition.
- [Theory Part 1](articles/theory-part1.qmd) for the control-affine framing.
- [Bibliography](resources/bibliography.qmd) for source provenance.
- [Critiques & Responses](critiques/index.qmd) for limitations and objections.
- [Golf Modeling Suite](models/models.qmd) for the site-level model entry point.
- [UpstreamDrift](https://github.com/D-sorganization/UpstreamDrift) for related executable model and workflow implementation.

## Assumptions, Review, and Validation

Computational tools support drafting, refactoring, and repeatable checks. They
are not the scientific claim of the project. Technical claims are expected to be
tied to stated assumptions, cited sources, model code, or explicit numerical
experiments, with limitations visible when evidence is incomplete.

In practice, the workflow emphasizes inspectable artifacts: equations, scripts,
references, diffs, tests, and issue-linked review notes.

## Local Development

This is a Quarto static site hosted through GitHub Pages at `AffineDrift.com`.

Preview locally:

```bash
git clone https://github.com/D-sorganization/AffineDrift.git
cd AffineDrift
quarto preview
```

The preview normally opens at `http://localhost:4000`.

Key paths:

```text
AffineDrift/
├── index.qmd           # Main homepage (Quarto markdown)
├── _quarto.yml         # Quarto configuration
├── styles.css          # Custom styling
├── js/                # JavaScript ES6 modules (main.js entry point)
├── docs/               # Additional documentation
│   └── assessments/    # Quality assessments
├── tests/              # Python tests
├── .github/
│   └── workflows/      # CI/CD pipelines
│       ├── ci-standard.yml      # Core quality gates and tests
│       ├── deploy-website.yml   # GitHub Pages deployment
│       └── quarto-syntax-check.yml # Quarto syntax validation
└── *.qmd               # Content pages (Quarto markdown)
```

## Documentation

**Development Guides:**

- [API Reference](docs/api-reference.md): public API for all `src/` modules.
- [Testing Guide](docs/development/testing-guide.md): test patterns, fixtures, and conventions.
- [Code Style Guide](docs/development/code-style-guide.md): Python, JavaScript, CSS, and Quarto standards.
- [Writing Style Guide](docs/development/writing-style-guide.md): prose standards for every rendered page — sentence economy, claim discipline, terminology, and the CI constraints on prose edits.
- [Git Workflow Guide](docs/development/git-workflow-guide.md): branch strategy, commits, and PR process.
- [Performance Tuning Guide](docs/development/performance-tuning-guide.md): profiling and NumPy optimization.
- [Security Guidelines](docs/development/security-guidelines.md): secrets, input validation, SAST.
- [Release Notes Template](docs/development/release-notes-template.md): changelog and milestone documentation.
- [Benchmarking Policy](docs/development/benchmarking.md): benchmark infrastructure and CI policy.

**Reference:**

- [Canonical Parameters Table](PARAMETERS.md): symbols, units, and parameter ranges.
- [Textbook Series Architecture](docs/development/geometry_of_motion_architecture.md): series architecture and issue-to-deliverable tracking.
- [Repository Inventory](docs/development/repository_inventory.md): component inventory, implementation status, and known gaps.
- [src/README.md](src/README.md): Python source-tree overview and status notes.

**Operations:**

- [SLO & Performance Targets](docs/operations/slo-targets.md): CI/CD SLOs and error budgets.
- [Incident Response Playbooks](docs/operations/incident-response-playbooks.md): step-by-step incident resolution.
- [Troubleshooting Guide](docs/operations/troubleshooting-guide.md): error lookup and debug procedures.
- [On-Call Procedures](docs/operations/on-call-procedures.md): routine checks and response runbooks.
- [Monitoring Setup](docs/operations/monitoring-setup.md): current and planned observability.

## Runtime and CI

- Python tooling targets Python 3.12.
- GitHub Actions run quality gates, tests, Quarto syntax checks, and deployment workflows.
- The repository includes Docker and Compose support for reproducible static-site preview.

Build and run the preview image:

```bash
docker build -t affinedrift:local .
docker run --rm -p 8080:8000 affinedrift:local
```

Or use Compose:

```bash
docker compose up --build
```

The container build now verifies the Quarto `.deb` checksum, installs Python
dependencies from the hash-locked `requirements-docker.lock`, and emits
`docs/build-provenance.json` inside the rendered site. Refresh the lock with:

```bash
py -3.12 -m piptools compile --allow-unsafe --generate-hashes --resolver=backtracking --output-file requirements-docker.lock requirements.txt
```

do not bake secrets into the image; pass credentials through local environment
variables or your deployment platform's secret store.

The container preview is available at `http://localhost:8080`.

## Contributing

This is a personal research and writing portfolio. Issues are useful when they
identify a source problem, broken link, reproducibility gap, unclear assumption,
or technical correction.

## License

All content is the property of the repository owner. Code structure may be used
as a template for similar projects with attribution.
