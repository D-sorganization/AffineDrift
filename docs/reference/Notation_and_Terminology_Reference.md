# Notation and Terminology Reference

**AffineDrift: A Control-Theoretic Framework for Golf Biomechanics**

This document provides precise definitions, mathematical notation, and conceptual explanations for core terms used throughout the AffineDrift framework. It is designed for reference and cross-article navigation.

---

## 1. Mathematical Notation

Standard notation conventions used throughout AffineDrift articles:

| Symbol | Meaning | Context |
|--------|---------|---------|
| $x$ | State vector | $x \in \mathbb{R}^n$; includes configuration and velocity |
| $q$ | Generalized coordinates (configuration) | $q \in \mathbb{R}^m$; joint angles, positions |
| $\dot{q}$ | Generalized velocities | Time derivative of $q$ |
| $\ddot{q}$ | Generalized accelerations | Time derivative of $\dot{q}$ |
| $u$ | Control input (generalized torques/forces) | $u \in \mathbb{R}^p$; outputs of muscular effort |
| $f(x)$ | Drift vector field | Passive dynamics; zero-input system evolution |
| $g(x)$ or $G(x)$ | Input matrix; actuation matrix | State-dependent coupling between $u$ and $\ddot{x}$ |
| $B(x)$ | Alternative notation for input matrix | Common in some robotics literature |
| $M(q)$ | Mass (inertia) matrix | Positive definite; encodes kinetic energy structure |
| $C(q, \dot{q})$ | Coriolis and centrifugal terms | Velocity-dependent forces; $\sim \mathcal{O}(\dot{q}^2)$ |
| $G(q)$ | Gravity vector | Potential force contributions |
| $\tau$ | Generalized joint torques | Control effort; output of muscles at actuated joints |
| $J(q)$ | Task Jacobian | Maps generalized coordinates to task space (e.g., hand position) |
| $\lambda$ | Constraint multipliers (Lagrange multipliers) | Forces enforcing kinematic constraints |
| $\phi(q)$ | Constraint equation | $\phi(q) = 0$ defines constraint manifold |
| $J_c(q)$ | Constraint Jacobian | $J_c = \partial \phi / \partial q$ |
| $p$ | Costate vector | Dual variable in optimal control / Hamiltonian formalism |
| $H(x, p)$ | Control Hamiltonian | $H = \sup_u [p^\top(f(x) + g(x)u)]$; governs reachability |
| $K(q)$ or $K_{\text{eff}}$ | Effective stiffness matrix | Impedance; used in constraint collapse analysis |
| $\Delta t$ | Time interval | Often used in reachability and control cone analysis |
| $\mathcal{R}(t; x_0)$ | Reachable set from $x_0$ at time $t$ | Set of states attainable under bounded controls |
| $\mathcal{V}(x)$ | Accessibility distribution | Span of control vector fields and their brackets |
| $[f, g]$ | Lie bracket of $f$ and $g$ | Measures non-commutativity; $[f,g] = (\nabla g) f - (\nabla f) g$ |
| $\mathrm{span}\{\cdot\}$ | Linear span (over reals) | Generates linear subspace |
| $\mathcal{O}(x^n)$ | Order of magnitude | For scaling analysis |
| $\nabla_u f$ | Partial derivative of $f$ w.r.t. $u$ | Used to formalize drift invariance |

### Operator Conventions

- **Time derivatives**: $\dot{(\cdot)} = d(\cdot)/dt$
- **Partial derivatives**: $\nabla_{(\cdot)} = \partial(\cdot)/\partial(\cdot)$
- **Euclidean norm**: $\\|\mathbf{v}\\| = \sqrt{\mathbf{v}^\top \mathbf{v}}$ (unless otherwise specified)
- **Weighted norm**: $\\|\mathbf{v}\\|_M = \sqrt{\mathbf{v}^\top M \mathbf{v}}$ (inertia-weighted)

---

## 2. Core Concepts (Alphabetical)

### **Accessibility Distribution**
- **Symbol/Abbreviation**: $\mathcal{V}(x)$
- **Definition**: The linear subspace spanned by the control vector field $g(x)$ and all iterated Lie brackets $[f,g]$, $[f,[f,g]]$, etc. Formally: $\mathcal{V}(x) = \mathrm{span}\{g(x), [f(x),g(x)], [f(x),[f(x),g(x)]],\ldots\}$
- **Intuitive Explanation**: The set of directions the system can move at state $x$ by combining drift and control.
- **First Introduced**: *Nonlinear Control Insights*
- **Key Properties**: Dimension of $\mathcal{V}$ governs small-time local controllability. As drift dominates, $\dim(\mathcal{V})$ effectively shrinks relative to drift magnitude.

