# Repository Inventory

## Inventory Map

| Component | Scope | Implementation Status | Known Gaps |
| --- | --- | --- | --- |
| `src/` | Python source modules and tooling | Active | Module-level README coverage was incomplete; now tracked. |
| `src/affine_control/` | Affine control algorithms and optimization code | Active | Needs expanded benchmark/result documentation. |
| `src/tangent_models/` | Tangent-space dynamics/model examples | Active | Additional end-to-end examples needed. |
| `.github/workflows/` | CI/CD and automation pipelines | Active | Workflow ownership notes were missing. |
| `articles/The_Geometry_of_Motion/` | Canonical LaTeX manuscripts | Active | Cross-volume style unification still pending. |
| `books/` | Website-facing textbook pages | Active | Some pages still point to in-progress chapter assets. |
| `notebooks/geometry_of_motion/` | Executable chapter notebook bridge | Active | Full engine-backed simulations remain in progress. |
| `scripts/` | Repo maintenance and validation scripts | Active | Script-level status index to be expanded. |

## Maintenance Note

When adding or significantly changing a primary component:

1. Update the component README with current capabilities.
2. Add or update `Implementation Status` and `Known Gaps` bullets.
3. Refresh this inventory table in the same PR.
4. Run `pytest tests/test_repository_inventory_refresh.py` before opening the PR.
