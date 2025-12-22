# Bibliographic Analysis: Affine Control Interpretation of the Golf Swing

## A) Concept Map

*   **System Modeling**
    *   **Multibody Dynamics**: Modeling the golfer as a kinematic chain of rigid bodies.
    *   **Control-Affine Form**: $\dot{x} = f(x) + g(x)u$. Separating dynamics into drift (passive) and input (active) vector fields.
    *   **Drift Invariance**: The property that passive dynamics $f(x)$ are independent of instantaneous torque inputs $u$.
    *   **Flexible Multibody Dynamics**: Modeling the shaft using Assumed Modes Method (AMM) within the rigid-body framework.

*   **Force Decomposition**
    *   **Drift Dynamics**: Passive forces from inertia, Coriolis/centrifugal effects, gravity, and shaft elasticity.
    *   **Input Dynamics**: Active forces arising purely from generalized joint torques.
    *   **Counterfactuals**:
        *   **Zero Torque Counterfactual (ZTCF)**: Trajectory integration with $u=0$ to isolate passive drift evolution.
        *   **Zero Velocity Counterfactual (ZVCF)**: Instantaneous evaluation at $\dot{x}=0$ to isolate configuration-dependent loads (gravity, stiffness).

*   **Causal Analysis**
    *   **Mechanical Causality**: Attributing motion to physical mechanisms (inertia vs. torque) rather than neural intent.
    *   **Force Taxonomy**: Classification of total force into Configuration Drift, Velocity Drift, Input, and Mixed components.

*   **Key References**
    *   **Murray, Li, Sastry**: Mathematical robotics foundation.
    *   **Featherstone**: Efficient rigid body algorithms.
    *   **Nesbit / MacKenzie**: Golf biomechanics baselines (Inverse/Forward dynamics).
    *   **Todorov**: Optimal control in biological systems.

## B) Bibliography (YAML)