---

### **Affine Structure** (Control-Affine System)
- **Symbol/Abbreviation**: $\dot{x} = f(x) + g(x)u$
- **Definition**: A nonlinear dynamical system where the state derivative depends linearly on control input $u$. Formally: the system is affine in $u$, meaning $\dot{x}$ is a linear function of $u$ for fixed $x$.
- **Intuitive Explanation**: A system where inputs can be "dialed in" proportionally, like adding separate force sources together; the effects superpose.
- **First Introduced**: *Superposition in Affine Control Systems*; *Affine Control Interpretation of the Golf Swing*
- **Key Properties**:
  - Superposition with respect to inputs holds (trajectories themselves do not superpose due to nonlinearity in $f(x)$).
  - Enables clean decomposition into drift (passive) and input (active) components.
  - Drift invariance: $f(x)$ is independent of instantaneous $u$.

---

### **Configuration Space**
- **Symbol/Abbreviation**: $q$, $Q$, $\mathbb{C}$ (geometry literature)
- **Definition**: The space of generalized coordinates describing the system's shape. For a golfer-club system, $q \in \mathbb{R}^m$ where $m$ is the number of degrees of freedom (e.g., shoulder angle, elbow angle, wrist angle, club orientation).
- **Intuitive Explanation**: The complete "snapshot" of where all the body parts and the club are at a given instant.
- **First Introduced**: Throughout; fundamental to Lagrangian mechanics formulations.
- **Key Properties**:
  - Kinetic energy depends on $\dot{q}$ via $T = \frac{1}{2}\dot{q}^\top M(q) \dot{q}$.
  - Potential energy depends on $q$ via gravity.
  - Dynamics evolve on tangent bundle $T\mathbb{C} = \mathbb{C} \times \dot{\mathbb{C}}$.

---

### **Constraint Collapse** (Intentional)
- **Symbol/Abbreviation**: (no standard symbol; sometimes "Jacobian collapse")
- **Definition**: The neuromuscular strategy of rapidly increasing effective impedance in selected degrees of freedom near impact, such that $K_{\text{eff}}(t) / K_{\text{perturbation}} \to \infty$ in those directions. Mathematically: $K_{\text{eff}}(t) = K_0 + \Delta K_{\text{co-contraction}}(t)$ where $\Delta K$ increases sharply during $[t_{\text{impact}} - \tau, t_{\text{impact}}]$ with $\tau \sim 50$-100 ms.
- **Intuitive Explanation**: Deliberately stiffening selected joints at the last moment to lock in the desired motion path while allowing force to concentrate on the ball impact point.
- **First Introduced**: *Intentional Constraint Collapse at Impact*
- **Key Properties**:
  - Not a kinematic singularity (rank loss in Jacobian); rather, a continuous high-impedance regime.
  - Creates "virtual constraints" that mimic rank loss without geometric discontinuity.
  - Timing is critical: applied late to preserve energy transfer earlier in swing.
  - Achieved through neuromuscular co-contraction of antagonist muscles.

---

### **Contraction Metric**
- **Symbol/Abbreviation**: (not extensively used in current articles; related to Lyapunov stability)
- **Definition**: A Riemannian metric on state space under which trajectories exponentially converge to each other. For a metric $M(x)$, a system is contracting if $\frac{1}{2}\frac{d}{dt}(M(x)) + M(x)\frac{\partial f}{\partial x} + \frac{\partial f}{\partial x}^\top M(x) \preceq -\lambda M(x)$ for some $\lambda > 0$.
- **Intuitive Explanation**: A mathematical tool to prove that nearby trajectories inevitably get squeezed together, guaranteeing exponential stability.
- **First Introduced**: Future research directions (mentioned in *Nonlinear Control Insights*).
- **Key Properties**: Sufficient condition for stability that does not require finding a Lyapunov function; works for time-varying systems.

---

### **Control Cone**
- **Symbol/Abbreviation**: $\mathcal{C}_c(x)$; sometimes $\mathcal{C}_{\text{control}}(x)$
- **Definition**: The instantaneous set of directions the system can move via control perturbations. Formally: $\mathcal{C}_c(x) = \lim_{\Delta t \to 0^+} \mathcal{R}(\Delta t; x)$ where $\mathcal{R}(\Delta t; x)$ is the reachable set from $x$ in time $\Delta t$. Spanned by $\mathcal{V}(x)$ scaled by control authority.
- **Intuitive Explanation**: The "cone" of future states you can reach; it narrows as drift overwhelms control, analogous to a light cone in relativity.
- **First Introduced**: *Drift-Control Ratio in the Golf Swing* (Section 6)
- **Key Properties**:
  - Wide when control dominates drift.
  - Collapses to a thin tube along the drift direction when drift dominates (high DCR).
  - Anisotropic ("pancake-shaped"): thin in high-inertia directions, wide in low-inertia directions.
  - Norm-dependent in absolute dimensions; norm-independent in qualitative narrowing.

