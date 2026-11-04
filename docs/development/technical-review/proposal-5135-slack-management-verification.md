# Independent Verification (Argon): Managing Slack in Linked Systems (#5135)

**Proposal:** `articles/slack-management-linked-systems.qmd` ([AffineDrift#5135](https://github.com/D-sorganization/AffineDrift/issues/5135))  
**Verdict:** **Holds with caveats** (the mathematical taxonomy separating memoryless deadzone, hysteretic play, smooth stiffening springs, unilateral complementarity, and Hill series-elastic dynamics is sound and the single-channel non-identifiability result reproduces; however, the proposed "decision rule" requires explicit counterexamples showing when zero-dead-zone equivalence fails and why local sensitivity rank does not imply class identifiability).  
**Executable verification:** `docs/development/technical-review/verify_slack_preload_proposals.py`

## 1. Independent Model & Numerical Verification

We independently checked the mathematical properties of the slack representation ladder, the closure-nullity sequence, and the constitutive-audit metrics cited in the proposal:

1. **Play operator (memory) vs. deadzone (memoryless):**
   - For the kinematic play operator $y_n = \operatorname{clip}(y_{n-1}, r_n - \Delta, r_n + \Delta)$ with $\Delta = 0.01\text{ rad}$, cycling input $r: 0 \to +0.015 \to 0$ leaves retained output $y = +0.005\text{ rad}$, whereas cycling $0 \to -0.015 \to 0$ leaves $y = -0.005\text{ rad}$ (hysteresis separation $0.010\text{ rad}$ at the identical current input $r=0$). A memoryless deadzone $d(r) = \operatorname{sgn}(r)\max(|r|-\Delta,0)$ evaluates to $0$ in both cases.
   - **Important audit finding on `typed_slack_dynamic_study.json`:** As documented in its `limitations` array, the `transmission_backlash` class in the repository's scalar constitutive study actually uses a **memoryless dead-zone-plus-damping surrogate**, not a stateful rate-independent Prandtl–Ishlinskii play operator. The article must state this distinction explicitly so readers do not conflate the taxonomy's play operator with the archived surrogate trace.
2. **Closure-model nullity progression:**
   - Using Proposition 1 of `loop_nullspace.tex` ($\text{nullity}(A) = m + n_g - r_u$ with $r_u = \operatorname{rank} J_{c,u}^\top$), we verified the spatial fixed-base ($n_a=14, n_g=0$) closure sequence:
     - `WELD` ($m=6, n_u=0 \implies r_u=0$): allocation nullity $= 6$, admitted velocity dim $= 14 - 6 = 8$.
     - `SHAFT_TWIST_REVOLUTE` ($m=5, n_u=0 \implies r_u=0$): allocation nullity $= 5$, admitted velocity dim $= 9$.
     - `TRAIL_BALL` ($m=3, n_u=0 \implies r_u=0$): allocation nullity $= 3$, admitted velocity dim $= 11$.
     - `LEAD_BALL` ($m=6$, adds $n_u=3$ unactuated ball coordinates with $r_u = \operatorname{rank} J_{c,u}^\top = 3$): allocation nullity $= 6 - 3 = 3$, admitted velocity dim $= 17 - 6 = 11$.
3. **Single-channel non-separability & passivity residuals:**
   - In the five-class constitutive audit (`typed_slack_dynamic_study.json`), all four mechanical classes (`contact_disengagement`, `transmission_backlash`, `structural_preload`, `biological_series_compliance`) close their work-energy ledgers to $\le 5.12\times 10^{-10}\text{ J}$, while `control_deadband` is a signal map where mechanical passivity does not apply.
   - Under multisine reversal excitation, every 3-parameter local sensitivity matrix has full rank $3$ (condition numbers $14.2$ to $64.5$), yet `contact_disengagement` and `biological_series_compliance` differ by only **1.957% normalized output RMSE** (`0.019574`).

## 2. Over-Claims, Missing Counter-Examples & Analogy Breaks

- **Missing counterexample 1 — Zero dead zone does NOT guarantee allocation-independent net torque when channel time constants differ:** In the 12-cell grid ($\delta \in \{0, 0.004, 0.012, 0.024\}\text{ rad}$, $T \in \{8, 18, 35\}\text{ ms}$), persistent and role-reversal programs are equivalent at $\delta=0$ (within $2.78\times 10^{-16}\text{ N m s}$) **only because $T_{\text{arm}} = T_{\text{wrist}}$**. When $\delta=0$ but $T_{\text{arm}} = 18\text{ ms}$ and $T_{\text{wrist}} = 36\text{ ms}$, the net torque difference between persistent $(10,-4)\to(16,-6)$ and reversal $(-4,10)\to(16,-6)$ is $\Delta\tau_{\Sigma}(t) = 14\bigl(e^{-t/T_{\text{arm}}} - e^{-t/T_{\text{wrist}}}\bigr)\text{ N m}$, which reaches **$-3.50\text{ N m}$** at $t = 24.95\text{ ms}$ (35% of the $10\text{ N m}$ target) with ZERO dead zone.
- **Missing counterexample 2 — Within-class rank vs. between-class identifiability:** Full rank ($3$) of $\partial y / \partial \theta_c$ within class $c$ only ensures local parameter identifiability *given* the true model structure $c$; it provides zero guarantee that class $c_1$ can be distinguished from class $c_2$ from a single output channel.
- **Missing counterexample 3 — Distributed grip zero-transition artifact:** In `articulated_distributed_grip_atlas.json` ($288$ trajectories, $1, 3, 5$ stations/hand), `maximum_transition_count = 0` because the transition counter tracks *any-station-active vs. all-stations-open* rather than individual station openings, and no friction is modeled.

## 3. Verifiable References for Core Physics Points

- **Backlash & deadzone adaptive control / play operators:** Tao & Kokotović (1995), *Automatica* 31(2):263–277, DOI `10.1016/0005-1098(94)00098-3`; Nordin & Gutman (2002), *Automatica* 38(10):1633–1649, DOI `10.1016/S0005-1098(02)00087-0`; Brokate & Sprekels (1996), *Hysteresis and Phase Transitions*, Springer, DOI `10.1007/978-1-4612-4048-8`.
- **Series elastic actuators (SEA) & compliant actuation:** Pratt & Williamson (1995), *Proc. IEEE/RSJ IROS*, Vol. 1, pp. 399–406, DOI `10.1109/IROS.1995.525827`.
- **Unilateral contact & complementarity dynamics:** Brogliato (2016), *Nonsmooth Mechanics: Models, Dynamics and Control* (3rd ed.), Springer, DOI `10.1007/978-3-319-28664-8`; Glocker & Pfeiffer (1995), *Nonlinear Dyn.* 7(4):471–497, DOI `10.1007/BF00121109` (`@Glocker1995`).
- **Compliant contact & restitution:** Carvalho & Martins (2019), *Mech. Mach. Theory* 139:174–194, DOI `10.1016/j.mechmachtheory.2019.03.028` (`@carvalho2019restitution`); Brown & McPhee (2018), *Proceedings* 2(6):239, DOI `10.3390/proceedings2060239` (`@brown2018grip`).
- **Structural & practical identifiability:** Raue et al. (2009), *Bioinformatics* 25(15):1923–1929, DOI `10.1093/bioinformatics/btp358` (`@raue2009identifiability`); Co-contraction cost & impedance: Hogan (1985), DOI `10.1115/1.3140702` (`@hogan1985impedance`); Li et al. (2021), DOI `10.3389/fbioe.2020.588908` (`@li2021cocontraction`).
