# Independent Verification (Argon): Slack Take-Up as a Witness (#5136)

**Proposal:** `articles/slack-takeup-identifiability.qmd` ([AffineDrift#5136](https://github.com/D-sorganization/AffineDrift/issues/5136))  
**Verdict:** **Holds with caveats** (the proposal's skeptical framing is mathematically validated: while engagement order identifies the pull end in a 1-D unpreloaded serial train, in a closed two-hand loop each slack element introduces unmeasured nuisance parameters—gap $\delta_i$ and initial preload $x_i(0)$—that make the event-time map underdetermined without prior calibration, allowing preload to invert take-up order completely).  
**Executable verification:** `docs/development/technical-review/verify_slack_preload_proposals.py`

## 1. Independent Model & Rank/Sensitivity Derivation

We built three independent minimal models matching Toys A, B, and C to test the counting argument $\operatorname{rank}(E_{\text{ev}} N_{\text{aug}}) - p_{\text{added}}$:

### A. Toy A (1-D Serial Train) vs. Toy B (2-Hand Closed Loop)
In a 1-D 3-car serial train starting at rest with zero initial offset ($d_{12}(0)=d_{23}(0)=0$) and gaps $\delta_{12}, \delta_{23} > 0$, applying force $+F$ to Car 1 engages coupler 1–2 at $t_{12} = \sqrt{2 m_1 \delta_{12}/F}$ and coupler 2–3 strictly later ($t_{23} > t_{12}$), identifying the pulling end.

In the two-hand closed loop on a rigid club, let net club demand be $\tau_{\text{net}} = \tau_1^* + \tau_2^*$ and internal nullspace torque be $s = \tfrac{1}{2}(\tau_2^* - \tau_1^*)$, so $\tau_1^* = \tfrac{1}{2}\tau_{\text{net}} - s$ and $\tau_2^* = \tfrac{1}{2}\tau_{\text{net}} + s$. Under first-order slack take-up $T_i\dot{x}_i = x_i^* - x_i$ toward $+\delta_i$, the engagement time of channel $i \in \{1,2\}$ is:
$$
t_i(s, d_{\text{eff},i}) = T_i \ln\!\left(1 + \frac{k_i\, d_{\text{eff},i}}{\tfrac{1}{2}\tau_{\text{net}} \mp s}\right), \qquad d_{\text{eff},i} \equiv \delta_i - x_i(0).
$$
- **Exact Dimension Count:** Observing two engagement times $(t_1, t_2)$ adds $m_{\text{ev}} = 2$ scalar observations, but introduces at least $p_{\text{added}} = 2$ unmeasured nuisance states $(d_{\text{eff},1}, d_{\text{eff},2})$ (plus $k_i, T_i$ if uncalibrated). The $2\times 3$ augmented Jacobian $J_{\text{aug}} = \bigl[\frac{\partial \mathbf{t}}{\partial s} \;\big|\; \frac{\partial \mathbf{t}}{\partial \mathbf{d}_{\text{eff}}}\bigr]$ has $\operatorname{rank}(J_{\text{aug}}) = 2 < 3$, leaving an **exact 1-D unobservable null direction**.
- **Sensitivity Ratio ($417\times$ in natural units, collapses SNR under uncertainty):** At $\tau_{\text{net}}=10\text{ N m}$, $s=0$ ($\tau_1^*=\tau_2^*=5\text{ N m}$), $k=600\text{ N m rad}^{-1}$, $\delta=0.012\text{ rad}$, $T=18\text{ ms}$:
  $$
  \frac{\partial t_i}{\partial s} = \pm 2.125\text{ ms}/(\text{N m}), \qquad \frac{\partial t_i}{\partial d_{\text{eff},i}} = 0.885\text{ ms}/\text{mrad}.
  $$
  The null vector is $[\Delta s, \Delta d_{\text{eff},1}, \Delta d_{\text{eff},2}]^\top = [1\text{ N m},\, -2.4\text{ mrad},\, +2.4\text{ mrad}]^\top$: a mere **$2.4\text{ mrad}$ ($0.14^\circ$) shift in initial preload/gap** mimics a $1\text{ N m}$ shift in internal torque.
- **Marginalized Singular Value Test:** With prior $\sigma_s = 2.5\text{ N m}$, preload uncertainty $\sigma_d = 8\text{ mrad}$, and the repository's $5\text{ ms}$ censoring resolution ($\sigma_t = 5\text{ ms}$), the scaled singular value of the observation map for $s$ drops to **`0.866 < 1.0`**, failing the NSX observability threshold ($\sigma_{\min}(\operatorname{diag}(1/\sigma)E_x N) \ge 1$).
- **Exact Preload-Reversal Counterexample (H10):** With zero preload ($x_{10}=x_{20}=0$), a trail-dominant internal torque $s = +2\text{ N m}$ ($\tau_1^*=3, \tau_2^*=7\text{ N m}$) gives $(t_1, t_2) = (22.03\text{ ms}, 12.73\text{ ms})$ (Hand 2 engages first). A lead-dominant internal torque $s = -2\text{ N m}$ ($\tau_1^*=7, \tau_2^*=3\text{ N m}$) with initial preloads $x_1(0) = -16.0\text{ mrad}, x_2(0) = +6.857\text{ mrad}$ produces the **exact same engagement times** $(22.03\text{ ms}, 12.73\text{ ms})$ to machine precision ($0.0\text{ s}$ error), completely inverting the inferred source hand!

### B. Toy C: Spatial 6-D Grasp Kernel Observability (Correction to Proposal Section "Plan" #3)
For hand offsets $\mp d = (\mp\delta, 0, 0)$ along the shaft axis ($\delta=0.06\text{ m}$), the $12\times 6$ grasp kernel $K$ maps $s = (s_1,\dots,s_6)^\top$ to $y = (f_L, c_L, f_R, c_R)^\top$:
$$
f_L = -s_{1:3},\quad c_L = -[d]_\times s_{1:3} - s_{4:6},\quad f_R = +s_{1:3},\quad c_R = -[d]_\times s_{1:3} + s_{4:6}.
$$
- **Important correction to Toy C expectation:** The proposal states: *"Expected result to test: twist and bending couples, not axial squeeze."* What about transverse shear forces $s_2, s_3$? Because $[d]_\times s_{1:3} = (0, -\delta s_3, +\delta s_2)^\top$, **wrist rotational slack channels ($E_{\text{rot}}$ observing $c_L, c_R$) have rank 5 on $K$, not rank 3!** They observe $s_4, s_5, s_6$ with gain $\sqrt{2} = 1.4142$ AND couple into transverse forces $s_2, s_3$ with lever-arm gain $\sqrt{2}\delta = 0.0849\text{ m}$ (badly conditioned by $1/\delta \approx 16.7\times$), while axial squeeze $s_1$ has exact norm `0.0000` ($\hat{u}\times\hat{u}=0$). Similarly, grip normal/transverse contact openings ($E_{\text{no-axial}}$) have rank $5$ and are blind to $s_1$.

## 2. Verifiable References for Core Physics Points

- **Train coupler slack action & run-in/run-out dynamics:** Garg & Dukkipati (1984), *Dynamics of Railway Vehicle Systems*, Academic Press, ISBN `978-0-12-275950-5`; Cole (2006), "Longitudinal Train Dynamics," Ch. 9 in Iwnicki (Ed.), *Handbook of Railway Vehicle Dynamics*, CRC Press, DOI `10.1201/9781420004892`.
- **Grasp matrix, internal wrench kernel $\ker G$ & closed chains:** Murray, Li, & Sastry (1994), *A Mathematical Introduction to Robotic Manipulation*, CRC Press (`@murray1994mathematical`); Lynch & Park (2017), *Modern Robotics*, Cambridge Univ. Press (`@lynch2017modern`); Featherstone (2008), *Rigid Body Dynamics Algorithms*, Springer, DOI `10.1007/978-1-4899-7560-7` (`@featherstone2008rigid`).
- **Hybrid-system observability, saltation matrices & event sensitivity:** Goebel, Sanfelice, & Teel (2012), *Hybrid Dynamical Systems*, Princeton Univ. Press (`@goebel2012hybrid`); Kong, Payne, Zhu, & Johnson (2024), *Proc. IEEE* 112(6):585–608, DOI `10.1109/JPROC.2024.3440211` (`@kong2024saltation`); Burden, Revzen, & Sastry (2015), *IEEE Trans. Autom. Control* 60(10):2626–2639, DOI `10.1109/TAC.2015.2411971` (`@Burden2015`); Vidal, Chiuso, Soatto, & Sastry (2003), "Observability of Linear Hybrid Systems," *HSCC 2003*, LNCS 2623, pp. 526–539, DOI `10.1007/3-540-36580-X_38`.