---

### **Drift** (Passive Dynamics)
- **Symbol/Abbreviation**: $f(x)$; sometimes called "zero-torque dynamics"
- **Definition**: The vector field governing system evolution under zero applied torque: $\dot{x} = f(x)$ when $u \equiv 0$. Encodes gravity, inertia, Coriolis/centrifugal effects, and elastic recoil.
- **Intuitive Explanation**: "What the system wants to do on its own" due to physics, without muscular intervention. Like coasting downhill on a bicycle.
- **First Introduced**: *Affine Control Interpretation of the Golf Swing*; foundational to all articles.
- **Key Properties**:
  - State-dependent: $f(x) = f(q, \dot{q})$ depends on configuration and velocity.
  - Causally upstream: reflects accumulated motion history (position, velocity, shaft deflection).
  - Scales quadratically with velocity in mechanical systems: $\|f(x)\| \sim \mathcal{O}(\dot{q}^2)$ (Coriolis/centrifugal terms).
  - Input-independent: $\nabla_u f(x) = 0$ (drift invariance).

---

### **Drift-Control Ratio** (DCR)
- **Symbol/Abbreviation**: $\mathrm{DCR}(t)$
- **Definition**: The ratio of drift force magnitude to control force magnitude on the dynamic fiber (acceleration subspace):
$$\mathrm{DCR}(t) = \frac{\|M^{-1}(C\dot{q} + G)\|}{\|M^{-1}\tau\|} \approx \frac{b\|\dot{q}(t)\|^2}{c\|\tau(t)\|}$$
where $b$ and $c$ are scaling constants depending on system parameters and the chosen norm.
- **Intuitive Explanation**: A number that tells you "how much is physics doing the work versus your muscles." DCR = 1 means equal forces; DCR = 100 means physics is 100 times stronger.
- **First Introduced**: *Drift-Control Ratio in the Golf Swing*
- **Key Properties**:
  - Increases monotonically through the downswing (quadratic numerator, bounded denominator).
  - Reaches 50-200+ by late downswing; peaks before impact.
  - Norm-independent in direction of growth; specific threshold "DCR > 10 = collapse" is norm-dependent.
  - Governs gross trajectory controllability; high DCR ⟹ trajectory is ballistically predetermined.

---

### **Drift Invariance**
- **Symbol/Abbreviation**: (principle; no single symbol)
- **Definition**: The mathematical property that the passive dynamics vector field $f(x)$ is independent of the instantaneous control input $u$: $\nabla_u f(x) = 0$. This is an assumption about mechanical systems, not a universal law.
- **Intuitive Explanation**: The "passive physics" part of your swing doesn't change based on what your muscles are currently doing. Your momentum and gravity operate independently.
- **First Introduced**: *Nonlinear Control Insights* (Section on Drift Invariance); detailed in *Affine Control Interpretation*.
- **Key Properties**:
  - Foundational assumption for the control-affine form $\dot{x} = f(x) + g(x)u$.
  - Enables clean causal decomposition: inputs do not affect drift field.
  - Approximately valid in high-speed regimes where muscle stiffness effects are second-order (validated in *Skeletal Baseline*).
  - Violated near impact if impedance modulation fundamentally alters constraint structure; handled by switched affine systems.

---

### **Effective Plant**
- **Symbol/Abbreviation**: Often written $f_{\text{eff}}(x)$, $K_{\text{eff}}$; context-dependent.
- **Definition**: In the context of constraint collapse, the effective impedance and force-generation dynamics during high-stiffness phases. Mathematically: the system parameters ($M$, $K$, etc.) and the resulting drift field when impedance is modulated. Can be understood as a mode in a switched affine system.
- **Intuitive Explanation**: The golfer's "effective" mechanical structure changes near impact. Looser during the backswing, stiffer (more "effective" at force transmission) near impact.
- **First Introduced**: *Intentional Constraint Collapse* (Section 8); referenced in *Drift-Control Ratio* (impedance stiffening critique response).
- **Key Properties**:
  - Time-varying within impact zone; fixed outside.
  - Achieved through neuromuscular co-contraction.
  - Different "Effective Plant" ⟹ different ZTCF (mode-dependent ZTCF).
  - Provides control reserve: high impedance suppresses destabilizing perturbations without performing external work.

