---
title: "Alpha War Branch Audit: Claims, ZTCF Share, and s*/phi* Verification (#5396)"
draft: true
listing: false
status: do-not-publish
date: "2026-11-03"
---

# Branch Audit Report (#5396)

- **Panel Reference:** `research/alpha-war/critiques/panel-th_bb97958bf095.md` (PR #5394, thread `th_bb97958bf095`)
- **Target Branch:** `research/alpha-war-thesis` (Draft PR #5327)
- **Audit Scope:** Cross-check `draft/alpha-war-v0.md`, `work/03_claims.md`, and `calcs/README.md` against `calcs/alpha_war_calculations.json` and `calcs/alpha_war_sensitivity_suite.py`.

## 1. Numerical Audit Against `calcs/alpha_war_calculations.json`

| Quantity | JSON Path & Raw Values | Audited Value | Prior Draft Value | Action Taken |
|---|---|---|---|---|
| **ZTCF passive couple share ($t = 0.2151\text{ s}$)** | `study_2_couple_vs_sum_of_moments.snapshots[7]`: `ztcf_passive_couple_mid_nm = -19.6294255...`, `total_hand_couple_mid_nm = -22.8147657...` | **$86.04\%$** (2-dp ratio: $86.06\%$) | $86.15\%$ | Updated to **$86.04\%$** across `draft/alpha-war-v0.md` (Box 3.4, §7.2) and `calcs/README.md`; enforced via `test_ztcf_share_derived_from_json_matches_draft`. |
| **ZTCF passive couple share ($t = 0.1933\text{ s}$)** | `study_2_couple_vs_sum_of_moments.snapshots[5]`: `-11.1947588 / -14.0805685` | **$79.51\%$** | Listed as raw N·m only | Added **$79.51\%$** simulated share in Box 3.4 and `calcs/README.md`. |
| **Sign-reversal station $s^*$ (Illustrative Tour Driver)** | `study_1_grip_point_transport.analytical_driver_transport_cases[0]`: $C_\alpha = -16.00\text{ N}\cdot\text{m}$, $R_y = -75.00\text{ N}$ | **$+0.2133\text{ m}$** (`+0.213 m`) | $+0.213\text{ m}$ | Explicitly labelled **Illustrative** at every point of use (Box 3.2, §6.1 diagram and prose, Table 7.2, `calcs/README.md`). |
| **Sign-reversal station $s^*$ (Simulated WSCG $t = 0.2151\text{ s}$)** | `study_1_grip_point_transport.wscg_at_minimum_couple`: $C_\alpha = -22.8148\text{ N}\cdot\text{m}$, $R_y = -30.9558\text{ N}$ | **$+0.7370\text{ m}$** (`+0.737 m`) | $+0.737\text{ m}$ ($+0.7368\text{ m}$ in Box 3.2) | Explicitly labelled **Simulated (WSCG Model)** and separated from the illustrative $+0.213\text{ m}$ case in Box 3.2, §6.1 diagram/prose, and Table 7.1. |
| **Clubface roll sign-flip angle $\phi^*$** | `study_3_frame_conventions.input_physical_couple_fsp_nm`: $\mathbf{M}_{\text{FSP}} = (+4.5, +8.0, -15.0)\text{ N}\cdot\text{m} \implies \arctan(15/8)$ | **$61.93^\circ$** | $61.93^\circ$ | Explicitly labelled **Illustrative** in Box 2.1, §6.3, Table 7.4, and `calcs/README.md`. |

## 2. Claim Verdict Relabels & Adjudication Attribution

Per unanimous Stage 5 panel agreement (`th_bb97958bf095`):
1. **`CLM-SGN-01`:** Relabelled from `Refuted / Definitional Artifact` to **`Unverified - convention mapping required`** in `draft/alpha-war-v0.md` (Table 8.1) and `work/03_claims.md` (Table 1 and detailed dossier §3).
2. **`CLM-LIT-05`:** Downgraded from `Settled` to **`Unverified - primary source check required (VRF-04b)`** in `draft/alpha-war-v0.md` (Table 8.1) and `work/03_claims.md` (Table 2).
3. **Verdict Authorship Disclosure:** Added `Adjudicated by: <role>, <date>` attribution to all 28 claim verdicts in Table 8.1 (`draft/alpha-war-v0.md`) and Tables 1–6 (`work/03_claims.md`).
