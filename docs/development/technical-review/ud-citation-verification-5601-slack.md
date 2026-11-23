# UpstreamDrift Citation Verification for the Slack Articles (#5601)

**Scope:** every UpstreamDrift permalink in `articles/slack-management-linked-systems.qmd`
and `articles/slack-takeup-identifiability.qmd`. This closes the "not checked" items for
these two articles in finding `ball` F7 of [#5601](https://github.com/D-sorganization/AffineDrift/issues/5601).
**Verified on:** 2026-11-23, by reading git objects in a local UpstreamDrift clone (no checkout
of `main`; every row below was read at the pinned commit, not at a branch tip).
**Guard:** `tests/test_slack_ud_citation_record_5601.py` fails if either article gains, drops or
re-pins an UpstreamDrift permalink without this record being updated.

## Pins

| Short | Full commit | Date | Subject |
| --- | --- | --- | --- |
| `3fd2a59e` | `3fd2a59e390523169df846a3bbb395a6203c382c` | 2026-10-21 | chore(changes): collate 1 change fragment(s) (#13613) |
| `92100115` | `92100115ea0be0d6744dcf7a4504ec8453fae6fa` | 2026-08-14 | research: audit typed slack dynamics and identifiability (#8626) |

Both are reachable commits, and `92100115` is an ancestor of `3fd2a59e`.
`typed_slack_dynamic_study.json` is byte-identical at both pins (`git diff` is empty), so the two
pins do not disagree about any quoted number. `articulated_distributed_grip_atlas.json` does not
exist at `92100115`, which is why the atlas link uses `3fd2a59e`.

## Results

| Article claim | Permalink path at pin | Result |
| --- | --- | --- |
| Null-space program is "publication blocked" (management line 60, takeup line 67) | `docs/research/loop_nullspace/publication_gate.md` at `3fd2a59e`; heading `## Scope and Current Status` exists and says "Current status: **publication blocked**" | Holds |
| "None of this says which grip a golfer uses" (management line 65) | `docs/research/loop_nullspace/closure_alternatives_report.md` line 57 at `3fd2a59e` | Holds |
| Admitted velocity space grows 8 (weld), 9 (revolute), 11 (ball); allocation nullity 6, 5, 3 | same report, lines 21-40 | Holds |
| Each grip model "is a declared alternative and none is validated" (management line 205) | same report, line 235 | Holds |
| Grasp map `G` is 6x12, so its kernel has six dimensions (takeup line 76, `#L524`) | `docs/research/loop_nullspace/loop_nullspace.tex` lines 523-527 at `3fd2a59e`: `G` in `\R^{6\times12}`, `w=Gy` | Holds |
| Nullity after observation is `nullity(A) - rank(E_x N)` (takeup table, `L274`) | same file, line 274 | Holds |
| A scaled singular value below one is "not resolved by the data" (takeup table, `L287`) | same file, lines 285-289 | Holds |
| No stiffness or co-contraction inference from net joint torques (takeup table, `L1783`) | same file, lines 1783-1784 | Holds |
| An earlier unsourced dead-zone duration was removed upstream (management line 214) | same file, line 1762: "Bosch 15--40 ms dead zone & REMOVED" | Holds |
| `transmission_backlash` "is represented by the existing memoryless dead-zone-plus-damping surrogate; a stateful rate-independent play operator is not represented" (management line 87) | `docs/research/proximal_distal_energy_transfer/data/typed_slack_dynamic_study.json`, `limitations[1]`, at `92100115` and `3fd2a59e` | Holds, verbatim |
| Five slack classes; every local three-parameter sensitivity matrix is full rank (management line 189) | same file, `identifiability`, both excitations (`slow_sine`, `multisine_reversal`), five classes, `rank` = 3 in all ten cells | Holds |
| Contact-disengagement and biological-series-compliance differ by 1.96 % normalized output RMSE | `pairwise_normalized_output_rmse_multisine`, key `contact_disengagement__biological_series_compliance` = 0.019574147... | Holds |
| H10 says "preload matching reverses open/taut classification" (management line 189) | `docs/research/proximal_distal_energy_transfer/MODEL_COMPLETION_FALSIFICATION_MATRIX.md` row H10 at `3fd2a59e` | Holds |
| Atlas: `maximum_transition_count = 0`, `maximum_open_fraction = 1.0`, 80 openings, 186 reattachments, 576 trajectories, friction coefficients 0 and 0.35, "equipment-provisional bounds", "not_identified" (management line 191) | `docs/research/proximal_distal_energy_transfer/data/articulated_distributed_grip_atlas.json` at `3fd2a59e`: `results.maximum_transition_count` 0, `results.maximum_open_fraction` 1.0, `results.registered_event_opening_count` 80, `results.registered_event_reattachment_count` 186, `design.trajectory_count` 576, `design.friction_coefficients` [0.0, 0.35], schema `articulated-distributed-grip-atlas/v3`, `claim_boundary` text | Holds |
| "VAR-03 at L279" is the instrumented-grip blocker (takeup line 227) | `publication_gate.md` line 279 at `3fd2a59e` is the VAR-03 row, status DEFERRED, "No instrumented-grip data" | Holds |
| "UpstreamDrift VAR-03 to VAR-05 are deferred" (takeup line 67) | VAR-03, VAR-04 and VAR-05 rows are all DEFERRED | Holds |
| UpstreamDrift paths are under `docs/research/` (takeup table caption) | `git ls-tree 3fd2a59e docs/research/` resolves | Holds |

## One Discrepancy: VAR-05 Is Not Deferred for Lack of an Instrumented Grip

`articles/slack-management-linked-systems.qmd` line 60 says: "Its grip-preload and co-contraction
validations (VAR-04 and VAR-05) are deferred for lack of an instrumented grip."

At `3fd2a59e` the gate table gives different reasons:

- VAR-04 (grip preload): "No instrumented grip; DV-12554 deferred". The article is right.
- VAR-05 (co-contraction or joint impedance): "Impedance is declared, not measured (#12722);
  DV-12554 deferred". Its required evidence is perturbation-derived impedance and EMG
  co-contraction ratios, not a grip wrench. The article is imprecise.

A correct wording is: "VAR-04 is deferred for lack of an instrumented grip, and VAR-05 because
joint impedance is declared rather than measured." Nothing else in the argument depends on the
sentence, and `slack-takeup-identifiability.qmd` line 67 avoids the problem by not stating a reason.

**Why this record does not edit the article.** The article is hashed in
`data/trust/claim_audit_inventory.json` (`evidence_sha256`), and pre-commit and CI both run
`python3 -m scripts.regenerate_claim_audit_evidence --check`. Editing the sentence therefore
requires regenerating `data/trust/claim_audit_inventory.json` and
`data/trust/generated/claim_audit_report.json`, which many open pull requests already change.
The one-sentence fix is best folded into the next change that already refreshes those files.

## Deliberately Not Changed

- **Two pins in one article.** Management cites `3fd2a59e` and `92100115`. Both resolve and agree,
  so this is consistent but not minimal. Re-pinning the two typed-slack links to `3fd2a59e` is safe
  (identical bytes) but would also change the per-route entries in `data/companion/pins.json`, a
  file another open pull request is rewriting.
- **Tools-repository and AffineDrift-internal claims** from `ball` F7 (`green-simulation.qmd`,
  `impact-optimality-and-model-limits.qmd`, `technology-heavy-hit-impact-coupling.qmd`) are out of
  scope here; they are not UpstreamDrift claims.

## Reproduce

```bash
cd UpstreamDrift
P=docs/research/proximal_distal_energy_transfer
git show 3fd2a59e:$P/data/articulated_distributed_grip_atlas.json | python -c "import json,sys; print(json.load(sys.stdin)['results'])"
git show 92100115:$P/data/typed_slack_dynamic_study.json | python -c "import json,sys; d=json.load(sys.stdin); print(d['limitations'][1]); print(d['pairwise_normalized_output_rmse_multisine']['contact_disengagement__biological_series_compliance'])"
git show 3fd2a59e:docs/research/loop_nullspace/publication_gate.md | sed -n 279p
git show 3fd2a59e:docs/research/loop_nullspace/loop_nullspace.tex | sed -n '274p;287p;524,527p;1762p;1783,1784p'
git diff --stat 92100115 3fd2a59e -- $P/data/typed_slack_dynamic_study.json   # empty: identical
```