---

### **Hybrid Automaton**
- **Symbol/Abbreviation**: (diagram-based notation in control theory; no single symbol)
- **Definition**: A dynamical system with both continuous-time dynamics and discrete mode transitions. Formally: a tuple $(Q, X, \Sigma, \mathcal{F}, \mathcal{E}, G, R)$ where $Q$ is a finite set of modes, $X$ is the continuous state space, dynamics $\dot{x} = f_q(x)$ evolve within mode $q$, and guards $G$ and resets $R$ govern discrete transitions $\sigma: q \to q'$.
- **Intuitive Explanation**: A system that switches between different regimes. Like a car with gears: it obeys continuous physics in each gear, but you can switch gears discretely.
- **First Introduced**: *Intentional Constraint Collapse* (Section 8); control theory formalism.
- **Key Properties**:
  - Preserves affine structure within each mode: $\dot{x} = f_q(x) + g_q(x)u$.
  - Mode transitions driven by discrete controller (motor planning system).
  - Allows drift field and input matrix to change between modes without violating drift invariance locally.
  - Used to model swing with two modes: free motion and impact-preparation stiffening.

---

### **Impedance Modulation**
- **Symbol/Abbreviation**: $\Delta K(t)$, $K_{\text{eff}}(t)$; "stiffness modulation"
- **Definition**: The continuous time-varying adjustment of mechanical impedance (stiffness and damping) via neuromuscular control. Achieved through co-contraction of antagonist muscles; does not involve geometric constraint changes.
- **Intuitive Explanation**: Making your muscles "tense up" (more stiff and damped) to resist motion in certain directions, without locking bones together.
- **First Introduced**: *Intentional Constraint Collapse* (throughout); implicit in *Impedance Control* references.
- **Key Properties**:
  - Energetically costly (metabolic co-contraction cost).
  - Non-geometric: Jacobian rank does not change.
  - Can be selective (directional) and transient (time-limited).
  - Creates "virtual constraints" that mimic kinematic constraint behavior.

---

### **Input Matrix** / **Actuation Matrix**
- **Symbol/Abbreviation**: $g(x)$ or $G(x)$; sometimes $B(x)$
- **Definition**: The state-dependent matrix that couples generalized torques/forces $u$ to state acceleration: $\dot{x} = f(x) + g(x)u$. For a Lagrangian system: $g(x) = [0; M^{-1}(q)]$ (zero for velocity component, mass-inverse for acceleration component).
- **Intuitive Explanation**: "How effective are your muscles at a given posture?" High effectiveness means small torques produce large accelerations. Low effectiveness means you're in a weak mechanical position.
- **First Introduced**: *Superposition in Affine Control Systems*; fundamental to all articles.
- **Key Properties**:
  - Columns are control vector fields; span the set of directions inputs can push the system.
  - State-dependent: effectiveness varies with joint angle and mass distribution.
  - Inversion gives "actuation deficiency": $g(x)^{-1}$ (or pseudo-inverse) tells you required torque for desired acceleration.

---

### **Lie Bracket** (Accessibility Context)
- **Symbol/Abbreviation**: $[f, g]$ or $[\cdot, \cdot]$
- **Definition**: A bilinear operation on vector fields measuring their non-commutativity: $[f,g](x) = (\nabla g(x))f(x) - (\nabla f(x))g(x)$. Components: $[f,g]_i = \sum_j (g_j \frac{\partial f_i}{\partial x_j} - f_j \frac{\partial g_i}{\partial x_j})$.
- **Intuitive Explanation**: "If you apply drift then control, do you end up at the same place as control then drift?" No ⟹ the bracket is nonzero ⟹ you can reach new directions by chaining operations.
- **First Introduced**: *Nonlinear Control Insights* (Lie Bracket Analysis); *Drift-Control Ratio* (Section 6.4).
- **Key Properties**:
  - Closed: $[\cdot,\cdot]$ is itself a vector field; iterated brackets generate accessibility distribution.
  - Lie bracket between drift and control fields: $[f,g]$ encodes secondary control authority.
  - Scales inversely with drift magnitude: $\|[f,g]\| / \|f\|$ shrinks as drift grows.

---

