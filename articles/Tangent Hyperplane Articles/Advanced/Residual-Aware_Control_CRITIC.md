# Critic's Corner: Residual-Aware Control

## Introduction

This critique examines "Residual-Aware Control: Exploiting Geometric Curvature" through the lens of scientific rigor, mathematical completeness, and empirical validation. The article presents an ambitious framework for using residuals as control signals rather than mere approximation errors. While the core intuition is compelling, several technical claims require strengthening, assumptions need explicit statement, and experimental validation needs deeper scrutiny.

This critique is structured to identify **actionable weaknesses** that could be exploited by hostile reviewers, with suggested remedies for each issue.

---

## Critique 1: Theorem 1.1 Proof Incompleteness

### Summary of Concern

The proof of Theorem 1.1 (Quantitative Residual Bound) makes several unstated assumptions and omits critical steps in the derivation, particularly in the transition from continuous-time analysis to the discrete-time bound used in practice.

### Location

- **Section:** 1.1.2 Hessian-Based Residual Bounds
- **Theorem:** 1.1 (Equation 2.3)
- **Proof:** Lines 85-129

### Nature of the Issue

**Logical gaps:**

1. **Step from eq. 2.7 to 2.9:** The proof claims $\|\delta u\| \leq K \|\delta x\|$ "for control-affine systems where δu is chosen via LQR," but this is only true for the *optimal* LQR controller, and only when the linearization is accurate. This is circular: we're bounding residuals assuming the controller works, but the controller's validity depends on small residuals.

2. **Integration argument:** The proof integrates $\|\dot{r}\| \leq C_M \|\delta x\|^2$ to get $\|r(t_1)\| \leq \int \|\dot{r}\| dt$, but $\delta x(t)$ itself depends on $r(t)$ through the coupling $\dot{\delta x} = A \delta x + \text{terms involving } r$. The proof treats $\delta x(t)$ as known, but it's part of the system state.

3. **Hessian bound uniformity:** The bound assumes $\|H_f\|_{\max} \leq M$ over the **entire trajectory**, but $M$ is computed at a single point in Example 1.1. How does $M$ vary along trajectories with large state excursions?

4. **Grönwall inequality application:** The appendix proof (Section A.1) invokes Grönwall's inequality but then makes an unjustified approximation $e^{\|A\|\Delta t} \approx 1 + \|A\|\Delta t$ "for bounded time intervals." This is only valid when $\|A\|\Delta t \ll 1$, which may not hold for stiff systems or aggressive maneuvers.

### Why This Is a Problem

A rigorous reviewer would immediately notice:

- **Circular reasoning:** The bound assumes the controller is working (δu small) to prove the bound is valid.
- **Non-constructive:** Without knowing δx(t) evolution, the bound cannot be computed a priori.
- **Missing conditions:** Under what conditions on A, M, K does the bound actually hold over finite horizons?

These gaps make the bound **qualitatively useful** (residuals scale as O(||δx||²)) but **quantitatively fragile** (constants are underspecified).

### Evidence / References

- **Grönwall's inequality:** Standard reference is [Khalil, "Nonlinear Systems" (2002), Lemma 3.4]. The lemma requires explicit bounds on the perturbation coupling, which are not provided here.

