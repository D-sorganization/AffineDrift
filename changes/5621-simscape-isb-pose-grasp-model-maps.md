---
issue: 5621
summary: "Add Simscape golfer-scapula/2.0 DOF/sign table generator, ISB Cardan conventions, and two-hand grasp map"
---

- Add `src/tools/simscape_golf_map.py`, `data/upstreamdrift_golf_models/simscape_golfer_scapula_v2.json`, and `models/_generated/golf-model-maps-simscape.qmd` via `scripts/generate_golf_model_maps.py`.
- Document ISB Cardan conventions, golf aliases, pose-estimator included-angle warning, and 6x12 two-hand grasp closure in `models/golf-model-maps.qmd`, `models/models-simulink.qmd`, and `articles/technology-motion-capture.qmd` (`Refs #5621`).