### **Snapshot Principle**
- **Symbol/Abbreviation**: (principle; no symbol)
- **Definition**: The mathematical fact that within a control-affine system, the instantaneous mapping from inputs to generalized forces (or accelerations) is *linear* at fixed state, even though the total dynamics are nonlinear. Formally: for fixed $x$, the map $u \mapsto g(x)u$ is linear, so superposition holds for forces/accelerations but not trajectories.
- **Intuitive Explanation**: "At any given instant, your muscle outputs combine linearly." But because the system's shape is changing, the overall trajectory is nonlinear and does not decompose.
- **First Introduced**: *Superposition in Affine Control Systems* (central theme)
- **Key Properties**:
  - Enables decomposition of motion into drift + control contributions.
  - Valid at each time slice but trajectories do not superpose.
  - Underpins Zero Torque Counterfactual (ZTCF) and Zero Velocity Counterfactual (ZVCF) baselines.

---

### **Stability-Optimality Duality**
- **Symbol/Abbreviation**: (principle; "duality")
- **Definition**: In optimal control of drift-dominated underactuated systems, stability constraints and optimality objectives are dual: stabilizing against disturbances is equivalent to minimizing the energy cost of corrective inputs. Formally: $\min_u \int \|u(t)\|^2 dt$ subject to trajectory stability yields a controller that maximizes $H(x,p)$ in a dual sense.
- **Intuitive Explanation**: "The most efficient way to swing is also the most stable way to swing." Fighting passive dynamics wastes energy; working with them saves energy.
- **First Introduced**: *Nonlinear Control Insights* (Optimal Control section); implicit in ZTCF/ZVCF analysis.
- **Key Properties**:
  - Arises in underactuated systems where drift dominates.
  - Suggests elite golfers exploit this duality naturally through skill.
  - Implies high-DCR regimes (where drift is huge) are also low-energy regimes if motion is ballistically committed.

---

### **State Space**
- **Symbol/Abbreviation**: $X$, $\mathbb{X}$; sometimes $(q, \dot{q})$
- **Definition**: The Cartesian product of configuration space and velocity space: $X = Q \times \dot{Q}$ where $q \in Q$ and $\dot{q} \in \dot{Q}$. For a system with $m$ DOF: $X = \mathbb{R}^m \times \mathbb{R}^m = \mathbb{R}^{2m}$.
- **Intuitive Explanation**: The complete description of a system's state right now: "Where am I and how fast am I moving?"
- **First Introduced**: Foundational to all dynamical systems analysis.
- **Key Properties**:
  - Evolution is a trajectory $x(t) = (q(t), \dot{q}(t))$ in state space.
  - Reachable set $\mathcal{R}(t; x_0) \subset X$ describes what states are attainable.
  - Tangent space $T_x X$ at each state defines direction of motion.

---

### **Tangent Hyperplane**
- **Symbol/Abbreviation**: $T_x S$ (tangent space to manifold $S$ at point $x$); sometimes written $T_x$
- **Definition**: In the context of nonlinear systems, the linear subspace spanned by the drift and control vector fields at a given state: $T_x = \mathrm{span}\{f(x), g(x)\}$. More formally: the tangent space to the reachable set at $x$.
- **Intuitive Explanation**: The "directions you can move" if you combine drift and control optimally at a given instant.
- **First Introduced**: *Tangent Hyperplanes* (article title/reference); implicit in control cone and accessibility distribution.
- **Key Properties**:
  - Dimension: $\dim(T_x) \leq m$ (number of DOF) but usually $\dim(T_x) < m$ due to underactuation.
  - Expands with control authority; shrinks as drift dominates.
  - Orthogonal to uncontrollable directions.

---

### **Tangent Space Exactness**
- **Symbol/Abbreviation**: (principle; "exactness" is a differential form concept)
- **Definition**: A differential geometry condition on control systems related to whether a one-form $\omega$ can be expressed as the exterior derivative of another form. For accessibility: exactness of certain distributions determines whether all states are reachable. (Technical: a form is exact if $d\omega = 0$ and $\omega = d\theta$ for some $\theta$.)
- **Intuitive Explanation**: Mathematical condition underlying "completeness" of controllability: if the tangent space is exact, you can reach any nearby state by chaining drift and control actions correctly.
- **First Introduced**: Future research directions; advanced control-theoretic tool.
- **Key Properties**: Related to Lie bracket integrability; enables reachability analysis beyond small-time local controllability.

---

