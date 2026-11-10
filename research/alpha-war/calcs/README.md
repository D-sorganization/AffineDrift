---
title: "Alpha War Supporting Calculations & UpstreamDrift Sensitivity Suite"
draft: true
listing: false
status: do-not-publish
---

# Alpha War Supporting Calculations (`calcs/`)

This directory contains the reproducible calculation and simulation suite supporting Chapters 3, 6, 7, and 8 of `draft/alpha-war-v1.md`. All calculations import and invoke modules from **UpstreamDrift** strictly **read-only**, at the commit pinned in `upstream_drift.lock.json`.

## Files

- `alpha_war_sensitivity_suite.py`: Executable Python calculation suite implementing six studies using `UpstreamDrift` wrench, identifiability, closed-loop, and flexible-shaft modules.
- `alpha_war_upstream.py`: Resolves `ALPHA_WAR_UPSTREAM_DRIFT_ROOT`, verifies the pinned commit and WSCG CSV hashes, and builds regeneration provenance.
- `upstream_drift.lock.json`: Pinned UpstreamDrift repository URL, commit SHA, and SHA-256 digests of WSCG CSV inputs.
- `alpha_war_calculations.json`: Machine-readable output (includes `generation_provenance`).
- `alpha_war_regeneration_manifest.json`: Standalone provenance manifest (output hash, inputs, commit).
- `regenerate_calculations.sh`: Fails unless `ALPHA_WAR_UPSTREAM_DRIFT_ROOT` points at the locked commit; reruns the suite and unit tests.
- `alpha_war_roll_projection.py`: FSP→club roll rotation matrix and `M_alpha,club(phi)` projection (Study 3 / Box 2.1; #5461).
- `test_alpha_war_roll_projection.py`: Orthonormal round-trip, norm invariance, and illustrative φ* guards (no UpstreamDrift).
- `alpha_war_hand_force_bounds.py`: Box 3.1 opposed hand-shear arithmetic for §5A.1 (force couple reconstruction; #5464).
- `test_alpha_war_hand_force_bounds.py`: Verifies couple–force algebra and draft CLM-SGN-05 wording.
- `test_alpha_war_sensitivity_suite.py`: Integration tests (require pinned UpstreamDrift; skipped when env unset).
- `test_alpha_war_reproducibility.py`: Lock/manifest/golden-number guards (no UpstreamDrift checkout required).
- `alpha_war_spatial_wrench.py` / `test_alpha_war_spatial_wrench_power.py`: Appendix A force-first wrench transport and dual power pairing (#5459).

## UpstreamDrift Modules Used (Read-Only)

1. `scripts.research.proximal_distal_energy.two_hand_wrench`:
   - `two_contact_wrench`, `transport_planar_moment`, `resolve_grip_components`, `find_zero_crossings`
2. `scripts.research.proximal_distal_energy.bilateral_wrench_identifiability`:
   - `point_force_wrench_map`, `full_hand_wrench_map`, `audit_linear_map`
3. `scripts.research.proximal_distal_energy.two_arm_closed_loop`:
   - `TwoArmParams`, `TwoArmControl`, `constraint_jacobian`, `kinematics`, `drift_control_attribution`, `contact_wrench`, `decompose_contact_forces`
4. `scripts.research.proximal_distal_energy.flexible_shaft_study`:
   - `FlexibleShaftParams`, `default_initial_state`, `rollout_flexible`, `rollout_rigid`, `shaft_interface_force`
5. Cached WSCG two-hand dataset (`docs/research/proximal_distal_energy_transfer/data/wscg_two_hand_raw/{base,ztcf,delta}.csv`).

## Summary of the Six Quantitative Studies

### Study 1: Reference-Point Transport & Sign-Reversal Locus (`study_1_grip_point_transport`)
Using the planar wrench transport law
$$
M_{\alpha,B} = M_{\alpha,A} - (\mathbf{r}_B - \mathbf{r}_A) \times \mathbf{R} \cdot \hat{\mathbf{e}}_z = M_{\alpha,M} - s_B R_y,
$$
where $s_B$ is the station offset along the shaft from the mid-hands point $M$ toward the clubhead ($s_G = +0.720\text{ m}$ at club COM $G$):
- **Simulated WSCG Minimum Couple ($t = 0.2151\text{ s}$, $v_{\text{head}} = 109.92\text{ mph}$):**
  - Opposed normal hand forces: $F_{L,y} = +228.57\text{ N}$, $F_{T,y} = -259.53\text{ N}$ across $s = 0.0762\text{ m}$ grip separation $\implies$ differential normal force $F_{d,y} = 244.05\text{ N}$, force couple $C_{F,M} = -18.60\text{ N}\cdot\text{m}$, free wrist torque $\tau_{\text{free}} = -4.22\text{ N}\cdot\text{m}$, total midpoint couple $M_{\alpha,M} = -22.81\text{ N}\cdot\text{m}$.
  - Transverse resultant force: $R_y = -30.96\text{ N}$.
  - Transported moment across club stations: Butt end ($s = -0.05\text{ m}$): $-24.36\text{ N}\cdot\text{m}$; Lead wrist ($s = -0.0381\text{ m}$): $-23.99\text{ N}\cdot\text{m}$; Mid-hands ($s = 0$): $-22.81\text{ N}\cdot\text{m}$; Trail wrist ($s = +0.0381\text{ m}$): $-21.64\text{ N}\cdot\text{m}$; Mid-shaft ($s = +0.40\text{ m}$): $-10.43\text{ N}\cdot\text{m}$; Club COM $G$ ($s = +0.72\text{ m}$): $-0.53\text{ N}\cdot\text{m}$; Clubhead center ($s = +1.02\text{ m}$): **$+8.76\text{ N}\cdot\text{m}$ (simulated sign flip at $s^* = +0.737\text{ m}$)**.
- **Illustrative Analytical Tour Driver Impact State ($C_{\alpha,M} = -16.0\text{ N}\cdot\text{m}$, $R_y = -75.0\text{ N}$ levering COM forward by $+54.0\text{ N}\cdot\text{m}$):**
  - Reported moment is **$-19.75\text{ N}\cdot\text{m}$** at the butt end, **$-16.00\text{ N}\cdot\text{m}$** at mid-hands, flips sign at **$s^* = +0.213\text{ m}$ (illustrative, just below the grip collar)**, and equals **$+38.00\text{ N}\cdot\text{m}$** at the club COM $G$ ($s = +0.72\text{ m}$).

### Study 2: Hand Couple vs. Sum of Moments Decomposition (`study_2_couple_vs_sum_of_moments`)
Tracks the exact decomposition $M_{\alpha,G}(t) = C_{\alpha,M}(t) - d_{G/M} R_y(t)$ across the simulated WSCG downswing:
- Early downswing ($t = 0.050\text{ s}$): $C_{\alpha,M} = +56.82\text{ N}\cdot\text{m}$ ($+34.88\text{ N}\cdot\text{m}$ force couple $+ 21.93\text{ N}\cdot\text{m}$ free wrist torque).
- Mid-downswing ($t = 0.140\text{ s}$): $C_{\alpha,M} = +36.69\text{ N}\cdot\text{m}$.
- Zero crossing of hand couple $C_{\alpha,M}$: **$t = 0.18017\text{ s}$** ($13.1\text{ ms}$ before peak clubhead speed at $t = 0.1933\text{ s}$).
- Peak clubhead speed ($t = 0.1933\text{ s}$, $115.08\text{ mph}$, simulated): $C_{\alpha,M} = -14.08\text{ N}\cdot\text{m}$ (while simulated ZTCF zero-torque passive couple is $-11.19\text{ N}\cdot\text{m}$, or $79.51\%$).
- Minimum hand couple ($t = 0.2151\text{ s}$, simulated): $C_{\alpha,M} = -22.8148\text{ N}\cdot\text{m}$ (while the **ZTCF** branch on the **same** trajectory is $-19.6294\text{ N}\cdot\text{m}$, giving **$86.04\%$** as the **magnitude ratio** $|C_{\alpha,\text{ZTCF}}|/|C_{\alpha,\text{BASE}}|$ — a **pointwise modeled diagnostic**, not a measured physiological muscle-energy share).

### Study 3: Coordinate Frame & Axis Convention Sensitivity (`study_3_frame_conventions`)
For an **illustrative** late-downswing couple $\mathbf{M}_{\text{FSP}} = (M_{\text{shaft}} = +4.5, M_{\text{out}} = +8.0, M_{\text{in}} = -15.0)\text{ N}\cdot\text{m}$:
- **Tutelman ("in, out, about"):** $(\alpha, \beta, \gamma) = (-15.0, +8.0, +4.5)\text{ N}\cdot\text{m}$.
- **MacKenzie / Golf Biomechanists:** $(\alpha, \beta, \gamma) = (-15.0, +4.5, +8.0)\text{ N}\cdot\text{m}$.
- **Club-Fixed Principal Frame across Face Roll $\phi_{\text{roll}}$:** Because the club-fixed $\alpha$ and $\beta$ axes rotate with the clubface about the shaft axis, $M_{\alpha,\text{club}}(\phi) = M_{\text{in}}\cos\phi + M_{\text{out}}\sin\phi$ is $-15.0\text{ N}\cdot\text{m}$ at $\phi = 0^\circ$, $-4.95\text{ N}\cdot\text{m}$ at $\phi = 45^\circ$, crosses zero at the **illustrative** angle $\phi^* = \arctan(15/8) = 61.93^\circ$, and flips **positive** ($+8.0\text{ N}\cdot\text{m}$ at $\phi = 90^\circ$, $+14.43\text{ N}\cdot\text{m}$ at $\phi = 120^\circ$) while the Euclidean norm $\|\mathbf{M}\| = 17.586\text{ N}\cdot\text{m}$ remains strictly invariant.

### Study 4: Butterworth Filter Cutoff, Collision Bleed & Aerodynamic Drag (`study_4_filtering_and_drag_sensitivity`)
- **Low-Cutoff Over-Smoothing Flip ($f_c = 8\text{ Hz}$):** When a realistic downswing couple (broad $+42\text{ N}\cdot\text{m}$ mid-downswing lobe followed by a sharp negative reversal crossing zero at $t = -17.2\text{ ms}$ to $-17.62\text{ N}\cdot\text{m}$ at impact) is double-differentiated from angles low-pass filtered at $f_c = 8\text{ Hz}$, the filter attenuates the $\sim 20\text{ Hz}$ pre-impact reversal and smears the mid-downswing positive peak into impact, flipping the inferred impact couple from **$-17.62\text{ N}\cdot\text{m}$ (negative)** to **$+0.26\text{ N}\cdot\text{m}$ at $t = 0$ and $+1.39\text{ N}\cdot\text{m}$ at $t = -5\text{ ms}$ (positive)**.
- **Collision Bleed Across Impact ($f_c = 20\text{--}50\text{ Hz}$):** Filtering across the ball-contact velocity discontinuity ($\Delta \omega = -7.8\text{ rad/s}$) with a zero-lag filter (`filtfilt`) leaks post-impact collision deceleration backward into the pre-impact window, inflating the inferred couple at $t = 0$ from $-15.18\text{ N}\cdot\text{m}$ (clean $30\text{ Hz}$) to **$-37.96\text{ N}\cdot\text{m}$** (across-impact $30\text{ Hz}$) and from $-15.91\text{ N}\cdot\text{m}$ to **$-34.69\text{ N}\cdot\text{m}$** at $5\text{ ms}$ before impact.
- **Aerodynamic Drag Bias:** Neglecting $9.0\text{--}10.0\text{ N}$ of driver head aerodynamic drag at $115\text{ mph}$ ($r_{\text{drag}} \approx 1.02\text{ m}$ from mid-hands) attributes an external aerodynamic retarding moment of **$-9.18\text{ to }-10.20\text{ N}\cdot\text{m}$** to the golfer's hands.

### Study 5: Bilateral Wrench Identifiability & Closed-Loop Drift (`study_5_closed_loop_and_identifiability`)
- **Bilateral Point-Force Map ($\mathbf{A}_F \in \mathbb{R}^{6\times 6}$):** $\operatorname{rank}(\mathbf{A}_F) = 5$, $\operatorname{nullity}(\mathbf{A}_F) = 1$ (internal axial tension/compression mode along the grip vector $\hat{\mathbf{d}}$).
- **Full Bilateral Hand-Wrench Map ($\mathbf{A}_W \in \mathbb{R}^{6\times 12}$):** $\operatorname{rank}(\mathbf{A}_W) = 6$, $\operatorname{nullity}(\mathbf{A}_W) = 6$ (club-only inverse dynamics cannot separate left-hand vs. right-hand forces or free wrist torques without an instrumented split grip).
- **Two-Arm Closed-Loop KKT Attribution:** At the tested late-downswing state, $M_{\text{total}} = -2.366\text{ N}\cdot\text{m}$ decomposes exactly into $M_{\text{drift}} = -0.929\text{ N}\cdot\text{m}$ (zero-torque motion-dependent constraint reaction) plus $M_{\text{control}} = -1.437\text{ N}\cdot\text{m}$ (residual $0.0\text{ N}\cdot\text{m}$). Setting grip separation $a_R = a_L = 0$ yields $M_{F,\text{zero-arm}} \equiv 0.0\text{ N}\cdot\text{m}$ identically.

### Study 6: Matched Flexible vs. Rigid Shaft Rebound (`study_6_shaft_flex_contribution`)
- **UpstreamDrift Matched 3-Link Model ($t = 0.4275\text{ s}$):** Reduced planar model (`FlexibleShaftParams.reference`) with gravity and shoulder/wrist damping. Lead shaft deflection $\approx -3.58^\circ$, shaft elastic moment $\approx +5.00\text{ N}\cdot\text{m}$, interface resultant $\|\mathbf{F}\| \approx 56.37\text{ N}$ with $(F_x,F_y) \approx (8.73,55.69)\text{ N}$. JSON exports **summed distal** generalized-acceleration contributions for **flexible** and **rigid** rollouts (control, momentum, gravity, joint damping, shaft elastic, shaft damping); each list sums to **total**.
- **Hypothetical Two-Hand Beam Row (not from Table 7.10):** Assumed $11^\circ$, $465\text{ N}$, and $+10\text{ N}\cdot\text{m}$ illustrate scalar $-sF$ bookkeeping only—**uncited** as a beam derivation in `alpha_war_calculations.json` (`inputs_are_uncited`: true). Do not merge with the matched rollout interface force (#5463).

## Running the Suite & Tests

```bash
# 1. Clone UpstreamDrift at the pinned commit (see upstream_drift.lock.json)
git clone https://github.com/D-sorganization/UpstreamDrift.git /tmp/UpstreamDrift
cd /tmp/UpstreamDrift && git checkout "$(jq -r .commit /path/to/AffineDrift/research/alpha-war/calcs/upstream_drift.lock.json)"

# 2. Regenerate JSON + run tests (fails closed if pin or hashes mismatch; sets
#    ``ALPHA_WAR_INTEGRATION_REQUIRED=1`` so UpstreamDrift integration tests cannot skip)
export ALPHA_WAR_UPSTREAM_DRIFT_ROOT=/tmp/UpstreamDrift
bash research/alpha-war/calcs/regenerate_calculations.sh

# Golden/manifest guards (no UpstreamDrift required)
python3 -m unittest research.alpha-war.calcs.test_alpha_war_reproducibility -v
```

If `ALPHA_WAR_UPSTREAM_DRIFT_ROOT` is unset, `test_alpha_war_sensitivity_suite.py` skips rather than treating missing UpstreamDrift as a pass.
