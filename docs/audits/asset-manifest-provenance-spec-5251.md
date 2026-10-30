# Asset Manifest Provenance Fields Specification (#5251)

## 1. Purpose and Scope

This specification defines the JSON Schema draft (`schemas/asset-manifest-v1.schema.json`) for `asset_manifest.json` files in `AffineDrift` (Idea 4 of parent epic `#5248`, panel `th_0692a05b4cc8`). The schema preserves full backward compatibility with the committed `articles/shot_pattern_analysis/asset_manifest.json` while adding four optional provenance fields at both the manifest root and individual asset entries. No producer pipelines are modified in this specification slice.

## 2. Optional Provenance Fields

| Field | JSON Type / Pattern | Level | Meaning |
| --- | --- | --- | --- |
| `producer_repo_sha` | `string` (`^[0-9a-f]{40}$`) | Top-level and `assets[]` | Full 40-character lowercase hexadecimal Git commit SHA of the producer repository (`UpstreamDrift` or `Tools`) that generated the asset. |
| `tools_contract_version` | `string` (`^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$`) | Top-level and `assets[]` | Semantic version of the `UpstreamDrift` / `Tools` software-fact or physics contract under which the asset was generated. |
| `input_sha256` | `string` (`^[0-9a-f]{64}$`) | Top-level and `assets[]` | Lowercase 64-character hexadecimal SHA-256 digest of the canonical input dataset, launch-monitor ensemble, or source registry consumed by the producer run. |
| `solver_config_sha256` | `string` (`^[0-9a-f]{64}$`) | Top-level and `assets[]` | Lowercase 64-character hexadecimal SHA-256 digest of the canonicalized numerical solver / integrator configuration (time step, tolerances, aerodynamic/contact model flags). |

## 3. Current Assets That Can Populate These Fields

| Current Manifest / Asset Surface | `producer_repo_sha` Source | `tools_contract_version` Source | `input_sha256` Source | `solver_config_sha256` Source |
| --- | --- | --- | --- | --- |
| `articles/shot_pattern_analysis/asset_manifest.json` (`report.pdf`, `summary.png`, `facebook_preview.png`, and 6 club density/flight-path PNGs) | Already present as `study_source_commit` and per-asset `source_commit` (`f3e83ea8aa754d93ea29b8d176a36fa3d4004a7d` in `D-sorganization/UpstreamDrift`). | Populate from the `UpstreamDrift` flight-model contract version exported at `study_source_commit`. | Populate from the SHA-256 digest of the phase-2 shot-pattern Monte Carlo input parameter bundle in `UpstreamDrift`. | Populate from the SHA-256 digest of the trajectory integrator configuration (`refinement_v3` aerodynamic/ball-flight solver settings). |
| `articles/proximal_distal_energy_transfer/source_manifest.json` (`proximal_distal_energy_transfer.pdf` and 264 projection files) | Already recorded at `source.commit` (`b700e58941205af6f673f13ebbffcd30f8cca9d8` in `D-sorganization/UpstreamDrift`). | Populate from the `UpstreamDrift` pointwise-ZTCF / articulated-attribution contract version. | Already recorded at `source.claim_registry.sha256` (`63df7e73...`) and `source.release_manifest_sha256` (`61e9ae4e...`). | Populate from the SHA-256 digest of the forward-dynamics / ZTCF integrator configuration used for the monograph figures. |
| `articles/forward_dynamics_matching/source_manifest.json` (`matching-forward-dynamics-draft.pdf` and 31 manuscript/reference files) | Already recorded at `upstream_commit` (`d7c7d07add0d7407a5a3376d5fe4a97aee9112a0`). | Populate from the `UpstreamDrift` forward-dynamics matching contract version. | Populate from the SHA-256 digest of the reference motion-capture / tracking input trajectories. | Populate from the SHA-256 digest of the shooting/collocation solver configuration (`06_shooting.qmd`, `07_collocation.qmd`). |
| `data/companion/snapshots/27b6eeadbbd970bebb8926a3c83aeaea1f6ee4da-a1c9a799ecceb4e8/manifest.json` | Already recorded at `source.commit` (`27b6eeadbbd970bebb8926a3c83aeaea1f6ee4da`). | Already recorded at `source.package_version` / `schema_version` (`1.0.0`). | Already recorded per input file under `source.inputs[].sha256`. | Not applicable to static software-fact companion inventory (or populate per executable workflow fixture). |