### **Zero Torque Counterfactual** (ZTCF)
- **Symbol/Abbreviation**: $\mathrm{ZTCF}$; sometimes $x_{\text{ZTCF}}(t)$ for trajectory
- **Definition**: The trajectory the system would follow if all muscular torques were instantaneously set to zero ($u \equiv 0$) while preserving all other system properties (mass, stiffness, gravity, etc.). Formally: the solution to $\dot{x} = f(x)$ with initial conditions matching the actual swing's state at some reference time.
- **Intuitive Explanation**: "What if your muscles turned off right now?" The answer tells you how much of the remaining motion is pure physics versus what you're actively controlling.
- **First Introduced**: *Affine Control Interpretation of the Golf Swing* (Part II: Counterfactuals); foundational baseline in all comparative analyses.
- **Key Properties**:
  - Unique for a given initial state (governed by autonomous ODE).
  - Coordinate-independent: same physical motion in all coordinate systems.
  - Diverges from actual trajectory when control is large; converges when DCR is high (drift dominates).
  - Mode-dependent in hybrid systems: different ZTCF in free-motion vs. impact-preparation modes.
  - Valid as pedagogical and computational tool; physiologically interpretable as "passive skeletal dynamics."

---

### **Zero Velocity Counterfactual** (ZVCF)
- **Symbol/Abbreviation**: $\mathrm{ZVCF}$; sometimes $\tau_{\text{ZVCF}}(t)$ for torque required to maintain state
- **Definition**: The generalized torques required to maintain zero acceleration at a given state: setting $\ddot{q} = 0$ and solving $M(q)\ddot{q} + C(q,\dot{q})\dot{q} + G(q) = \tau$ yields $\tau_{\text{ZVCF}} = C(q,\dot{q})\dot{q} + G(q)$. Represents the "load" the system imposes at a given instant.
- **Intuitive Explanation**: "How hard do I have to hold this position right now?" The answer is the total passive force (gravity + momentum effects) that I must counteract.
- **First Introduced**: *Affine Control Interpretation of the Golf Swing* (Part II: Counterfactuals); used as a "state-dependent load cell."
- **Key Properties**:
  - Scales quadratically with velocity: $\|\tau_{\text{ZVCF}}\| \sim \mathcal{O}(\dot{q}^2)$ (Coriolis dominates).
  - Objective measure of dynamic load independent of what the golfer intends.
  - Allows quantification of "effective plant" during constraint collapse (high ZVCF ⟹ high passive load).
  - Inverse of control authority: $\alpha(t) = 1 / \mathrm{DCR}(t)$ relates to torque margin above ZVCF.

---

## 3. Acronyms and Abbreviations

| Acronym | Full Form | Context |
|---------|-----------|---------|
| **DCR** | Drift-Control Ratio | Ratio of passive to active force magnitudes; core metric of drift dominance |
| **ZTCF** | Zero Torque Counterfactual | Trajectory under $u=0$; passive baseline for force decomposition |
| **ZVCF** | Zero Velocity Counterfactual | Torques required for zero acceleration; dynamic load quantification |
| **DOF** | Degrees of Freedom | Number of independent coordinates ($\dim(q)$); golf swing typically 3-9 DOF depending on model |
| **COM** | Center of Mass | Point summarizing distributed mass; used in inverse dynamics |
| **EMG** | Electromyography | Direct muscle activation measurement; validates torque reconstructions |
| **GRF** | Ground Reaction Force | Force applied by ground to golfer; input to golfer-club system |
| **COP** | Center of Pressure | Point of application of GRF; determines moment arm for torque generation |
| **Inertia-weighted norm** | $\|\cdot\|_M = \sqrt{\mathbf{v}^\top M \mathbf{v}}$ | Preferred norm for DCR calculations; measures kinetic energy scale |
| **LMI** | Linear Matrix Inequality | Optimization tool for control synthesis; used in robust control analysis |
| **Lyapunov** | Lyapunov stability analysis | Framework for proving asymptotic stability; indirect application |

---

## 4. Cross-Reference Map

### **By Article: Primary Definitions and Heavy Usage**

#### **Superposition in Affine Control Systems**
Introduces and rigorously proves:
- **Affine Structure** ($\dot{x} = f(x) + g(x)u$)
- **Snapshot Principle**
- **Input Superposition** (in forces, not trajectories)
- **Drift** (with Newton-Euler and Lagrangian derivations)

Cross-references:
- Uses $f(x)$, $g(x)$, $M(q)$, $C(q,\dot{q})$, $G(q)$
- Establishes foundation for all subsequent articles

---

#### **Affine Control Interpretation of the Golf Swing (Part I)**
Central focus:
- **Zero Torque Counterfactual (ZTCF)**
- **Zero Velocity Counterfactual (ZVCF)**
- **Force Taxonomy** (decomposes measured forces into drift and input contributions)
- **Drift Invariance** (core assumption)

