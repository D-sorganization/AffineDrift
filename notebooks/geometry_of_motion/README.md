# Geometry of Motion Notebooks

This directory hosts executable companion notebooks for the textbook series.

## Bridge contract

- `manifest.json` maps each chapter source anchor to a notebook path.
- `status: "scaffolded"` means the notebook file must exist and include a tutorial title cell.
- `status: "planned"` reserves future chapter notebooks without failing validation.

## Validation

Run:

```bash
pytest tests/test_notebooks_bridge.py
```