- **Perturbation analysis for LQR:** [Bian & Jiang (2019), "Robust stability of perturbed LQR"](https://doi.org/10.1016/j.automatica.2019.02.051) shows that LQR robustness to modeling errors requires explicit conditions on perturbation magnitude—conditions not stated here.

- **Residual bounds in DDP:** [Tassa et al. (2012), iLQG paper](https://homes.cs.washington.edu/~todorov/papers/TassaIROS12.pdf) uses quadratic residual approximations but does **not** claim rigorous bounds—they use backtracking line search to handle approximation errors empirically.

### Severity

**Medium-High**: The theorem is central to the adaptive timestep algorithm (2.1), so if the bound is unreliable, the entire adaptive framework loses its theoretical foundation.

### Suggested Remedies

1. **State assumptions explicitly:**
   - Add: "Assume ||δu|| = ||K δx|| where K is the LQR gain with ||K|| ≤ K_max."
   - Add: "Assume ||A(t)|| ≤ A_max uniformly along the trajectory."
   - Add: "Assume ||H_f(x,u)|| ≤ M for all (x,u) in a tube around the nominal trajectory."

2. **Revise the integration argument:**
   - Either: Solve the coupled δx-r system explicitly (harder), or
   - Use a **bootstrapping argument**: "For small initial perturbations ||δx(0)|| ≤ δ₀, the residual remains O(δ₀²) over time horizons satisfying..."

3. **Clarify Grönwall application:**
   - State the condition: "For DDP timesteps Δt satisfying ||A||Δt < 0.1, the exponential term is approximately 1 + O(||A||Δt)."
   - Add: "For stiff systems with large ||A||, either reduce Δt or use the exact exponential form."

4. **Provide worked example with trajectory-varying M:**
   - Extend Example 1.1 to show M(θ) as a function of angle, and compute worst-case M over a flip trajectory.

---

## Critique 2: Adaptive Timestep Convergence Claims

### Summary of Concern

Theorem 2.1 claims that "Adaptive DDP converges to a local minimum of the continuous-time cost functional" with discretization error O(εᵣ), but the proof is a hand-wave ("proof sketch") and the assumptions are vague ("standard DDP assumptions").

### Location

- **Section:** 2.1.3 Convergence Guarantees
- **Theorem:** 2.1 (after Eq. 2.5)

### Nature of the Issue

**Unjustified generalization:**

1. **What are "standard DDP assumptions"?** DDP convergence requires:
   - Controllability
   - Positive definite cost Hessians (Qᵤᵤ > 0)
   - Lipschitz continuous dynamics
   - Initial guess in basin of attraction

   But adaptive timesteps **change the discretization** at each iteration. Does convergence still hold when the grid itself is moving?

2. **Discretization error claim:** The theorem states "trajectory discretization error O(εᵣ)" but provides no proof. The standard result is that **fixed-timestep** methods with timestep Δt have error O(Δt²) for RK4. How does adaptive timestep affect this?

3. **No discussion of mesh refinement stability:** Changing the time grid between iterations could destabilize the optimization. Methods like ALTRO (Howell et al. 2019) use **fixed grids** for this reason.

### Why This Is a Problem

Without a rigorous convergence proof, the adaptive timestep method is **heuristic**, not principled. A reviewer could argue:

- "This is just an engineering trick with no guarantees."
- "You could get faster convergence by simply using a fine fixed grid."
- "Changing the discretization during optimization violates standard convergence proofs."

### Evidence / References

- **DDP convergence:** [Li & Todorov (2004)](https://homes.cs.washington.edu/~todorov/papers/LiICINCO04.pdf) proves local convergence for **fixed discretizations**. Their proof does not extend to adaptive grids.

- **Adaptive mesh refinement in optimization:** [Betts (2010), "Practical Methods for Optimal Control"](https://epubs.siam.org/doi/book/10.1137/1.9780898718577) discusses mesh refinement but emphasizes that it should be done **between solve attempts**, not during iteration.

- **Moving grids in ODE solvers:** [Hairer & Wanner (1996)](https://link.springer.com/book/10.1007/978-3-642-05221-7) analyze adaptive ODE integration, but their convergence results assume the **final grid is fixed**, not changing adaptively.

### Severity

**Medium**: The algorithm works empirically (as shown in applications), but the theoretical justification is weak. This invites skepticism about whether the approach is truly better than standard methods or just a re-parameterization.

### Suggested Remedies

1. **Downgrade claim to conjecture:**
   - Change "Theorem 2.1" to "Conjecture 2.1" or "Empirical Observation 2.1."
   - Or restrict to: "Under fixed timestep selection (computed once before optimization), convergence follows from standard DDP results."

2. **Provide empirical convergence analysis:**
   - Plot: Cost vs. iteration for adaptive DDP vs. fixed-step DDP.
   - Show that convergence is monotonic (or explain backtracking when grid changes).

3. **Add stabilization technique:**
   - Adapt grid only when cost improvement stalls (like mesh refinement in collocation methods).
   - Or: Use **frozen grid** for backward pass, update grid only in forward pass.

4. **Cite related work:**
   - Reference [GPOPS-II (Patterson & Rao 2014)](https://doi.org/10.1145/2558904) which uses adaptive mesh refinement in optimal control, and discuss how their approach differs.

---

## Critique 3: Hessian Bound Computation Accuracy

### Summary of Concern

The article uses two methods for computing Hessian bounds (analytical and autodiff), but neither is validated against ground truth, and the bounds may be overly conservative or incorrect for complex systems.

### Location

- **Section:** 1.1.3 Computing the Hessian Bound
- **Code:** Section 4.1, lines 1006-1013

### Nature of the Issue

**Unstated assumptions and potential errors:**

1. **Example 1.1 (pendulum):** The Hessian computation claims $\|H_f\|_{\max} = g/L$ based on the (0,0) element of the Hessian of $f_2(\theta, \dot\theta)$. But:
   - The Hessian is a 2×2 matrix (for 2D state). What about the (1,0), (0,1), (1,1) elements?
   - The norm should be computed as $\max_i \|H_{f_i}\|$ where $H_{f_i}$ is the Hessian of the i-th component of f.

2. **Autodiff method (lines 1006-1013):** The code computes `jax.hessian(lambda x: dynamics(x, u, params))`, which returns a tensor of shape (n, n, n). The code takes `vmap` over the first dimension and computes Frobenius norms. But:
   - Is Frobenius norm the right choice? The bound requires operator norm (spectral norm).
   - Why `vmap` over dimension 0 instead of taking the max over all elements?

3. **No numerical validation:** The article never checks whether the computed M actually bounds the true residuals in simulation.

### Why This Is a Problem

If the Hessian bound is wrong, then:

- **Adaptive timesteps could be too large** (M underestimated) → residuals exceed εᵣ → linearization errors grow → optimization fails.
- **Or too small** (M overestimated) → excessive computation for no benefit.

A rigorous paper would include:
- Numerical experiment: Compute predicted residual bound vs. observed residual.
- Comparison: Analytical M vs. autodiff M vs. Monte Carlo sampling of H over trajectories.

### Evidence / References

- **Hessian norms for control:** [Ames et al. (2014), "Control barrier functions"](https://doi.org/10.1109/TAC.2014.2330732) use Hessian bounds for Lyapunov analysis and emphasize the importance of **tight bounds** for practical performance.

- **Norm choices:** [Golub & Van Loan (2013), "Matrix Computations"](https://jhupbooks.press.jhu.edu/title/matrix-computations) discuss operator norms vs. Frobenius norms: for bounding solutions to differential equations, the **2-norm (spectral norm)** is standard, not Frobenius.

### Severity

**Medium**: The Hessian bound is used throughout the algorithms, so errors propagate. However, practical robustness (clipping Δt to [0.001, 0.1]) mitigates catastrophic failures.

### Suggested Remedies

1. **Correct the pendulum example:**
   - Show the full Hessian matrix for both f₁ and f₂.
   - Compute the spectral norm, not just the max element.

2. **Fix the autodiff code:**
   - Use `jnp.linalg.norm(H_i, ord=2)` instead of Frobenius norm.
   - Clarify: "We compute the maximum spectral norm over state dimensions."

3. **Add numerical validation section:**
   - Title: "4.2 Validation of Hessian Bounds"
   - Content:
     - Simulate pendulum/quadrotor with known perturbations.
     - Plot predicted ||r|| from Theorem 1.1 vs. actual ||r|| from simulation.
     - Show that M is indeed an upper bound (or adjust M if not).

4. **Discuss conservatism:**
   - Add: "In practice, M computed over the full state space is conservative. For computational efficiency, we recommend computing M locally over a tube around the nominal trajectory."

---

## Critique 4: Experimental Validation Sufficiency

### Summary of Concern

The application examples (quadrotor, humanoid, golf) present **simulated results** with suspiciously round numbers (e.g., "40% fewer nodes," "4× speedup") but no error bars, no comparison against other state-of-the-art methods, and no discussion of hyperparameter tuning.

### Location

- **Section:** Part III: Applications (entire section)
- **Tables:** Quadrotor (line 715), Humanoid (line 847), Golf (line 890)

### Nature of the Issue

**Empirical insufficiency:**

1. **Quadrotor aerobatics (3.1):**
   - Claims "40% fewer nodes than uniform fine discretization" but:
     - What was the baseline? Uniform Δt = ?
     - How sensitive is this to εᵣ? (only one value shown: εᵣ = 0.05)
     - No comparison against ALTRO, Crocoddyl, or other modern solvers.

2. **Humanoid walking (3.2):**
   - Claims "fall rate reduced from 15% to 5%"—on what dataset?
   - Only 20 trials each—with binomial statistics, this is not statistically significant (p ≈ 0.24 using Fisher's exact test).
   - No comparison: is 5% good? What does a state-of-the-art MPC achieve?

3. **Golf swing (3.3):**
   - Results table shows "ball_speed: 71.8 m/s (99.6% of fine)" but:
     - This is **simulated data** in a code block, not experimental.
     - Where is the actual data? No plots, no raw numbers.
     - The comparison is against "uniform coarse/fine"—why not against IPOPT, SNOPT, or other NLP solvers?

4. **No ablation studies:**
   - How much does performance degrade if you remove Hessian-based adaptation and just use fixed Δt?
   - What if you use adaptive Δt but ignore residuals and adapt based on, e.g., state curvature directly?

### Why This Is a Problem

A skeptical reviewer would say:

- "These are cherry-picked examples with post-hoc tuning."
- "20 trials is not enough to claim statistical significance."
- "Simulated 'results' in code blocks are not experimental validation."
- "Where are the baselines? This could just be a re-implementation of standard methods with different names."

### Evidence / References

- **Statistical significance:** With n=20 trials, 3/20 vs 1/20 failures gives p=0.24 (Fisher's exact test). Standard practice requires p < 0.05 for significance. See [Wasserstein & Lazar (2016), "ASA Statement on p-Values"](https://doi.org/10.1080/00031305.2016.1154108).

- **Optimal control benchmarks:**
  - [ALTRO (Howell et al. 2019)](https://roboticexplorationlab.org/papers/altro-iros.pdf): State-of-the-art solver with rigorous benchmarks.
  - [Crocoddyl (Mastalli et al. 2020)](https://doi.org/10.1109/TRO.2020.3041882): Contact-rich trajectory optimization with extensive comparisons.

- **Ablation studies in ML/robotics:** Standard practice—see [Lipton & Steinhardt (2019), "Troubling Trends in ML"](https://arxiv.org/abs/1807.03341) on the importance of baselines.

### Severity

**High**: Without rigorous validation, the entire framework could be dismissed as "interesting idea, insufficient evidence."

### Suggested Remedies

1. **Expand humanoid experiment:**
   - Increase trials to n ≥ 100 to achieve statistical power.
   - Report confidence intervals (e.g., 95% CI for fall rate).
   - Compare against: (a) pure MPC, (b) pure LQR, (c) residual-adaptive (proposed).

2. **Add quantitative golf data:**
   - Remove the fake "simulated results" code block.
   - Either: (a) run actual simulations and report distributions, or (b) clearly label it as "Hypothetical Performance" and don't claim it as validation.

3. **Benchmark against ALTRO:**
   - Implement the same quadrotor flip problem in ALTRO.
   - Report: solve time, final cost, constraint violations, nodes used.
   - Show that residual-adaptive is competitive or better.

4. **Ablation study:**
   - Test: Fixed Δt (coarse), Fixed Δt (fine), Adaptive Δt (no residuals, just state-based), Adaptive Δt (residual-based).
   - Plot: Cost vs. computation time for all methods.

5. **Add error bars to all tables:**
   - Report mean ± std for all metrics.
   - Use boxplots for distributions (e.g., solve time across 50 random initializations).

---

## Critique 5: Generalization Beyond Smooth Dynamics

### Summary of Concern

The article claims to handle "hybrid systems" (e.g., heel strike in Section 3.2) by "detecting residual spikes," but provides no rigorous treatment of discontinuities. The bound in Theorem 1.1 assumes C² dynamics, which is violated at impacts.

### Location

- **Section:** 3.2 Humanoid Walking with Impacts
- **Equation:** 3.7 (impact map)
- **Claim:** "Residual behavior: At impact ||r|| → ∞ (discontinuous)"

### Nature of the Issue

**Boundary condition failure:**

1. **Theorem 1.1 requires C² dynamics:** The proof uses Taylor expansion and Hessian bounds, both undefined at discontinuities. So how can residuals be used at impacts?

2. **Detection is post-hoc:** The article says "spike above threshold → impact detected," but:
   - By the time the residual spikes, the impact has **already occurred**.
   - How do you prevent integrator failure during the discontinuity?
   - Standard hybrid systems (Westervelt et al., Grizzle et al.) use **guard functions** to predict impacts before they happen.

3. **No switching controller design:** The article mentions "switch to hybrid system model" but gives no details. What is the hybrid controller? How do you reset the state estimate? What about Zeno behavior (infinite impacts in finite time)?

### Why This Is a Problem

A hybrid systems expert would immediately object:

- "You cannot use C² analysis for discontinuous systems."
- "Residual-based impact detection is reactive, not predictive—you'll crash before adapting."
- "This is just rebranding guard functions as 'residual monitoring.'"

### Evidence / References

- **Hybrid systems theory:** [Goebel et al. (2012), "Hybrid Dynamical Systems"](https://press.princeton.edu/books/hardcover/9780691153896/hybrid-dynamical-systems) is the standard reference. Impacts require explicit treatment via reset maps, not residual bounds.

- **Bipedal walking control:** [Grizzle et al. (2014), "Models, feedback control, and open problems of 3D bipedal robotic walking"](https://doi.org/10.1016/j.automatica.2014.04.021) uses **virtual constraints + impact-aware planning**. Residuals are not mentioned because the model explicitly includes impacts.

- **Zeno behavior:** [Ames & Sastry (2005), "Characterization of Zeno behavior"](https://doi.org/10.1109/HSCC.2005.47) shows that impact detection alone is insufficient—you need Lyapunov or energy arguments to prevent infinite bouncing.

### Severity

**Medium-High**: The article claims applicability to hybrid systems, but the theoretical framework explicitly excludes them. This is a **scope overreach**.

### Suggested Remedies

1. **Restrict claims:**
   - Remove "with Impacts" from Section 3.2 title.
   - Add disclaimer: "This article addresses smooth dynamics. For systems with impacts (heel strike, collisions), see [Hybrid Tangent Spaces article]."

2. **Or expand the framework:**
   - Add Section 1.4: "Extension to Hybrid Systems."
   - Define piecewise-C² dynamics with guard functions g(x) = 0.
   - Modify Theorem 1.1: "For t ∈ [tₖ, tₖ₊₁] (between impacts), the residual bound holds. At impacts, use reset map Δ(x) explicitly."

3. **Clarify impact detection:**
   - Change "spike above threshold → impact detected" to:
     - "We monitor both residuals ||r|| and guard function g(x). When g(x) ≈ 0, we switch to impact-aware mode."
   - Add: "Residuals provide early warning of model mismatch (e.g., unexpected slip), while guard functions predict geometric impacts (e.g., heel strike)."

4. **Remove or caveat the humanoid results:**
   - If the results assume smooth dynamics between impacts (valid), state this clearly.
   - If the results claim to handle impacts via residuals (invalid), remove or add theoretical justification.

---

## Critique 6: Residual Monitoring vs. Model Predictive Control

### Summary of Concern

The article frames residual-adaptive control as novel, but it's conceptually similar to **standard MPC with error feedback**. The distinction is not clearly articulated, risking dismissal as "MPC rebranded."

### Location

- **Section:** 2.2 Residual-Triggered Mode Switching
- **Claim:** "Use residuals to switch intelligently between LQR and MPC."

### Nature of the Issue

**Unclear novelty:**

1. **MPC already monitors tracking error:** In standard MPC, the controller observes $x_{\text{meas}}$ and replans if $\|x_{\text{meas}} - x_{\text{nom}}\|$ exceeds a threshold. How is this different from residual monitoring?

2. **Residual = tracking error in the tangent space:** The observed residual is:
   $$r_{\text{obs}} = x_{\text{meas}} - (\bar{x} + \Phi \delta x_0)$$
   But $\Phi \delta x_0$ is the linearized prediction, so $r_{\text{obs}}$ is just the **prediction error**. Standard MPC uses prediction error to trigger replanning—what's new here?

3. **No comparison against error-aware MPC:** Methods like [Tube MPC (Mayne et al. 2005)](https://doi.org/10.1016/j.automatica.2004.08.019) and [Robust MPC (Rawlings & Mayne 2009)](https://www.springer.com/gp/book/9780857296009) explicitly account for modeling errors. How does residual-aware control compare?

### Why This Is a Problem

A control theorist would ask:

- "Why not just use tracking error $\|x - \bar{x}\|$ directly?"
- "What does the tangent space decomposition buy you?"
- "This looks like MPC with a fancy name for prediction error."

Without a clear answer, the contribution is unclear.

### Evidence / References

- **Tube MPC:** [Mayne et al. (2005)](https://doi.org/10.1016/j.automatica.2004.08.019) uses error bounds to define tubes around nominal trajectories—exactly what Section 2.3 does.

- **Learning-based MPC:** [Hewing et al. (2020), "Learning-based MPC"](https://doi.org/10.1016/j.arcontrol.2020.10.001) uses **model error prediction** to adapt MPC online—similar to residual prediction.

- **Error-triggered replanning:** [Kalakrishnan et al. (2011), STOMP](https://doi.org/10.1177/0278364911406761) uses trajectory deviation to trigger re-optimization—predates this work.

### Severity

**Medium**: The approach may be novel, but the novelty is not clearly articulated. This invites confusion and diminishes perceived contribution.

### Suggested Remedies

1. **Add explicit comparison section:**
   - Section 2.2.1: "Comparison to Standard MPC Error Monitoring"
   - Explain:
     - Standard MPC: Replan when $\|x - \bar{x}\| > \epsilon$ (total error).
     - Residual-aware: Replan when $\|r\| > \epsilon_r$ (second-order error).
     - Advantage: Residuals isolate **nonlinearity-induced error** from disturbances/noise.

2. **Clarify the benefit:**
   - Add: "Monitoring residuals separately from first-order deviations allows us to distinguish between:
     - **Disturbances** (captured by δx, handled by LQR), and
     - **Model nonlinearity** (captured by r, requiring MPC).
   - This enables finer-grained mode switching than total error alone."

3. **Cite and differentiate from Tube MPC:**
   - Add: "Our approach complements Tube MPC by providing **geometric residual bounds** (Theorem 1.1) instead of worst-case disturbance bounds. This allows tighter tubes in low-curvature regions."

4. **Experimental comparison:**
   - In Section 3.1 (quadrotor), compare:
     - Residual-triggered switching vs.
     - Error-triggered switching (||x - x̄|| threshold) vs.
     - Always-MPC.
   - Show that residual-based switching is more efficient.

---

## Critique 7: Missing Boundary Conditions for Adaptive Timestep

### Summary of Concern

Equation 2.1 (adaptive timestep rule) can produce arbitrarily small Δt when M is large or δx is large, potentially causing numerical issues or computational blow-up. No minimum timestep is enforced in the theorem—only in the code (Δt ∈ [0.001, 0.1]).

### Location

- **Section:** 2.1.2 Adaptive Timestep Selection Rule
- **Equation:** 2.1
- **Code:** Line 1141 (clipping)

### Nature of the Issue

**Unstated assumptions:**

1. **No lower bound in theory:** Equation 2.1 gives $\Delta t = \sqrt{\frac{2\epsilon_r}{M \|\delta x_{\max}\|^2}}$. If M → ∞ or δx → ∞, then Δt → 0.

2. **Ad-hoc clipping in code:** Line 1141 clips Δt to [0.001, 0.1], but this is **heuristic**, not principled. What if the system needs Δt < 0.001 to satisfy the residual bound?

3. **Computational cost ignored:** Very small Δt → many nodes → slow optimization. The article claims "computational efficiency" but doesn't analyze the trade-off.

### Why This Is a Problem

A rigorous paper would:

- Derive the minimum Δt from numerical stability constraints (e.g., CFL condition for integrators).
- Analyze the trade-off: smaller Δt → more accuracy but higher cost.
- Provide guidance: when is it better to switch to a different integrator (e.g., implicit) rather than shrink Δt?

Without this, the adaptive rule is **unprincipled**.

### Evidence / References

- **CFL condition:** [Courant–Friedrichs–Lewy (1928)](https://link.springer.com/article/10.1007/BF01456804) is the classical reference for timestep stability in PDEs. For ODEs, see [Hairer & Wanner (1996)](https://link.springer.com/book/10.1007/978-3-642-05221-7).

- **Computational complexity:** [Betts (2010)](https://epubs.siam.org/doi/book/10.1137/1.9780898718577) discusses mesh refinement strategies and notes that **too-fine meshes can degrade conditioning** of the NLP.

### Severity

**Low-Medium**: Practical impact is limited (clipping prevents disasters), but the theoretical gap is noticeable.

### Suggested Remedies

1. **Add minimum timestep analysis:**
   - Section 2.1.4: "Minimum Timestep from Numerical Stability"
   - Derive: For RK4 integrator with Lipschitz constant L, require $\Delta t \geq \Delta t_{\min} = \frac{1}{L}$ for stability.

2. **Justify clipping:**
   - Change hard-coded [0.001, 0.1] to:
     - $\Delta t_{\min}$ = max(10⁻³, 1/L) (stability)
     - $\Delta t_{\max}$ = εᵣ / (M δx²) (accuracy)

3. **Discuss computational trade-off:**
   - Add: "In regions with M → ∞ (near singularities), adaptive Δt may become impractically small. In such cases, alternative methods (collocation, implicit integration) should be used."

4. **Add cost model:**
   - Estimate total computation: Cost ≈ N_iter × Σ (1/Δtᵢ) × C_step.
   - Plot: Computation vs. εᵣ to show the Pareto frontier.

---

## Critique 8: Lack of Literature Engagement with Recent Work

### Summary of Concern

The article cites foundational references (Li & Todorov 2004, Mayne et al. 2005) but omits significant recent work on adaptive trajectory optimization, residual dynamics, and learning-based MPC. This creates the impression that the work is isolated from the current state of the art.

### Location

- **Section:** 5.2 Further Reading
- **Throughout:** Missing citations to 2015+ work

### Nature of the Issue

**Literature gaps:**

1. **Adaptive mesh refinement in trajectory optimization:**
   - [GPOPS-II (Patterson & Rao 2014)](https://doi.org/10.1145/2558904): Uses adaptive mesh refinement in Gaussian quadrature collocation—directly relevant to adaptive Δt.
   - [Hereid et al. (2016), "Frost: Fast robot optimization and simulation toolkit"](https://doi.org/10.1109/IROS.2016.7759025): Uses adaptive time grids for contact-rich systems.

2. **Residual learning in model-based RL:**
   - [Nagabandi et al. (2018), "Neural network dynamics for model-based deep RL"](https://arxiv.org/abs/1708.02596): Learns residual dynamics $\hat{f} = f_{\text{nominal}} + f_{\text{residual}}$.
   - [Mehta et al. (2020), "Learning quadrupedal locomotion over challenging terrain"](https://arxiv.org/abs/2010.11251): Uses residuals to adapt MPC online.

3. **Curvature-aware control:**
   - [Manchester (2017), "LQR-Trees with input and state constraints"](https://doi.org/10.1016/j.automatica.2017.06.027): Uses funnels (similar to residual tubes) for verification.
   - [Majumdar & Tedrake (2017), "Funnel libraries for real-time robust feedback motion planning"](https://doi.org/10.1177/0278364917712421): Closely related to residual-aware tube MPC.

4. **Geometric mechanics in control:**
   - [Ratliff et al. (2018), "Riemannian Motion Policies"](https://arxiv.org/abs/1801.02854): Uses manifold curvature for policy design—very relevant to Section 1.3.

### Why This Is a Problem

Omitting recent work suggests:

- The authors are unaware of the current state of the art.
- The contribution is incremental but presented as foundational.
- Reviewers will say: "This is just [X] rebranded" where X = GPOPS-II, residual learning, funnel libraries, etc.

### Evidence / References

Listed above.

### Severity

**Medium**: Does not invalidate results, but diminishes perceived novelty and could lead to rejection if reviewers perceive lack of scholarship.

### Suggested Remedies

1. **Add "Related Work" section:**
   - Insert before Section 1: "0.1 Relationship to Prior Work"
   - Subsections:
     - Adaptive mesh methods in trajectory optimization
     - Residual learning in robotics
     - Geometric control and funnel methods
     - Tube MPC and robust control
   - For each, explain: how this work differs or builds on it.

2. **Update bibliography:**
   - Add at least 5-10 papers from 2015-2025 in optimal control, robotics, and geometric mechanics.

3. **Explicitly differentiate:**
   - Add: "Unlike residual learning methods (Nagabandi et al. 2018) which learn f_residual from data, we derive residual bounds analytically from Hessian analysis."
   - Add: "Unlike funnel methods (Majumdar & Tedrake 2017) which compute funnels offline, our residual-aware tubes adapt online based on observed curvature."

---

## Summary Table of Critiques

| # | Issue | Severity | Primary Remedy |
|---|-------|----------|----------------|
| 1 | Theorem 1.1 proof gaps | Medium-High | Explicit assumptions, revised proof |
| 2 | Adaptive DDP convergence unsupported | Medium | Downgrade to conjecture or prove rigorously |
| 3 | Hessian bound computation errors | Medium | Numerical validation, corrected norms |
| 4 | Insufficient experimental validation | High | More trials, error bars, baselines |
| 5 | Hybrid systems scope overreach | Medium-High | Restrict claims or expand theory |
| 6 | Unclear novelty vs. MPC | Medium | Explicit comparison section |
| 7 | Missing timestep bounds | Low-Medium | Minimum Δt analysis |
| 8 | Outdated literature | Medium | Related work section, recent citations |

---

## Overall Assessment

### Strengths

- **Core intuition is sound:** Residuals as curvature signals is a valuable perspective.
- **Practical algorithms:** The JAX implementation is well-structured and usable.
- **Geometric interpretation:** Section 1.3 provides good intuition.

### Weaknesses

- **Theoretical rigor:** Proofs are sketchy, assumptions unstated, convergence unsupported.
- **Experimental validation:** Results are preliminary, lack statistical significance, and missing baselines.
- **Scope clarity:** Claims to handle hybrid systems and general nonlinear control, but theory is limited to smooth, controllable systems.

### Verdict

This is a **strong draft** of a potentially important paper, but it requires significant tightening before publication in a top-tier venue (IEEE TAC, Automatica, IJRR).

For a blog/website, it's **excellent** as an accessible introduction to the ideas, but should be clearly labeled as:

- "Work in progress"
- "Preliminary results"
- "Not peer-reviewed"

### Recommended Next Steps

1. **Immediate (before public release):**
   - Add disclaimers about proof sketches and preliminary results.
   - Fix Hessian computation errors (Critique 3).
   - Remove or qualify hybrid systems claims (Critique 5).

2. **Short-term (for publication):**
   - Expand experimental validation (Critique 4): more trials, error bars, ALTRO comparison.
   - Add Related Work section (Critique 8).
   - Clarify novelty vs. MPC (Critique 6).

3. **Long-term (for theoretical contribution):**
   - Rigorous proof of Theorem 2.1 (Critique 2).
   - Complete proof of Theorem 1.1 with explicit assumptions (Critique 1).
   - Formal extension to hybrid systems or remove claims (Critique 5).

---

## Final Word Count

**Total:** ~3,850 words

This critique is intended to **strengthen the work**, not diminish it. The ideas are compelling—the execution needs to match the ambition.
