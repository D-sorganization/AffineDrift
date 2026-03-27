# Textbook Review: Recommended Additional Material

**Date:** 2026-02-21
**Reviewer:** Antigravity Agent
**Textbook:** *Tangent-Space Methods for Nonlinear Control and Biomechanics*

---

## Executive Summary

The textbook is structured as an 8-chapter progression:

| Ch | Title | Core Focus | Lines |
|----|-------|------------|-------|
| 1 | Foundations | Tangent spaces, Fréchet derivative, axioms | 963 |
| 2 | Variational Dynamics | STM, Peano-Baker, Duhamel, sensitivity | 1163 |
| 3 | Superposition | Control-affine structure, 3 derivations | 1221 |
| 4 | Contraction | Metric certificates, partial contraction, CCM | 996 |
| 5 | Optimal Control | DDP, iLQR, Riccati recursion | 955 |
| 6 | Duality | Stability-optimality bridge, robustness margins | 1063 |
| 7 | Counterfactuals | ZTCF, ZVCF, drift-control ratio | 1186 |
| 8 | Applications | Golf, robotics, aerospace, automotive | 1646 |

**Total: ~9,200 lines across 8 chapters.**

The book has a clear and distinctive thesis (tangent-space exactness → contraction → optimal control → drift decomposition) that is well-developed. Below I identify material that would strengthen the text both as a **nonlinear control textbook** and within this book's specific framework. Items are organized by priority.

---

## PRIORITY 1: Critical Gaps

These are topics whose absence creates a logical hole in the book's argument or limits its applicability as a graduate reference.

### 1.1 Observability and Estimation (Missing Chapter)

**What's missing:** The book covers controllability implicitly (through the control-affine structure and DDP), but observability and state estimation are entirely absent. A nonlinear control textbook that discusses trajectory optimization without discussing how states are measured or estimated has a significant gap.

**Why it matters for this book:** The duality treated in Chapter 6 covers the control side (LQR ↔ Lyapunov) but doesn't cover the Kalman filter side. The Riccati equation for estimation (the dual Riccati) is the mirror image of the control Riccati — and the stability-optimality duality applies equally to observers. This is a missed opportunity.

**Recommendation:** Add a chapter (or substantial section in Ch6) covering:
- The variational observer: propagating uncertainty through tangent spaces
- Extended Kalman Filter (EKF) as tangent-space estimation
- Contraction-based observer design (a natural fit: Andrieu, Praly, Astolfi 2009)
- The dual Riccati interpretation: the estimation Riccati as a contraction metric for the observer error dynamics
- Observability Gramians as the estimation analogue of controllability Gramians

**Placement:** New Chapter 6.5 or expansion of Chapter 6 to "The Estimation–Control Duality"

---

### 1.2 Lie Bracket, Controllability, and Accessibility (Missing from Ch1/Ch3)

**What's missing:** Ch3 covers the control-affine structure `ẋ = f(x) + G(x)u` but never discusses the Lie bracket `[f, g_i]` or the Lie algebraic rank condition (LARC) for local accessibility. For a book that takes geometric structure seriously, this is a notable omission.

**Why it matters for this book:** The Lie bracket tells you which directions in state space are reachable through *combinations* of drift and control — even if they are not in the span of `G(x)`. For underactuated systems (which the book discusses extensively in Ch7-8), the Lie bracket structure determines which motions are achievable. The golf swing, as an underactuated system, has exactly this character.

**Recommendation:** Add a section to Ch3 covering:
- Lie brackets `[f, g]` and their geometric interpretation as curvature of the control distribution
- The accessibility rank condition
- Chow's theorem (reachability via sufficient brackets)
- Connection to underactuation: why the golf swing can reach states not in the span of `B(q)`, through inertial coupling (which is precisely the Lie bracket structure)

**Placement:** Ch3, after the control-affine derivation, before the energy perspective

---

### 1.3 Model Predictive Control (MPC) — The Online Version of DDP

