# Agent Handoff — AffineDrift

Updated: 2026-08-29. Current-state only; use git and GitHub for history.

## Protected Authority

- Protected `main` is `b28fd8227d5003c752a16426ed508e13ff2e137a`.
- No AffineDrift pull request was open when this handoff was refreshed.
- The primary checkout at `C:\Users\diete\Repositories\AffineDrift` is clean,
  on `main`, and equal to `origin/main`.
- Numerous older local worktrees remain. Their presence is not evidence that an
  issue or pull request is active. Verify GitHub state and exact ancestry before
  resuming any of them.

## Merge Governance

- Use full pull requests and ordinary protected merges; never bypass checks,
  reviews, or branch protection.
- The live ruleset requires zero approving reviews. Human review remains
  optional for risk or expertise, not a standing release gate.
- Regenerate controlled outputs from canonical source, run exact-head gates,
  and verify the protected merge plus post-merge deployment before claiming
  publication.

## Proximal–Distal Publication Boundary

- UpstreamDrift is the computational, claim, evidence, and campaign authority.
  AffineDrift is the immutable publication and explanatory layer.
- The current protected projection is AffineDrift #3992 / PR #3993. It pins the
  protected UpstreamDrift #9151/#9152 authority and the 252-page technical PDF.
- Canonical technical source:
  `articles/proximal_distal_energy_transfer/index.qmd`.
- Qualified local PDF:
  `articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf`.
- `source_manifest.json` and
  `python scripts/verify_proximal_distal_projection.py` govern immutable source,
  figure, adaptation, claim-registry, and PDF identity.
- UpstreamDrift #9153 is still an unprotected structural campaign. Do not edit
  or refresh the AffineDrift projection until #9153 is protected, its release
  manifest is immutable, and all failure boundaries remain visible.
- Do not infer human technique, anatomy, physiology, or coaching effects from
  structural-model evidence.

## Research-Readiness Program

- #4041 is protected on current `main` through PR #4079. The public lifecycle
  library is simulation-ready only; it does not mint publication authority or
  measured-human validation.
- #4042 owns the external immutable release and claim-promotion adapter. Treat
  local branches as unapproved until ordinary protected publication completes.
- #4034–#4040 define falsifiability programs for the model ladder, bilateral
  wrenches, active impedance, neural timing, impact timing, participant-held-out
  generalization, and equipment response. Preserve unavailable and adverse
  evidence; never substitute manufactured fixtures for human data.
- #4021/#4063 govern route-level scientific claim audit and trust surfaces.
  Current protected main includes the #4075/#4077 deploy and heading repairs.

## Markerless Mocap Boundary

- AffineDrift #3954 is the immutable publication projection; Tools owns public
  contracts and UpstreamDrift owns orchestration and scientific computation.
- AffineDrift #3956 is the camera evidence registry. Candidate devices and
  manufactured fixtures are not procurement or validation authority.
- Never publish raw video, PII, secrets, private evidence, or AGPL runtime
  components. Public projection records must be revision-pinned and fail closed.

## Must-Read Files

1. `AGENTS.md` and `CLAUDE.md` — repository and publication policy.
2. `SPEC.md` — current scientific/publication contracts.
3. `articles/proximal_distal_energy_transfer/source_manifest.json` — immutable
   upstream projection boundary.
4. `reports/scientific-claim-audit.md` — governed route classification.
5. `scripts/verify_proximal_distal_projection.py` — projection verifier.

## Validation

```powershell
python -m pytest tests/test_proximal_distal_*.py -v
python -m pytest tests/test_markerless_mocap_projection_contract.py -v
python -m pytest tests/test_mocap_camera_registry_contract.py -v
python -m ruff check .
python -m black --check .
python scripts/check_title_case.py
```

For publication work, also render Quarto from canonical sources, run site
health/publication enforcement, and inspect responsive output in both themes.
Do not treat source tests alone as rendered-publication evidence.

## Ordered Next Actions

1. Leave the proximal–distal projection unchanged while UpstreamDrift #9153 is
   unprotected.
2. When a protected UpstreamDrift release exists, start a clean leased worktree
   from then-current AffineDrift `origin/main` and pin exact source/digests.
3. Run projection, claim-audit, title, link, PDF, site, and browser gates; retain
   adverse and unavailable evidence in the public limitations.
4. Publish through a full protected pull request and verify post-merge deploy.

## Do Not

- Do not duplicate computational engines or edit generated projection files.
- Do not use mutable upstream links as scientific authority.
- Do not revive a stale worktree without fetching and proving exact ancestry.
- Do not promote simulation-ready, manufactured, unavailable, or private
  evidence to validated or published status.
