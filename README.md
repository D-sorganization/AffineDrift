# AffineDrift

[![CI Standard](https://github.com/D-sorganization/AffineDrift/actions/workflows/ci-standard.yml/badge.svg)](https://github.com/D-sorganization/AffineDrift/actions/workflows/ci-standard.yml)
[![Built with Quarto](https://img.shields.io/badge/built%20with-Quarto-blue.svg)](https://quarto.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**The published site is at [affinedrift.com](https://affinedrift.com).** This
repository holds its source. If you came to read the material, read it there;
the files here are Quarto markdown and do not render as pages on GitHub.

AffineDrift is a scientific writing and modeling portfolio covering golf
mechanics, multibody dynamics, and nonlinear control. It publishes
source-bounded exposition, model notes, critique responses, and links to
executable companion work, rather than presenting a finished theory as a settled
result.

The established material is the underlying mechanics and control literature. The
contribution here is the application, synthesis, and review workflow around golf
swing models: assumptions, derivations, references, simulations, and open
limitations tracked together and visible to a reader.

## Read the material

| Start here                                                                                | What it covers                                                   |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [The Physics of Golf](https://affinedrift.com/articles/The_Physics_of_Golf/quarto/)       | The main mechanics exposition, textbook length                   |
| [The Geometry of Motion](https://affinedrift.com/articles/The_Geometry_of_Motion/quarto/) | The control and differential-geometry narrative                  |
| [Books and textbooks](https://affinedrift.com/books/)                                     | The full series, including the four-volume roadmap               |
| [Technology overview](https://affinedrift.com/pages/technology.html)                      | Force measurement, motion capture, launch monitors, club fitting |
| [Golf Modeling Suite](https://affinedrift.com/models/models.html)                         | The executable models behind the exposition                      |
| [Critiques and responses](https://affinedrift.com/critiques/)                             | Objections, assumptions, and evidence gaps                       |
| [Bibliography](https://affinedrift.com/resources/bibliography.html)                       | Source provenance for every cited claim                          |
| [Learning paths](https://affinedrift.com/resources/learning-paths.html)                   | Suggested reading orders by background                           |

For readers who want the shortest technical route: **The Physics of Golf** for
mechanics, then **Critiques and Responses** for what the models do not settle.

## Companion repositories

| Repository                                                                              | Relationship                                          |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| [UpstreamDrift](https://github.com/D-sorganization/UpstreamDrift)                       | The executable multi-engine simulation platform       |
| [Tools](https://github.com/D-sorganization/Tools)                                       | Shared engineering and analysis applications          |
| [rate-of-closure-explorer](https://github.com/D-sorganization/rate-of-closure-explorer) | Interactive companion to the reference-point research |
| [Launch-Monitor-Data](https://github.com/D-sorganization/Launch-Monitor-Data)           | Traceable public launch-monitor data and provenance   |

## What is checked, and what is not

Continuous integration validates Quarto syntax, internal and external links,
front matter, the Python test suite, and selected repository quality gates. Some
pages carry explicit provenance notes separating standard control-theory results
from AffineDrift's golf-specific interpretations.

That validation does not establish that any biomechanical interpretation holds
in vivo. Treat model-dependent quantities, optimization narratives, and proposed
golf-specific metrics as hypotheses unless a page ties them to a cited source, an
executable model, or a stated numerical experiment.

Technical claims are expected to rest on stated assumptions, cited sources, model
code, or explicit numerical experiments, with limitations visible wherever the
evidence is incomplete. Computational tools support drafting, refactoring, and
repeatable checks; they are not the scientific claim of the project.

## Building the site

AffineDrift is a Quarto static site deployed to GitHub Pages at
`affinedrift.com`.

```bash
git clone https://github.com/D-sorganization/AffineDrift.git
cd AffineDrift
quarto preview
```

The preview opens at `http://localhost:4000`.

A container build is also available, either directly:

```bash
docker build -t affinedrift:local .
docker run --rm -p 8080:8000 affinedrift:local
```

or through Compose:

```bash
docker compose up --build
```

The preview is then served at `http://localhost:8080`. The image verifies the
Quarto package checksum, installs Python dependencies from the hash-locked
`requirements-docker.lock`, and writes `docs/build-provenance.json` into the
rendered site. Pass credentials through environment variables or your deployment
platform's secret store; do not bake secrets into the image.

Python tooling targets Python 3.12. See
[the contributor guide](CONTRIBUTING.md) for the full local setup, and
[docs/development/](docs/development/) for the release and build process.

### Source layout

```text
AffineDrift/
├── index.qmd            Site homepage
├── _quarto.yml          Site configuration and navigation
├── articles/            Long-form articles and textbook volumes
├── books/               Book series landing pages
├── models/              Model documentation pages
├── critiques/           Critique and response record
├── resources/           Bibliography, article index, learning paths
├── pages/               Standalone pages: manifesto, technology, reviews
├── src/                 Python modules supporting figures and calculations
├── styles.css           Site styling
├── js/                  JavaScript modules
├── tests/               Python test suite
└── docs/                Rendered output and repository documentation
```

## Repository documentation

**Writing and content**

- [Writing style guide](docs/development/writing-style-guide.md) — prose standards and the constraints CI enforces on page edits.
- [Canonical parameters](PARAMETERS.md) — symbols, units, and parameter ranges used across the site.
- [Notation](NOTATION.md) — notation conventions.
- [Textbook series architecture](docs/development/geometry_of_motion_architecture.md) — series structure and issue-to-deliverable tracking.

**Development**

- [Contributing](CONTRIBUTING.md) — how to propose a change.
- [Code style guide](docs/development/code-style-guide.md) — Python, JavaScript, CSS, and Quarto standards.
- [Testing guide](docs/development/testing-guide.md) — test patterns, fixtures, and conventions.
- [Public site verification](docs/development/public-site-verification.md) — every-route visual,
  responsive, and revision-bound deployment contract.
- [Git workflow](docs/development/git-workflow-guide.md) — branch strategy, commits, and pull requests.
- [API reference](docs/api-reference.md) — the public API of the modules under `src/`.
- [Repository inventory](docs/development/repository_inventory.md) — component status and known gaps.
- [Security guidelines](docs/development/security-guidelines.md) — secrets handling, input validation, static analysis.

**Operations**

- [Troubleshooting](docs/operations/troubleshooting-guide.md) — build and deployment failures.
- [Service targets](docs/operations/slo-targets.md) — CI and deployment objectives.
- [Incident response](docs/operations/incident-response-playbooks.md) — deployment and outage procedures.

## Contributing

This is a research and writing portfolio maintained by one author, so pull
requests that rewrite editorial content are unlikely to be merged. Issues are
welcome and useful when they identify one of the following:

- A source problem: a misattributed, misread, or missing citation.
- A technical error in a derivation, model, or numerical result.
- A reproducibility gap between a stated result and the code that produces it.
- An assumption stated too weakly, or an unstated one.
- A broken link, rendering fault, or accessibility problem on the site.

Use the [issue templates](.github/ISSUE_TEMPLATE/) — there is one for content
corrections, one for critique responses, and one for proposing an article.
Report security issues through [SECURITY.md](SECURITY.md), not through public
issues.

## License

Source code is released under the MIT License; see [LICENSE](LICENSE).

Written content, figures, and the textbook material published on
[affinedrift.com](https://affinedrift.com) are reserved by the author. Quote and
cite them under normal academic practice; ask before republishing them in
substantial part. [COPYRIGHT.md](COPYRIGHT.md) states exactly which files fall
under each, and gives the citation format.
