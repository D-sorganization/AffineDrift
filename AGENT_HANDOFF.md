# Agent Handoff — AffineDrift

Last updated: 2026-08-20

This is current operational state. Historical detail belongs in git/GitHub.

## Publication Architecture & Proximal-to-Distal Monograph

AffineDrift is the publication home of textbooks (_The Physics of Golf_, _The Geometry of Motion_, _Volumes I–IV_), articles, and scientific monographs. UpstreamDrift remains the computational, claim, and evidence authority for the proximal-to-distal program:

- **Published Technical Monograph**: [`articles/proximal_distal_energy_transfer/index.qmd`](articles/proximal_distal_energy_transfer/index.qmd)
  - 34 comprehensive technical chapters (`chapters/_ch01_...` to `_ch09_...`) covering multibody mechanics, exact interaction-force decompositions, multi-station Coulomb friction, and Latin Hypercube parameter sweeps.
  - Published technical PDF: [`proximal_distal_energy_transfer.pdf`](articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf) (231 pages, >= 69,000 words).
  - [`source_manifest.json`](articles/proximal_distal_energy_transfer/source_manifest.json) pins UpstreamDrift protected squash `6e28baef54a04da714f1120c71c49058d7d7ebee`, the release-manifest and claim-registry digests, the embedded generation environment, and both PDF digests. Digest equality establishes provenance, not independent scientific confirmation.
  - The pinned profile is computational-release ready. It is not archival/PID ready: the PDF is untagged and retains Type 3 and unembedded font resources.
  - Dual web & PDF rendering registered in `_quarto.yml` (resources, `books-nav` sidebar, and `Read` navbar).
- **Lay Companion Book**: [`articles/proximal-distal-a-journey-through-the-swing.qmd`](articles/proximal-distal-a-journey-through-the-swing.qmd) (30 chapters, PDF).
- **Web Summary Article & Workbench**: [`articles/proximal-distal-energy-transfer.qmd`](articles/proximal-distal-energy-transfer.qmd) and [`articles/proximal-distal-model-workbench.qmd`](articles/proximal-distal-model-workbench.qmd).

## Shipped Technology & Biomechanics Articles

- **Club Fitting Simulation & Identification (Epic #4549, Child C9)**:
  - [`articles/technology-club-fitting.qmd`](articles/technology-club-fitting.qmd): Forward twist counterfactuals, shaft forward dynamics (lead/lag/droop), divergence theorem watertight polyhedral mesh inertia tensor integration, and OEM fitting document interchange.
- **Multibody Impact Coupling & Heavy Hit (Epic #4562, Child H5)**:
  - [`articles/technology-heavy-hit-impact-coupling.qmd`](articles/technology-heavy-hit-impact-coupling.qmd): Proves tau^2 decoupling law (contact duration ~400 us vs flexural wave transit ~2300 us), apparent striking mass decoupling fraction eta > 0.99, and MJCF/URDF/.osim model interchange.

## Research Evidence & UpstreamDrift Alignment

- Source release is pinned to UpstreamDrift protected squash `6e28baef54a04da714f1120c71c49058d7d7ebee`. #8751/#8752 remain open against their unchanged acceptance criteria.
- Source release: 571 artifacts, 295 atomic claims, 2,100 evidence references, 301 local artifacts, and 78 external URLs; no source-manifest mismatch remains.
- #3882 owns the immutable publication-projection contract, portable links, generated metadata, and deployment qualification.
- **Critical Adverse Results**:
  - Ground screen: 0/384 coupled--fixed cells admitted under registered 5% match (ground damping asymmetry). Post-hoc screen admits 60 cells with mixed signs.
  - Shaft screen: 126/384 coupled--rigid cells match, rejecting universal passive-shaft speed benefit.
  - Initialization sensitivity: natural-zero (32.8 N), gravity-only (565.5 N), conditional (510.3 N) peak ground forces.
- Governed human data (#8556): synchronized bilateral 6-axis grip wrenches remain the external validation gate.

## Launch-Monitor Professional Release Program

- AffineDrift issue #3883 is the publication stream under the cross-repository Tools epic #4583.
- `articles/Launch_Monitor_Technology_Review/sections/11-validation-program.tex` documents the approved Release A/Release B boundary, ShotLink training quarantine, explicit-identity rule, and UpstreamDrift statistical authority.
- The technology review may publish qualified aggregate findings and method limitations, but it must not expose private source files or describe an internal emulator as a certified vendor model.
- Rebuild the complete PDF and inspect every rendered page whenever this chapter, the program results, or the running-header contract changes.

## Definitional Integrity (Epic #3834 — Verified Closed)

- `NOTATION.md` is normative public semantic authority.
- Drift is the complete autonomous vector field of the declared plant.
- Zero declared control does not mean zero muscle activation or effort.
- DCR compares drift with bounded control capacity.

## Gate Commands & Verification

Run locally before pushing:

```bash
python -m pytest tests/test_proximal_distal_*.py -v
python -m pytest tests/ -q
python scripts/check_terminology.py
python scripts/check_image_budget.py
python -m ruff check .
```

Monograph verification:

```bash
python -m pytest tests/test_proximal_distal_technical_monograph_contract.py -v
```

Do not infer human technique/physiology; bypass branch protection; add unverified claims; or duplicate computational engines from UpstreamDrift.
