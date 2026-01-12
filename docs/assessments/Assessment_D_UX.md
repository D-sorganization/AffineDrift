# Assessment D Results: User Experience & Developer Journey

## Executive Summary

*   **Website UX is Strong**: The Quarto-based website (`AffineDrift`) offers a polished, responsive user experience for readers.
*   **Developer UX is Mixed**:
    *   **Pros**: `quarto preview` allows for near-instant local feedback. CI/CD automation handles deployment transparently.
    *   **Cons**: Python tools are CLI-only with no unified launcher, requiring shell proficiency.
*   **Installation Friction**: `pip install -r requirements.txt` is standard, but the lack of a virtual environment setup script or `Makefile` adds a manual step.
*   **Discovery**: The `tools/` directory is not well-advertised in the main `README.md`, making tool discovery difficult for new contributors.

## Time-to-Value Metrics

| Stage             | Time (Est) | Friction Level | Notes                                      |
| ----------------- | ---------- | -------------- | ------------------------------------------ |
| Installation      | 5 min      | Low            | Standard Python/Quarto setup.              |
| First run (Site)  | 2 min      | Low            | `quarto preview` works out of the box.     |
| First run (Tools) | 15 min     | High           | Must navigate to `tools/`, figure out CLI. |
| First result      | 5 min      | Low            | Site renders quickly.                      |

## Scorecard

| Category              | Score | Evidence                                           | Remediation                     |
| --------------------- | ----- | -------------------------------------------------- | ------------------------------- |
| Installation Ease     | 8/10  | Standard requirements.txt.                         | Add `make install` or `setup`.  |
| First-Run Success     | 9/10  | Quarto is reliable.                                | N/A                             |
| Documentation Quality | 7/10  | Good for site, poor for tools.                     | Improve Tool docs.              |
| Error Clarity         | 6/10  | CLI scripts print generic errors.                  | Improve error messages.         |
| API Ergonomics        | 5/10  | Inconsistent CLI args across tools.                | Standardize (Click/Typer).      |
| **Overall UX Score**  | **7.0/10** | **Good for Readers, Average for Devs.**       |                                 |

## Remediation Roadmap

**48 Hours**
1.  Add `make setup` (or `Justfile`) to automate venv creation and dependency install.

**2 Weeks**
1.  Create a "Tool Index" page or section in documentation to aid discovery.
