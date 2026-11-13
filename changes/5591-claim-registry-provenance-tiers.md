---
issue: 5591
branch: "gemini-ct/5591-claim-registry"
summary: "Reconcile claim_registry.json, per-file provenance SHA-256 hashes, ZTCF/DCR wording, and companion software-artifact tiering."
---

- Reconciled `data/trust/claim_registry.json` per-file SHA-256 digests, ZTCF/DCR claim wording, `mathematical_identity` tiering, duplicate-hash check in `scripts/generate_trust_panels.py`, and `software_artifact` companion tiering in `src/affine_control/evidence_presentation/`.