Cross-references:
- Depends on Superposition article
- Foundational for DCR and constraint collapse articles
- Defines conceptual framework for Parts II-V

---

#### **Drift-Control Ratio in the Golf Swing**
Detailed analysis of:
- **Drift-Control Ratio (DCR)**
- **Control Cone** (relativistic analogy)
- **Control Authority Collapse** (when DCR > 10)
- **Anisotropic Reachability** (pancake hypothesis)
- **Stability of Impact** (sensitivity to early-swing perturbations)

Cross-references:
- Uses ZTCF, ZVCF as baselines
- Applies Lie bracket theory (accessibility distribution)
- Validates DCR predictions using skeletal baseline

---

#### **Nonlinear Control Theory Insights**
Provides theoretical depth for:
- **Underactuation** and drift dominance
- **State-Dependent Effectiveness of Torques** ($g(x)$ analysis)
- **Lie Bracket** mechanics and control accessibility
- **Partial Feedback Linearization** (theoretical tool)
- **Reachability Analysis** (foundations)
- **Optimal Control** perspective (stability-optimality duality)

Cross-references:
- Synthesizes theory from Superposition and Affine Interpretation articles
- Provides rigorous justification for ZTCF uniqueness and coordinate invariance
- Connects to constraint collapse (hybrid automaton framing)

---

#### **Intentional Constraint Collapse at Impact**
Detailed development of:
- **Constraint Collapse** (definition, timing, mechanics)
- **Impedance Modulation** (co-contraction dynamics)
- **Internal Forces** (nullspace redundancy exploitation)
- **Effective Plant** (mode-dependent dynamics)
- **Hybrid Automaton** (switched affine system formalism)

Cross-references:
- Resolves drift invariance critique using hybrid systems
- Uses ZTCF as baseline for mode-specific analysis
- Connects to DCR analysis (temporal constraint from planar DCR)
- Leverages Control Cone concept (stiffening narrows cone)

---

### **By Concept: Which Articles Contain Detailed Treatment**

| Concept | Primary Article | Secondary References |
|---------|-----------------|----------------------|
| **Affine Structure** | Superposition; Affine Interpretation | Nonlinear Control, Constraint Collapse |
| **Control Cone** | Drift-Control Ratio | Nonlinear Control (accessibility) |
| **Constraint Collapse** | Constraint Collapse (entire article) | Drift-Control Ratio (temporal aspects), Affine Interpretation |
| **Drift** | Superposition, Affine Interpretation | All articles (foundational) |
| **Drift-Control Ratio (DCR)** | Drift-Control Ratio (entire article) | Constraint Collapse (timing), Nonlinear Control (reachability) |
| **Effective Plant** | Constraint Collapse | Drift-Control Ratio (critique response) |
| **Impedance Modulation** | Constraint Collapse | Nonlinear Control (feedback linearization analogy) |
| **Lie Bracket** | Nonlinear Control | Drift-Control Ratio (cone narrowing mechanism) |
| **Snapshot Principle** | Superposition | Nonlinear Control (superposition in underactuated systems) |
| **State-Dependent Effectiveness** | Nonlinear Control | Drift-Control Ratio (control authority scaling) |
| **Underactuation** | Nonlinear Control | All articles (pervasive theme) |
| **ZTCF, ZVCF** | Affine Interpretation | All articles (baselines and reference) |

---

### **Reading Order Recommendations**

1. **Foundations (Required):**
   - *Superposition in Affine Control Systems* → *Affine Control Interpretation (Part I)*
   - Establishes $\dot{x} = f(x) + g(x)u$ and ZTCF/ZVCF

2. **Drift Quantification:**
   - *Drift-Control Ratio in the Golf Swing*
   - Metrics and control cone concept

3. **Control Theory Context (Optional but Recommended):**
   - *Nonlinear Control Theory Insights*
   - Deepens understanding of reachability, Lie brackets, optimality

4. **Advanced Application:**
   - *Intentional Constraint Collapse at Impact*
   - Integrates hybrid systems, impedance, and timing

5. **Future Extensions:**
   - Papers on Skeletal Baseline (experimental validation)
   - Equipment design under affine formulation
   - Data-driven drift identification

---

## 5. Terminology Guidelines for Authors and Contributors

### **Precision Standards**

1. **"Drift" vs. "Passive Dynamics"**: Use interchangeably; both acceptable. Prefer "drift" when emphasizing mathematical form ($f(x)$) or control-theoretic context; "passive dynamics" when emphasizing biomechanical origin.

