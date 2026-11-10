# Alpha War v1 closure evidence (lane A3)

**Audit ref:** `research/alpha-war-thesis` @ `320a9f676c197729680a752d4e1b4ba7f376abb4`  
**Auditor:** `cursor-cloud-wave-20261109-a3`  
**Date:** 2026-11-09  
**Local check:** `cd research/alpha-war/calcs && python3 -m unittest discover -v -p 'test_*.py'` → **44 passed, 9 skipped** (UpstreamDrift unset).

**Anchor note (#5459):** Appendix A / Box 3.3 fixes merged in #5500 were reverted on thesis by #5513; restoration is **in flight** on [PR #5554](https://github.com/D-sorganization/AffineDrift/pull/5554) (`59a66450`), not on thesis HEAD above.

---

## AD #5463 — separate assumed shaft-rebound loads from model results

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Relabel 11°/465 N/+10 N·m as hypothetical | **Met** | Draft §7.6 / Table 7.11 (`alpha-war-v1.md` ~1416–1451); JSON `study_6.two_hand_beam_rebound_wrench_model.scenario` + `inputs_are_uncited` |
| EI/geometry/boundary for capacity inputs | **Met (negative scope)** | Draft and JSON explicitly omit EI/length for hypothetical row; matched rollout documents flexible params in §7.6 prose |
| Shaft-on-hands vs hands-on-club conventions | **Met** | Draft Table 7.10 vs 7.11 separation; README Study 6 notes |
| Table 7.10 from stored outputs; full accel decomposition | **Met** | `test_table_7_10_study_6_matches_json_5463` (`test_alpha_war_draft_table7.py` **172–211**) — contribution sums, gravity/joint/shaft terms, interface norm |
| Remove “guarantee/overpower” conclusions | **Met** | Same test **211**: `assertNotIn("overpowering voluntary wrist muscles", section_76.lower())`; CLM-MCH-03 relabeled in draft ~1540 |

**Integration (optional):** `test_study_6_shaft_flex_contribution` (`test_alpha_war_sensitivity_suite.py` **141–164**) — requires `ALPHA_WAR_UPSTREAM_DRIFT_ROOT`.

---

## AD #5465 — reproducibility from pinned dependencies

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Configurable path + pinned commit + input hashes | **Met** | `alpha_war_upstream.py`; `upstream_drift.lock.json`; `test_upstream_lock_has_full_commit_sha` (`test_alpha_war_reproducibility.py` **24–30**) |
| Regeneration manifest (versions, hashes) | **Partial** | `alpha_war_regeneration_manifest.json` records `python_version`, `suite_version`, `studies_sha256`, WSCG hashes; **no** pinned `numpy`/`scipy` versions in manifest |
| Clean-environment regenerate command | **Met** | `regenerate_calculations.sh` — fails closed without pin-matched clone |
| Tests on data-to-table/figure values | **Met** | `test_table_7_1_matches_calculations_json`, `test_golden_table7_anchors_unchanged`, `test_fig1_transport_stations_matches_json` / `test_fig3_club_roll_projection_matches_json` (`test_alpha_war_figures.py`) |
| Skipped deps must not count as scientific success | **Gap** | Nine `test_alpha_war_sensitivity_suite.py` cases **skip** when env unset; default CI/local unittest run reports **OK (skipped=9)** with no required UpstreamDrift job |

**Repo CI hook:** `tests/test_alpha_war_calcs_reproducibility.py` re-exports lock/manifest tests only (not full suite integration).

---

## AD #5460 — double-pendulum inertia and free-hinge signs

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Single diagram: angles, torques, positive uncocking | **Gap** | Appendix B.1 (`alpha-war-v1.md` **1865–1878**) is equations only; no dedicated pendulum figure |
| Derive M, velocity, gravity from T,V; Hessian check | **Gap** | Prose states `M_{11}=J_1`, etc. (**1877–1878**); **no** automated derivation or Hessian test |
| τ₂=0 limit with gravity retained | **Partial** | Free-hinge display eq. **1899–1900**; not covered by unittest |
| Independent two-link numeric compare / limits | **Gap** | No `test_*5460*` or `alpha_war_double_pendulum*.py` on thesis HEAD |
| Remove unconditional negative-torque necessity | **Partial** | B.2 lists kinematic conditions (**1888–1895**); **1901** still reads “must apply **negative** hinge torque” without test lock |
| Reconcile §3.3, §5.5, B.1–B.2, verdicts | **Partial** | Narrative aligned in draft (#5501 merge); **no** regression test tying sections |

**First queued issue with substantive remaining work** after #5463/#5465 audit (per lane order: #5465 gap is policy/CI; #5460 gap is missing test module).

---

## AD #5461 — roll projection, bases, sign conventions

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Orthonormal shaft/plane frame + degeneracies | **Met (draft)** | Appendix B.0 Table B.1 + prose (`alpha-war-v1.md` **1836–1844**); `test_v1_assembly_boxed_caveats_and_no_verify_5401` checks B.0 headers (**152–161**, `test_alpha_war_draft_table7.py`) |
| Roll matrix derived once; used in prose/tables/figures | **Met** | Roll law **1859**; `run_study_3_frame_conventions` builds `jacobs_club_frame_roll_sweep` (`alpha_war_sensitivity_suite.py` **409**); Figure 3 from JSON |
| Tests: 0°, ±90°, norm invariance, φ*, round trip | **Partial** | `test_study_3_frame_conventions_norm_invariance` + `test_study_3_club_roll_zero_crossing_matches_sweep` (`test_alpha_war_sensitivity_suite.py` **73–107**) — **skipped** without UpstreamDrift; static JSON checks: `test_fig3_club_roll_projection_matches_json` (**83–104**, `test_alpha_war_figures.py`) |
| Explicit axis transforms (no mid-example sign flip) | **Met (draft)** | B.0 mapping eq. **1856–1859** |
| Separate math transform from Nesbit/Jacobs pipeline claims | **Met** | Table B.1 labels camps; Study 3 marked illustrative in calcs README |

---

## AD #5462 — WSCG provenance and ZTCF interpretation

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Label WSCG model-derived / planar | **Met** | Draft ~583, 621, 1180; `test_wscg_ztcf_provenance_language_present_5462` (**63–70**, `test_alpha_war_draft_table7.py`) |
| Define zeroed wrist commands + provenance | **Met** | Draft ~621–636, glossary ~1721; JSON generation_provenance in reproducibility test |
| 86.04% as same-state modeled ratio, not muscle share | **Met** | Draft ~636, 1250–1278; `test_ztcf_share_derived_from_json_matches_draft` (**47–61**) |
| vs forward torque-cut / relaxed-grip experiment | **Met** | Draft CLM-MCH-04 ~1538; Box 3.4 / Study 5 wording |
| Remove universal/causal claims in summary/Fig 1/2/8.1 | **Met** | Layer 2 verdict “Not Declared Settled”; figure captions include “modeled magnitude ratio” |
| Propagate to `work/03_claims.md` | **Partial** | `work/03_claims.md` CLM-MCH-04 updated (~155) but **no** explicit `86.04%` or “not measured muscle” line in work file; **no** automated test on `work/03_claims.md` |

---

## AD #5464 — hand-force bound and muscle-speed inference

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Box 3.1 arithmetic (per-hand lbf, not halved) | **Met** | `test_differential_force_for_plus_30_nm_couple`, `test_opposed_hands_each_carry_full_differential_magnitude` (`test_alpha_war_hand_force_bounds.py` **30–42**) |
| Draft §5A.1 + CLM-SGN-05 relabel | **Met** | `TestAlphaWarDraftHandForceBoundProse` (**70–92**) |
| Separate club vs wrist vs fascicle velocity | **Met** | `test_section_5a_separates_velocity_quantities` (**84–92**) |

---

## Recommended next PR (lane queue)

1. **#5463** — criteria met on thesis HEAD; no implementation PR required (closure = Barb/Astra).  
2. **#5465** — implement CI or guard that fails (or documents deferral) when `test_alpha_war_sensitivity_suite` integration is skipped in release gates; extend manifest dependency pins.  
3. **#5460** — add `test_alpha_war_double_pendulum.py` (+ minimal `alpha_war_double_pendulum.py`) per acceptance (first **code** follow-on if #5465 deferred).

Agent: cursor-cloud-wave-20261109-a3 (composer-2.5).