**What's missing:** Ch5 covers DDP/iLQR in detail as offline trajectory optimization, but never discusses MPC — the *online, receding-horizon* version that is the dominant paradigm in modern control engineering. The book mentions MPC exactly once (in passing, in Ch8's pitfalls section).

**Why it matters for this book:** The book's framework (linearize locally, solve Riccati, verify contraction) is exactly the computational loop of MPC. Omitting MPC means the book's most powerful practical contribution — the idea that tangent-space methods are used in real-time — goes unstated.

**Recommendation:** Add a section to Ch5 (or as a short new chapter between Ch5 and Ch6):
- MPC as a receding-horizon DDP/iLQR
- Warm-starting: using the previous solution's shifted trajectory
- Stability of MPC: terminal cost as a local CLF (connects to Ch4's contraction)
- Computational considerations: how many DDP iterations per control cycle?
- Real-time iteration (RTI) scheme: one Newton step per time step

**Placement:** Ch5, after the DDP algorithm section, before convergence analysis. Or new Chapter 5.5.

---

## PRIORITY 2: Strong Additions

These would significantly strengthen the book's coverage and its position in the field.

### 2.1 Feedback Linearization and Exact Linearization

**What's missing:** The book emphasizes that linearization is exact *infinitesimally* but never discusses **exact (global) linearization via feedback** — the input-output linearization framework of Isidori, where an appropriate coordinate transformation + feedback renders the system exactly linear in a neighborhood.

**Why it matters for this book:** This is the natural counterpoint to the book's thesis. The book argues "linearization is exact in tangent spaces." Feedback linearization says "under the right conditions, you can make it exact *globally* (modulo zero dynamics)." Contrasting these perspectives would strengthen the reader's understanding of both.

**Recommendation:**
- Definition of relative degree, normal form, zero dynamics
- When exact linearization is possible (involutivity of the distribution)
- Why it often fails in practice (cancellation of useful nonlinearities, robustness issues)
- Connection to Ch4: feedback linearization cancels nonlinearity; contraction-based control *exploits* it
- The philosophical contrast: exact linearization *fights* the manifold, contraction theory *works with* it

**Placement:** Ch3 or new Ch3.5, between superposition and contraction

---

### 2.2 Exercises and Problems

**What's missing:** The textbook has zero exercises. For a book aimed at "graduate students and practicing engineers" (Preface, line 241), this is a significant pedagogical weakness. Every major nonlinear control textbook (Khalil, Slotine & Li, Sastry, Isidori) includes extensive problem sets.

**Recommendation:** Add 8-12 exercises per chapter, including:
- **Computational exercises** (e.g., "Compute the STM for the following 2D system")
- **Proof exercises** (e.g., "Prove that the semigroup property holds for discrete-time STMs")
- **Conceptual exercises** (e.g., "Explain why contraction rate λ decreases when the condition number κ(M) increases")
- **Application exercises** (e.g., "For the double pendulum of Ch7, compute the ZTCF at three configurations and interpret the drift-control ratio")
- **Programming exercises** (e.g., "Implement the DDP algorithm from Algorithm 5.1 for the inverted pendulum and reproduce Figure X")

**Placement:** End of each chapter

---

### 2.3 Passivity and Port-Hamiltonian Structure

**What's missing:** Ch3 discusses the energy perspective (kinetic/potential energy decomposition) but never introduces passivity — the property that a system dissipates energy. Ch6 discusses the Willems dissipation framework but doesn't connect it to passivity of the plant.

**Why it matters for this book:** The golf swing analysis (Ch7-8) fundamentally involves energy transfer between subsystems. The port-Hamiltonian formulation makes this completely explicit: each body segment is a port that exchanges power with its neighbors, and passivity of the individual ports guarantees stability of the interconnection. This is the energy-based complement to the contraction-based analysis in Ch4.

**Recommendation:**
- Passivity definition (supply rate, storage function)
- Mechanical systems as naturally passive (Hamiltonian = storage)
- Interconnection of passive subsystems (cascade stability without contraction)
- Port-Hamiltonian structure: `ẋ = (J(x) - R(x))∂H/∂x + G(x)u`
- Connection to contraction: passive systems contract in the energy metric

**Placement:** Ch3 (Energy Perspective section) or new Ch3.5

---

### 2.4 Stochastic Extensions and Process Noise

**What's missing:** The entire treatment is deterministic. Real systems have process noise and measurement uncertainty. The variational dynamics of Ch2 transfer directly to the stochastic case (Extended Kalman Filter covariance propagation), and the contraction framework of Ch4 has stochastic extensions (stochastic contraction analysis, Wang & Slotine 2005).

**Recommendation:** Add a section (not full chapter) covering:
- Brownian-motion perturbations in the variational equation
- The Fokker-Planck perspective: how probability densities evolve on manifolds
- Stochastic contraction: contraction rate as a bound on the mean trajectory divergence
- Connection to robust control: process noise as a structured uncertainty

**Placement:** Ch4 or Ch6, as a section on "Extensions to Stochastic Systems"

---

### 2.5 Geometric Integration and Structure-Preserving Numerics

**What's missing:** Ch2 discusses numerical computation of the STM (Padé, Runge-Kutta) but never addresses **structure preservation**: symplectic integrators for Hamiltonian systems, Lie group integrators for SO(3)/SE(3), and variational integrators that preserve energy and momentum. For the golf swing (which involves rotation groups and long-time energy tracking), this matters.

**Recommendation:**
- Why standard RK4 can violate conservation laws (energy drift)
- Symplectic Euler and Störmer-Verlet for Hamiltonian systems
- Lie group integration for rotation dynamics (Crouch-Grossman, Munthe-Kaas)
- Variational integrators: discrete Hamilton's principle
- When structure preservation is critical: long-horizon simulation, periodic orbits, contraction rate computation

**Placement:** Ch2, new subsection under "Numerical Computation"

---

## PRIORITY 3: Valuable Additions

These would round out the text and make it more comprehensive.

### 3.1 Funnel Control and Tube-Based Approaches

**Relevance:** The contraction analysis in Ch4 implicitly defines a *tube* around the nominal trajectory — the set of all trajectories that are exponentially converging. Making this explicit connects to the modern **robust tube MPC** literature and **funnel control** (Ilchmann & Ryan, where the tracking error is guaranteed to stay within a prescribed performance funnel).

**Placement:** Ch4 or Ch5, as a section connecting contraction tubes to funnel/tube MPC

---

### 3.2 Sum-of-Squares (SOS) Programming for Metric Search

**Relevance:** Ch4 discusses the LMI-based search for contraction metrics but doesn't mention SOS programming — the polynomial optimization technique that extends LMI-based search to polynomial metrics on polynomial systems. This is the computational frontier of contraction theory.

**Placement:** Ch4, after the CCM section

---

### 3.3 Multi-Body Dynamics: Recursive Algorithms

**Relevance:** Ch3 derives the mass matrix and Coriolis terms from the Lagrangian, but for systems with many DOF (humanoid robots, full-body golf models), direct computation of M(q) is O(n³). The Articulated Body Algorithm (ABA) and Recursive Newton-Euler Algorithm (RNEA) from Featherstone (already in the bibliography) achieve O(n) — essential for real-time applications.

**Placement:** Ch3 or Ch8, as a section on "Computational Scaling for Large Systems"

---

### 3.4 The Connection Between Chapters — A Unifying Diagram

**Relevance:** The book's central contribution is the *connections* between tangent spaces, contraction, optimal control, and counterfactuals. But these connections are spread across 8 chapters and can be hard to keep in mind. A single figure — a "concept map" showing how the key objects (STM, contraction metric, Riccati matrix, drift-control ratio) relate — would significantly improve comprehension.

**Placement:** Preface or Chapter 1 (as a roadmap figure), then revisited in Chapter 8

---

### 3.5 Appendix: Differential Geometry Primer

**Relevance:** The book assumes "familiarity with linear algebra, multivariable calculus, and ODEs" but uses concepts from differential geometry (manifolds, tangent bundles, pushforward/pullback). A short appendix (10-15 pages) providing the key definitions (smooth manifold, tangent space, cotangent space, metric tensor, connection) with examples would make the book self-contained.

**Placement:** Appendix A

---

### 3.6 Appendix: Linear Algebra Review (Matrix Inequalities, Loewner Order)

**Relevance:** The contraction theory chapters (Ch4, Ch6) heavily use the Loewner partial order on symmetric matrices (A ≼ B), Schur complements, and eigenvalue bounds. These are not standard in all graduate programs. A 5-page appendix would prevent the reader from needing to consult additional references.

**Placement:** Appendix B

---

## Summary: Impact–Effort Matrix

| Topic | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Observability/Estimation | ★★★★★ | High (new chapter) | 1 |
| Lie Brackets/Controllability | ★★★★★ | Medium (new section) | 1 |
| MPC | ★★★★☆ | Medium (new section) | 1 |
| Feedback Linearization | ★★★★☆ | Medium (new section) | 2 |
| Exercises | ★★★★★ | High (96+ exercises) | 2 |
| Passivity/Port-Hamiltonian | ★★★★☆ | Medium (new section) | 2 |
| Stochastic Extensions | ★★★☆☆ | Medium (new section) | 2 |
| Geometric Integration | ★★★☆☆ | Low (subsection) | 2 |
| Funnel/Tube Control | ★★★☆☆ | Low (subsection) | 3 |
| SOS Programming | ★★☆☆☆ | Low (subsection) | 3 |
| Recursive Multi-Body | ★★☆☆☆ | Low (subsection) | 3 |
| Concept Map Diagram | ★★★★☆ | Low (single figure) | 3 |
| DiffGeo Appendix | ★★★☆☆ | Medium (appendix) | 3 |
| LinAlg Appendix | ★★☆☆☆ | Low (appendix) | 3 |

---

## Specific Technical Recommendations

### Regarding Existing Chapter Content

1. **Ch1, line 486:** The warning box about the sin(x) residual is a good pedagogical moment. Consider adding a brief remark that for *multivariate* functions, the residual structure is governed by the Hessian tensor — this previews the second-order expansion in Ch5.

2. **Ch2, STM computation:** The Padé approximation and direct integration methods are covered, but the Magnus expansion (an alternative to Peano-Baker that converges faster for oscillatory systems) is not mentioned. This is relevant for systems with rapidly varying A(t).

3. **Ch3, Screw theory derivation:** This is one of three parallel derivations (Newton-Euler, Lagrangian, Screw). The screw theory treatment is the most condensed. Consider expanding it or adding a comparison table showing the computational trade-offs of each formulation.

4. **Ch4, CCM section (line 452):** The control contraction metric is introduced via the dual variable W = M⁻¹ and the pointwise LMI. Consider noting that the search for W (and hence the feedback law) can be made convex in W — this is the main computational advantage of CCM over direct metric search, and it's the key result of Manchester & Slotine 2017 (already cited).

5. **Ch5, DDP convergence (line 412):** The convergence analysis shows that DDP achieves local quadratic convergence. Consider mentioning the global convergence results of iLQR with line search (which only guarantees first-order convergence but from any starting point) — this trade-off (local quadratic vs. global linear) is practically important.

6. **Ch6, H∞ connection (line 780):** The section connecting LQR duality to H∞ robust control is present but brief. Consider expanding it to show the game-theoretic interpretation: the optimal controller plays against the worst-case disturbance, and the Riccati equation at the saddle point simultaneously certifies both optimality and robustness.

7. **Ch7, Data-driven drift estimation (line 436):** The persistent excitation condition for separating drift from control is mentioned but deserves more attention. Consider adding the specific rank condition on the input regression matrix and noting its connection to system identification theory (Ljung).

8. **Ch8, Golf section:** The Schur complement decomposition of the mass matrix (separating rigid body and shaft modes) is the most technically novel contribution of the applications chapter. Consider adding a remark on how this decomposition generalizes to any system with a fast/slow separation — the fast modes are "shaft-like" and the slow modes are "body-like."
