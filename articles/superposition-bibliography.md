# Bibliographic Analysis: Superposition in Affine Control

## A) Concept Map

- **Mathematical Foundations**

  - **Control-Affine Systems**: $\dot{x} = f(x) + g(x)u$. Linearity of input mapping.
  - **Tangent Bundle Geometry**: State $x \in TQ$. Fiber-linearity of the tangent bundle.
  - **Superposition Principle**: Input contributions superpose linearly at a fixed state; trajectories do not.

- **Mechanics Formulations**

  - **Newton–Euler**: Force/Torque linearity ($F=ma$).
  - **Lagrangian**: Generalized forces $Q$ as linear mappings of physical forces.
  - **Screw Theory**: Spatial vectors (Twists/Wrenches). Linearity of wrench composition.
  - **Gauss's Principle of Least Constraint**: Variation of acceleration minimized under constraints.

- **Applications**

  - **Inverse Dynamics**: Decomposing torque into gravity, Coriolis, and task components.
  - **Induced Acceleration Analysis**: Biomechanical term for input-to-acceleration superposition.
  - **Gravity Compensation**: Feedforward cancellation of drift terms.
  - **Drift Invariance**: Theoretical justification for the Zero Torque Counterfactual (ZTCF).

- **Key References**
  - **Featherstone**: Spatial vector algebra and articulated body inertia.
  - **Murray, Li, Sastry**: Geometric control and Lagrangian mechanics.
  - **Zajac & Gordon**: Induced acceleration analysis in biomechanics.
  - **Udwadia & Kalaba**: Analytical dynamics and constraint forces.

## B) Bibliography (YAML)

