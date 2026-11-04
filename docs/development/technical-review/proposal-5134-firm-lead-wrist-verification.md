# Independent Verification (Argon): The Firm Lead Wrist as Preload (#5134)

**Proposal:** `articles/firm-lead-wrist-preload.qmd` ([AffineDrift#5134](https://github.com/D-sorganization/AffineDrift/issues/5134))  
**Verdict:** **Holds with caveats** (the mathematical and numerical claims reproduce exactly, but the preload advantage is strictly conditional on a literal gap/dead-zone constitutive law and collapses by two orders of magnitude—or reverses sign—under smooth Hill-type activation and series-force dynamics).  
**Executable verification:** `docs/development/technical-review/verify_slack_preload_proposals.py`

## 1. Independent Model & Numerical Reproduction

From first principles, we independently derived and integrated both the two-channel rotational dead-zone transmission model and the four-muscle Hill activation + series-elastic bridge over the $180\text{ ms}$ preparation ($6\text{ N m}$ net) and $120\text{ ms}$ delivery ($10\text{ N m}$ net) windows:

| Model / Condition | Persistent $(10,-4)\to(16,-6)\text{ N m}$ | Role Reversal $(-4,10)\to(16,-6)\text{ N m}$ | Difference ($\text{Rev}-\text{Pers}$) | Relative Effect |
|---|---:|---:|---:|---:|
| **Dead-zone ($0.1\text{ ms}$ Euler, finite prep)** | `0.0717150568 N m s` ($0\text{ ms}$ gaps) | `0.1954089217 N m s` ($11.5\text{ ms}$ arm, $22.0\text{ ms}$ wrist) | `+0.1236938649 N m s` | **+172.5%** (+63.3% of rev) |
| **Dead-zone (exact closed-form ODE, eq. init)** | `0.0719083704 N m s` ($0\text{ ms}$ gaps) | `0.1959506834 N m s` ($11.553\text{ ms}$ arm, $22.028\text{ ms}$ wrist) | `+0.1240423131 N m s` | **+172.5%** |
| **Dead-zone (relaxed start $x_i(0)=0$)** | `0.2010713807 N m s` ($6.7, 14.2\text{ ms}$ gaps) | `0.2010713807 N m s` ($6.7, 14.2\text{ ms}$ gaps) | `0.0000000000 N m s` | **0.0%** |
| **Hill muscle bridge ($0.2\text{ ms}$ Euler, published)** | `0.0899832911 N m s` | `0.0908399207 N m s` | `+0.0008566297 N m s` | **+0.943%** |
| **Hill muscle bridge (RK4 limit $\Delta t\to 0$)** | `0.0920259396 N m s` | `0.0924270292 N m s` | `+0.0004010896 N m s` | **+0.434%** |

### How Large the Effect Really Is (and Why It Collapses)
1. **Dead-zone closed-form verification:** Under $T\dot{x}_i = x_i^* - x_i$ ($k=600\text{ N m rad}^{-1}$, $\delta=0.012\text{ rad}$, $T=18\text{ ms}$), persistent loading stays outside $|x_i|\le\delta$, reducing to linear first-order lag $J_{\text{pers}} = 4T(1 - e^{-0.12/T}) = 0.071908\text{ N m s}$ (`0.071715 N m s` under $0.1\text{ ms}$ forward Euler). Role reversal traverses $[-\delta, +\delta]$ with exact analytical dwell $\Delta t_i = T\ln\bigl((|\tau_{i,\text{post}}^*| + k\delta)/(|\tau_{i,\text{post}}^*| - k\delta)\bigr)$ when starting from equilibrium, yielding $11.553\text{ ms}$ (arm) and $22.028\text{ ms}$ (wrist)—matching the $0.1\text{ ms}$ sample counts ($11.5\text{ ms}$, $22.0\text{ ms}$) and `0.1954089 N m s`.
2. **Muscle-bridge cancellation:** In the Hill/activation/series-force bridge ($\tau_{\text{act}}=10\text{ ms}$, $\tau_{\text{deact}}=40\text{ ms}$, $T_{\text{tendon}}=12\text{ ms}$), individual channel tracking errors are **6.3× larger** under role reversal ($J_{\text{arm}}+J_{\text{wrist}} = 1.1586\text{ N m s}$ vs. $0.1848\text{ N m s}$). However, because activation is $4\times$ faster than deactivation ($\tau_{\text{act}} < \tau_{\text{deact}}$), the newly activating arm flexors (+16 N m) rise much faster than the deactivating wrist flexors (+10 N m $\to 0$) decay. Their sum $\tau_{\Sigma}(t)$ rises *faster* initially under role reversal ($8.86\text{ N m}$ vs. $7.53\text{ N m}$ at $t=15\text{ ms}$) and then *overshoots* the $10\text{ N m}$ target (peaking at $10.80\text{ N m}$ at $t=46\text{ ms}$). The early deficit and late overshoot nearly cancel in $J = \int_0^{0.12}|\tau_{\Sigma}^* - \tau_{\Sigma}|\,dt$, leaving only `0.000857 N m s` (0.94%) at $\Delta t=0.2\text{ ms}$ and `0.000401 N m s` (0.43%) in the continuous limit ($\Delta t\to 0$).
3. **Counterexample where role reversal beats persistent direction:** Because of the activation/deactivation asymmetry overshoot, if the post-transition arm target is increased from $(16,-6)$ to $(20,-6)\text{ N m}$ (net target $14\text{ N m}$), role reversal yields $J_{\text{rev}} = 0.1505\text{ N m s}$ vs. $J_{\text{pers}} = 0.1918\text{ N m s}$ ($\Delta J = -0.0413\text{ N m s}$)—reversing the sign of the advantage.

## 2. Over-Claims, Missing Counter-Examples, Unit/Sign Audits & Analogy Breaks

- **Unit & metric semantics (`N m s`):** $J = \int |\tau_{\Sigma}^* - \tau_{\Sigma}|\,dt$ has units of $\text{N m s}$, but it is **integrated L1 tracking error**, neither signed angular impulse ($\int (\tau_{\Sigma}^* - \tau_{\Sigma})\,dt$, which is $+0.0920\text{ N m s}$ for persistent vs. $-0.0032\text{ N m s}$ for reversal in the muscle model!) nor mechanical work ($\int \tau\,\dot{\theta}\,dt$).
- **Author citation error in `ch06bc`:** `articles/proximal_distal_energy_transfer/chapters/_ch06bc_torque_allocation_preload.qmd` L38 cites `[@jobe1995]`, whereas the first author is **Kao** (`@kao1995`: Kao, Pink, Jobe, & Perry, 1995). The draft must use `@kao1995`.
- **Analogy break (gearbox backlash vs. antagonistic wrist):** A passive mechanical gear has one tooth gap per mesh. A biological joint spanned by agonist and antagonist muscles can maintain zero net torque ($\tau_{\text{net}}=0$) while both tendons are taut under high co-contraction ($f_+ = f_- > 0$), yielding high short-range tangent stiffness with **zero dead zone**.

## 3. Verifiable References for Core Physics Points

- **Bilateral grip wrench & upper-limb kinetics:** Koike (2016), *Proc. 34th Int. Conf. Biomech. Sports* (`@koike2016instrumented`); Choi & Park (2020), *Sensors* 20(13):3672, DOI `10.3390/s20133672` (`@koike2020`).
- **Scapular & wrist EMG in golf:** Kao et al. (1995), *Am. J. Sports Med.* 23(1):19–23, DOI `10.1177/036354659502300104` (`@kao1995`); Robinson et al. (2023), *J. Sports Sci.* 41(17):1596–1604, DOI `10.1080/02640414.2023.2285121` (`@robinson2023`).
- **Muscle activation/deactivation asymmetry & series compliance:** Zajac (1989), *CRC Crit. Rev. Biomed. Eng.* 17(4):359–411; Thelen (2003), *J. Biomech. Eng.* 125(1):70–77, DOI `10.1115/1.1531112` (`@thelen2003adjustment`).
- **Short-range stiffness & impedance:** Hu, Murray, & Perreault (2011), *J. Neurophysiol.* 105(4):1633–1641, DOI `10.1152/jn.00537.2010` (`@hu2011ShortRange`); Hogan (1985), *J. Dyn. Syst. Meas. Control* 107(1):1–7, DOI `10.1115/1.3140702` (`@hogan1985impedance`).
- **Impact duration, shaft wave transit & feel acoustics:** Roberts, Jones, & Rothberg (2001), *Sports Eng.* 4(4):191–203, DOI `10.1046/j.1460-2687.2001.00084.x` (`@roberts2001contacttime`); Roberts et al. (2005), *J. Sound Vib.* 287(4–5):651–666, DOI `10.1016/j.jsv.2004.11.026` (`@roberts2005sound`); Corke et al. (2018), *Appl. Sci.* 8(3):422, DOI `10.3390/app8030422` (`@corke2018gripping`).