2. **"Control" vs. "Input" vs. "Torque"**:
   - **Control** = general term for intentional effort ($u$ or strategy)
   - **Input** = specific term for control signal $u(t)$
   - **Torque** = physical manifestation of control at joint level ($\tau = g(x)u$)

3. **"Drift Invariance"**: A property of the model, not a discovered law. Phrase as "We assume drift invariance..." or "The drift invariance property allows us to..."

4. **"Effective Plant"**: Use sparingly; reserve for high-impedance regimes near impact or when explicitly discussing mode-dependent dynamics. Avoid conflating with "actual plant."

5. **"Control Cone" vs. "Reachable Set"**:
   - Control cone = instantaneous tangent cone (infinitesimal time limit)
   - Reachable set = actual attainable states over finite time

6. **"Constraint Collapse" vs. "Stiffening"**:
   - "Constraint Collapse" emphasizes geometric / impedance perspective
   - "Stiffening" emphasizes mechanical effect
   - Use both for clarity; they are complementary

7. **Norm specification**: Always report which norm (Euclidean, inertia-weighted, etc.) is used for DCR or force magnitudes. Default is Euclidean unless otherwise noted.

### **Citation Format for Core Concepts**

When first introducing a concept, cite the defining article:

Example: "The Drift-Control Ratio (DCR) [Drift-Control Ratio in the Golf Swing] quantifies the dominance of passive dynamics..."

---

## 6. Index of All Defined Terms

**A:** Accessibility Distribution, Affine Structure, Anisotropic Reachability
**C:** Configuration Space, Constraint Collapse, Constraint Jacobian, Contraction Metric, Control Cone, Control-Affine System
**D:** Drift, Drift Invariance, Drift-Control Ratio
**E:** Effective Plant, Euler-Lagrange Equations
**G:** Generalized Coordinates, Generalized Torques
**H:** Hybrid Automaton
**I:** Impedance Modulation, Input Matrix, Input Superposition
**J:** Jacobian (Task), Jacobian (Constraint)
**K:** Kinetic Energy, Kinetic Energy Metric
**L:** Lagrangian Mechanics, Lie Bracket, Lyapunov Stability
**M:** Mass Matrix, Mechanical Impedance
**N:** Nonholonomic Constraint, Norm (Euclidean, Inertia-Weighted)
**O:** Optimal Control, Optimality-Stability Duality
**P:** Passive Dynamics, Phase Portrait, Potential Energy
**Q:** Quasi-Static Analysis
**R:** Reachable Set, Reachability Analysis
**S:** Snapshot Principle, Stability, State Space, State-Dependent Effectiveness, Switched System
**T:** Tangent Hyperplane, Tangent Space, Task Jacobian
**U:** Underactuation
**V:** Vector Field, Virtual Constraint
**Z:** Zero Torque Counterfactual (ZTCF), Zero Velocity Counterfactual (ZVCF)

---

## 7. Mathematical Notation Summary (Quick Reference)

### System Dynamics
- $\dot{x} = f(x) + g(x)u$ — Control-affine system
- $M(q)\ddot{q} + C(q,\dot{q})\dot{q} + G(q) = \tau$ — Lagrangian form
- $\dot{x} = f_\sigma(x) + g_\sigma(x)u$ — Hybrid (mode $\sigma$)

### Key Quantities
- $\mathrm{DCR}(t) = \frac{\|f_{\text{acc}}\|}{\|g_{\text{acc}}u\|}$ — Drift-Control Ratio
- $\tau_{\text{ZVCF}} = C\dot{q} + G$ — Zero Velocity Counterfactual torque
- $K_{\text{eff}} = K_0 + \Delta K_{\text{co-contraction}}$ — Effective impedance

### Reachability
- $\mathcal{R}(t; x_0)$ — Reachable set from $x_0$ at time $t$
- $\mathcal{V}(x) = \mathrm{span}\{g, [f,g], \ldots\}$ — Accessibility distribution
- $\mathcal{C}_c(x)$ — Control cone at state $x$

### Operators
- $[f,g]$ — Lie bracket
- $J_c = \partial \phi/\partial q$ — Constraint Jacobian
- $\Lambda_c = (J_c M^{-1} J_c^\top)^{-1}$ — Constraint-space inertia

---

## Document Information

- **Version**: 1.0
- **Created**: March 10, 2026
- **Scope**: AffineDrift framework articles and projects
- **Audience**: Researchers, students, interdisciplinary readers
- **Status**: Comprehensive reference; subject to updates as framework evolves

For additions, corrections, or clarifications, please contact the AffineDrift documentation team.