```yaml
- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["robotics", "mechanics", "spatial algebra"]
  concepts:
    ["spatial vectors", "articulated body algorithm", "model-based control"]
  related_ids: ["jain2010robot", "pinocchio_lib"]
  references_out_ids: ["jain2010robot", "pinocchio_lib"]

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:
    - "Richard M. Murray"
    - "Zexiang Li"
    - "S. Shankar Sastry"
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "control theory"]
  concepts:
    ["lagrangian dynamics", "manipulator equations", "geometric mechanics"]
  related_ids: ["lynch2017modern", "bullo2004geometric"]
  references_out_ids: ["bullo2004geometric"]

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters: ["robotics", "mechanics"]
  concepts: ["screw theory", "dynamics", "configuration space"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: bullo2004geometric
  title: "Geometric Control of Mechanical Systems"
  authors:
    - "Francesco Bullo"
    - "Andrew D. Lewis"
  year: 2004
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["control theory", "geometric mechanics"]
  concepts: ["affine connection", "covariant derivative", "controllability"]
  related_ids: ["bloch2003nonholonomic"]
  references_out_ids: ["bloch2003nonholonomic"]

- id: zajac1989determining
  title: "Determining muscle's force and action in multi-articular movement"
  authors:
    - "Felix E. Zajac"
    - "M. E. Gordon"
  year: 1989
  venue: "Exercise and Sport Sciences Reviews"
  scholar_link: "https://scholar.google.com/scholar?q=Determining+muscle's+force+and+action+in+multi-articular+movement+Zajac"
  clusters: ["biomechanics", "motor control"]
  concepts: ["induced acceleration", "muscle synergy", "dynamic coupling"]
  related_ids: ["koike2019dynamic"]
  references_out_ids: ["koike2019dynamic"]

- id: udwadia1996analytical
  title: "Analytical Dynamics: A New Approach"
  authors:
    - "Firdaus E. Udwadia"
    - "Robert E. Kalaba"
  year: 1996
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Analytical+Dynamics+A+New+Approach+Udwadia"
  clusters: ["mechanics", "applied mathematics"]
  concepts: ["gauss principle", "constrained motion", "moore-penrose inverse"]
  related_ids: ["aghili2005unified"]
  references_out_ids: []

- id: jain2010robot
  title: "Robot and Multibody Dynamics: Analysis and Algorithms"
  authors:
    - "Abhinandan Jain"
  year: 2010
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Robot+and+Multibody+Dynamics+Jain"
  clusters: ["multibody dynamics", "robotics"]
  concepts:
    ["operator algebra", "mass matrix factorization", "spatial operators"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors:
    - "Alberto Isidori"
  year: 1995
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["control theory", "nonlinear systems"]
  concepts: ["affine systems", "lie brackets", "feedback linearization"]
  related_ids: ["khalil2002nonlinear"]
  references_out_ids: []

- id: koike2019dynamic
  title: "Dynamic contribution analysis of the golf swing"
  authors:
    - "Sekiya Koike"
    - "et al."
  year: 2019
  venue: "Sports Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamic+contribution+analysis+of+the+golf+swing+Koike"
  clusters: ["golf biomechanics", "induced acceleration"]
  concepts: ["contribution analysis", "equation of motion", "golf"]
  related_ids: ["zajac1989determining"]
  references_out_ids: []

- id: bloch2003nonholonomic
  title: "Nonholonomic Mechanics and Control"
  authors:
    - "Anthony M. Bloch"
  year: 2003
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonholonomic+Mechanics+and+Control+Bloch"
  clusters: ["mechanics", "control theory"]
  concepts: ["nonholonomic constraints", "lagrange-d'alembert", "momentum map"]
  related_ids: ["bullo2004geometric"]
  references_out_ids: []

- id: khatib1987unified
  title: "A unified approach for motion and force control of robot manipulators: The operational space formulation"
  authors:
    - "Oussama Khatib"
  year: 1987
  venue: "IEEE Journal of Robotics and Automation"
  scholar_link: "https://scholar.google.com/scholar?q=A+unified+approach+for+motion+and+force+control+Khatib"
  clusters: ["robotics", "control"]
  concepts:
    ["operational space", "dynamically consistent inverse", "projection"]
  related_ids: ["aghili2005unified"]
  references_out_ids: []

- id: aghili2005unified
  title: "A unified approach for inverse and direct dynamics of constrained multibody systems based on linear projection operator"
  authors:
    - "Farhad Aghili"
  year: 2005
  venue: "IEEE Transactions on Robotics"
  scholar_link: "https://scholar.google.com/scholar?q=A+unified+approach+for+inverse+and+direct+dynamics+constrained+Aghili"
  clusters: ["multibody dynamics", "constraints"]
  concepts: ["projection operator", "constrained dynamics", "null space"]
  related_ids: ["khatib1987unified", "udwadia1996analytical"]
  references_out_ids: []

- id: pinocchio_lib
  title: "Pinocchio: An efficient and rigid multi-body dynamics library"
  authors:
    - "Justin Carpentier"
    - "et al."
  year: 2019
  venue: "IEEE ICRA"
  scholar_link: "https://scholar.google.com/scholar?q=Pinocchio+efficient+rigid+multi-body+dynamics+library"
  clusters: ["software", "simulation"]
  concepts: ["c++", "rigid body algorithms", "spatial algebra"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []

- id: scipy_lib
  title: "SciPy 1.0: fundamental algorithms for scientific computing in Python"
  authors:
    - "Pauli Virtanen"
    - "et al."
  year: 2020
  venue: "Nature Methods"
  scholar_link: "https://scholar.google.com/scholar?q=SciPy+1.0+fundamental+algorithms"
  clusters: ["software", "scientific computing"]
  concepts: ["numerical integration", "optimization"]
  related_ids: []
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (Foundations of Superposition)

_Target: Understand why "forces add up" but "motions don't"._

1.  **Murray, Li, Sastry (1994)** - _Mathematical Introduction to Robotic Manipulation_ (`murray1994mathematical`). Chapter 6 on Dynamics.
2.  **Featherstone (2008)** - _Rigid Body Dynamics Algorithms_ (`featherstone2008rigid`). Chapter 3 on Spatial Vectors.
3.  **Lynch & Park (2017)** - _Modern Robotics_ (`lynch2017modern`). Chapter 8 on Dynamics of Open Chains.
4.  **Zajac & Gordon (1989)** - _Determining muscle's force..._ (`zajac1989determining`). The classic biomechanics "induced acceleration" paper.
5.  **Koike et al. (2019)** - _Dynamic contribution analysis of the golf swing_ (`koike2019dynamic`). Direct application to golf.

### Path 2: Deep Technical (Geometric & Algebraic Structure)

_Target: Master the fiber-linear structure and spatial operator algebra._

1.  **Bullo & Lewis (2004)** - _Geometric Control of Mechanical Systems_ (`bullo2004geometric`). Rigorous treatment of affine connections.
2.  **Jain (2010)** - _Robot and Multibody Dynamics_ (`jain2010robot`). Operator algebra showing explicit matrix factorizations.
3.  **Udwadia & Kalaba (1996)** - _Analytical Dynamics_ (`udwadia1996analytical`). Gauss's principle and the explicit form of constraint forces.
4.  **Isidori (1995)** - _Nonlinear Control Systems_ (`isidori1995nonlinear`). The control-theoretic view of affine systems.
5.  **Khatib (1987)** - _Operational Space Formulation_ (`khatib1987unified`). Projection matrices and dynamic consistency.
6.  **Aghili (2005)** - _Unified Approach for Constrained Systems_ (`aghili2005unified`). Null-space projections for closed loops.

### Path 3: Implementation (Computation)

_Target: Compute these terms numerically._

1.  **Pinocchio Library** (`pinocchio_lib`). Use `computeAbacom()` or `rnea()` to isolate terms.
2.  **Featherstone (2008)** (`featherstone2008rigid`). Pseudo-code for RNEA and CRBA.
3.  **SciPy** (`scipy_lib`). For ODE solvers `solve_ivp` to integrate the drift field.
4.  **Olson (2024)** (`olson2024twohand`). Example of Simulink implementation (referenced in broader project).
