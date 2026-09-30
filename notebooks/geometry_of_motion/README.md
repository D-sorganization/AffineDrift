# Tangent-Space Methods for Nonlinear Control and Biomechanics — Notebooks

This directory hosts executable companion notebooks for the textbook series.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/D-sorganization/AffineDrift/main?urlpath=lab/tree/notebooks/geometry_of_motion)

Launch the badge above to run every scaffolded notebook in this directory in
a browser-based JupyterLab session, with no local install required. Binder
builds the environment from the repository's `environment.yml`, which
installs from `requirements-docker.lock` (the same pinned dependency set used
by the project's Docker dev image).

## Bridge contract

- `manifest.json` maps each chapter source anchor to a notebook path.
- `status: "scaffolded"` means the notebook file must exist and include a tutorial title cell.
- `status: "planned"` reserves future chapter notebooks without failing validation.

## Validation

Run:

```bash
pytest tests/test_notebooks_bridge.py
```