```yaml
- id: cochran1968search
  title: "The Search for the Perfect Swing"
  authors:
    - "Alastair J. Cochran"
    - "John Stobbs"
  year: 1968
  venue: "Heinemann"
  scholar_link: "https://scholar.google.com/scholar?q=The+Search+for+the+Perfect+Swing+Cochran"
  clusters: ["golf physics", "foundational"]
  concepts: ["double pendulum", "impact physics", "kinematics"]
  related_ids: ["jorgensen1993physics", "penner2003physics"]
  references_out_ids: ["jorgensen1993physics"]

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:
    - "Richard M. Murray"
    - "Zexiang Li"
    - "S. Shankar Sastry"
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "control theory", "multibody dynamics"]
  concepts: ["lagrangian dynamics", "manipulator equations", "control-affine systems"]
  related_ids: ["lynch2017modern", "spong2005robot"]
  references_out_ids: ["featherstone2008rigid", "isidori1995nonlinear"]

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

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["multibody dynamics", "simulation"]
  concepts: ["recursive algorithms", "spatial algebra", "articulated body algorithm"]
  related_ids: ["jain2010robot", "pinocchio_lib"]
  references_out_ids: ["jain2010robot", "pinocchio_lib"]

- id: nesbit2005three
  title: "A three dimensional kinematic and kinetic study of the golf swing"
  authors:
    - "Steven M. Nesbit"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=A+three+dimensional+kinematic+and+kinetic+study+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "inverse dynamics"]
  concepts: ["joint torques", "work and power", "full-body model"]
  related_ids: ["mackenzie2009three", "nesbit2014work"]
  references_out_ids: ["mackenzie2009three"]

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors:
    - "Sasho J. MacKenzie"
    - "Eric J. Sprigings"
  year: 2009
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=A+three-dimensional+forward+dynamics+model+of+the+golf+swing+MacKenzie"
  clusters: ["golf biomechanics", "forward dynamics"]
  concepts: ["forward simulation", "optimization", "flexible shaft"]
  related_ids: ["nesbit2005three", "olson2024twohand"]
  references_out_ids: ["olson2024twohand"]

- id: shabana2020dynamics
  title: "Dynamics of Multibody Systems"
  authors:
    - "Ahmed A. Shabana"
  year: 2020
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Multibody+Systems+Shabana"
  clusters: ["multibody dynamics", "flexible bodies"]
  concepts: ["assumed modes method", "floating frame of reference", "flexible multibody"]
  related_ids: ["simo1986dynamics"]
  references_out_ids: ["book1984recursive"]

- id: simo1986dynamics
  title: "On the dynamics of flexible beams under large overall motions—The plane case: Part I and II"
  authors:
    - "J. C. Simo"
    - "L. Vu-Quoc"
  year: 1986
  venue: "Journal of Applied Mechanics"
  scholar_link: "https://scholar.google.com/scholar?q=On+the+dynamics+of+flexible+beams+under+large+overall+motions+Simo"
  clusters: ["flexible bodies", "mechanics"]
  concepts: ["geometric stiffness", "large deformation", "beam theory"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: []

- id: todorov2004optimality
  title: "Optimality principles in sensorimotor control"
  authors:
    - "Emanuel Todorov"
  year: 2004
  venue: "Nature Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Optimality+principles+in+sensorimotor+control+Todorov"
  clusters: ["motor control", "neuroscience"]
  concepts: ["optimal control", "synergies", "minimal intervention"]
  related_ids: ["todorov2002optimal"]
  references_out_ids: []

- id: mcgeer1990passive
  title: "Passive Dynamic Walking"
  authors:
    - "Tad McGeer"
  year: 1990
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Passive+Dynamic+Walking+McGeer"
  clusters: ["passive dynamics", "robotics"]
  concepts: ["limit cycles", "passive stability", "energy efficiency"]
  related_ids: ["collins2005efficient"]
  references_out_ids: ["tedrake2023underactuated"]

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
  references_out_ids: ["khalil2002nonlinear"]

- id: sharp2009influence
  title: "The influence of the kick point on the performance of a golf club"
  authors:
    - "K. N. Sharp"
  year: 2009
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=The+influence+of+the+kick+point+on+the+performance+of+a+golf+club+Sharp"
  clusters: ["golf equipment", "shaft dynamics"]
  concepts: ["kick point", "shaft deflection", "launch conditions"]
  related_ids: ["penner2003physics"]
  references_out_ids: []

- id: olson2024twohand
  title: "Two Hand Golf Swing Model"
  authors:
    - "Dieter Olson"
  year: 2024
  venue: "MATLAB Central File Exchange"
  scholar_link: "https://scholar.google.com/scholar?q=Two+Hand+Golf+Swing+Model+Olson"
  clusters: ["simulation", "software"]
  concepts: ["forward dynamics", "simulink", "flexible shaft"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: []

- id: book1984recursive
  title: "Recursive Lagrangian dynamics of flexible manipulator arms"
  authors:
    - "Wayne J. Book"
  year: 1984
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Recursive+Lagrangian+dynamics+of+flexible+manipulator+arms+Book"
  clusters: ["flexible robotics", "dynamics"]
  concepts: ["recursive formulation", "flexible links", "lagrangian"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: []

- id: spong2005robot
  title: "Robot Modeling and Control"
  authors:
    - "Mark W. Spong"
    - "Seth Hutchinson"
    - "M. Vidyasagar"
  year: 2005
  venue: "Wiley"
  scholar_link: "https://scholar.google.com/scholar?q=Robot+Modeling+and+Control+Spong"
  clusters: ["robotics", "textbook"]
  concepts: ["manipulator dynamics", "control design", "euler-lagrange"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: khalil2002nonlinear
  title: "Nonlinear Systems"
  authors:
    - "Hassan K. Khalil"
  year: 2002
  venue: "Prentice Hall"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Systems+Khalil"
  clusters: ["control theory", "nonlinear analysis"]
  concepts: ["lyapunov stability", "singular perturbations", "passivity"]
  related_ids: ["isidori1995nonlinear"]
  references_out_ids: []

- id: penner2003physics
  title: "The physics of golf"
  authors:
    - "A. Raymond Penner"
  year: 2003
  venue: "Reports on Progress in Physics"
  scholar_link: "https://scholar.google.com/scholar?q=The+physics+of+golf+Penner"
  clusters: ["golf physics", "review"]
  concepts: ["aerodynamics", "impact", "swing dynamics"]
  related_ids: ["jorgensen1993physics"]
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

- id: drake_lib
  title: "Drake: Model-based design and verification for robotics"
  authors:
    - "Russ Tedrake"
    - "et al."
  year: 2019
  venue: "GitHub"
  scholar_link: "https://scholar.google.com/scholar?q=Drake+Model-based+design+and+verification+Tedrake"
  clusters: ["software", "control"]
  concepts: ["trajectory optimization", "symbolic dynamics", "verification"]
  related_ids: ["tedrake2023underactuated"]
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
  concepts: ["numerical integration", "optimization", "data analysis"]
  related_ids: []
  references_out_ids: []

- id: tedrake2023underactuated
  title: "Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation"
  authors:
    - "Russ Tedrake"
  year: 2023
  venue: "Course Notes"
  scholar_link: "https://scholar.google.com/scholar?q=Underactuated+Robotics+Tedrake"
  clusters: ["robotics", "control"]
  concepts: ["passive dynamics", "trajectory optimization", "limit cycles"]
  related_ids: ["mcgeer1990passive", "drake_lib"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (Conceptual Overview)
*Target: Grasp the core mechanical vs. biological distinction and the golf context.*
1.  **Cochran & Stobbs (1968)** - *The Search for the Perfect Swing* (`cochran1968search`). Canonical intro to golf physics.
2.  **Nesbit (2005)** - *A 3D kinematic and kinetic study* (`nesbit2005three`). Introduction to inverse dynamics in golf.
3.  **Spong, Hutchinson, Vidyasagar (2005)** - *Robot Modeling and Control* (`spong2005robot`). Accessible intro to Lagrangian dynamics.
4.  **McGeer (1990)** - *Passive Dynamic Walking* (`mcgeer1990passive`). Inspiration for "drift" as a useful driver of motion.
5.  **Todorov (2004)** - *Optimality principles* (`todorov2004optimality`). Understanding control cost vs. mechanical task.

### Path 2: Deep Technical (Theory & Derivation)
*Target: Understand the affine decomposition and flexible body math.*
1.  **Murray, Li, Sastry (1994)** - *Mathematical Introduction to Robotic Manipulation* (`murray1994mathematical`). The rigorous geometric foundation.
2.  **Isidori (1995)** - *Nonlinear Control Systems* (`isidori1995nonlinear`). Formal treatment of affine systems and drift vector fields.
3.  **Featherstone (2008)** - *Rigid Body Dynamics Algorithms* (`featherstone2008rigid`). Efficient computation of $M(q)$ and $C(q,\dot{q})$.
4.  **Shabana (2020)** - *Dynamics of Multibody Systems* (`shabana2020dynamics`). Flexible body formulations/AMM.
5.  **Book (1984)** - *Recursive Lagrangian dynamics of flexible manipulator arms* (`book1984recursive`). Classic recursive formulation for flexible chains.
6.  **Simo & Vu-Quoc (1986)** - *Dynamics of flexible beams* (`simo1986dynamics`). Advanced beam theory for the shaft.
7.  **MacKenzie & Sprigings (2009)** - *Forward dynamics model* (`mackenzie2009three`). Specific application to golf.
8.  **Lynch & Park (2017)** - *Modern Robotics* (`lynch2017modern`). Modern geometric treatment.

### Path 3: Implementation (Simulation & Analysis)
*Target: Reproducing the results or building a simulator.*
1.  **Olson (2024)** - *Two Hand Golf Swing Model* (`olson2024twohand`). Direct implementation reference.
2.  **Pinocchio Library** - (`pinocchio_lib`). Best open-source tool for the rigid backbone.
3.  **Drake (Tedrake)** - (`drake_lib`). For trajectory optimization extensions.
4.  **SciPy** - (`scipy_lib`). For ODE integration and signal processing.
5.  **Sharp (2009)** - *Influence of kick point* (`sharp2009influence`). Data/parameters for shaft modeling.
