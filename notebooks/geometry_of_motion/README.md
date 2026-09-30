# Tangent-Space Methods for Nonlinear Control and Biomechanics — Notebooks

This directory hosts executable companion notebooks for the textbook series.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/D-sorganization/AffineDrift/main?urlpath=lab/tree/notebooks/geometry_of_motion)

Launch the badge above to open the notebook scaffolds in this directory in a
browser-based JupyterLab session, with no local install required. Each
scaffold currently only establishes its chapter title cell (see "Bridge
contract" below); it does not yet contain the chapter's executable content.
Binder builds the environment from the repository's `environment.yml`, which
installs from `requirements.txt`.

## Bridge contract

- `manifest.json` maps each chapter source anchor to a notebook path.
- `status: "scaffolded"` means the notebook file must exist and include a tutorial title cell.
- `status: "planned"` reserves future chapter notebooks without failing validation.

## Validation

Run:

```bash
pytest tests/test_notebooks_bridge.py
```
