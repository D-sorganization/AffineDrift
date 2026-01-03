# Bibliography Data: Null Space of the Constraint Jacobian

## A) Concept Map

- **Multibody Dynamics**

  - **Differential-Algebraic Equations (DAEs)**: Systems described by differential equations constrained by algebraic equations (Index-3).
  - **Lagrange Multipliers**: ($\lambda$) Forces required to enforce kinematic constraints.
  - **Constraint Jacobian**: ($J_c$) The mapping from generalized velocities to constraint violation rates.

- **Geometric Mechanics**

  - **Null Space Projector**: ($P$) Operator that separates forces into motion-inducing and constraint-absorbing components.
  - **Tangent Bundle**: ($T\mathcal{Q}$) The state space of permissible velocities at a given configuration.
  - **Riemannian Manifold**: The configuration space equipped with the mass metric.

- **Control Theory**

  - **Control-Affine Systems**: Formulating the constrained dynamics as $\dot{x} = f(x) + g(x)u$.
  - **Drift Vector Field**: The natural evolution of the system (passive dynamics) projected onto the feasible manifold.
  - **Controllability**: The ability to steer the system using available inputs within the null space.

- **Computational Methods**
  - **SVD / QR Decomposition**: Numerical techniques for computing the null space basis.
  - **Coordinate Reduction**: Transforming DAEs into ODEs using minimal coordinates ($\dot{z}$).

## B) Bibliography (YAML)

```yaml
- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:
    - "Richard M. Murray"
    - "Zexiang Li"
    - "S. Shankar Sastry"
  year: 1994
  venue: "CRC Press"
  scholar_url: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "geometric mechanics", "control"]
  concepts: ["constraints", "lagrange multipliers", "holonomic systems"]
  related_ids: ["lynch2017modern", "siciliano2016springer"]
  references_out_ids: ["lynch2017modern", "bloch2003nonholonomic"]

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["multibody dynamics", "algorithms"]
  concepts: ["recursive algorithms", "constraints", "spatial algebra"]
  related_ids: ["murray1994mathematical", "aghili2005unified"]
  references_out_ids: ["aghili2005unified", "pinocchio_lib"]

- id: udwadia2002general
  title: "What is the general form of the explicit equations of motion for constrained mechanical systems?"
  authors:
    - "Firdaus E. Udwadia"
    - "Robert E. Kalaba"
  year: 2002
  venue: "Journal of Applied Mechanics"
  scholar_url: "https://scholar.google.com/scholar?q=general+form+explicit+equations+motion+constrained+mechanical+systems+Udwadia"
  clusters: ["constrained dynamics", "analytical mechanics"]
  concepts:
    ["explicit equation of motion", "moore-penrose inverse", "gauss principle"]
  related_ids: ["blajer1997geometric"]
  references_out_ids: []

- id: blajer1997geometric
  title: "A geometric unification of constrained system dynamics"
  authors:
    - "Wojciech Blajer"
  year: 1997
  venue: "Multibody System Dynamics"
  scholar_url: "https://scholar.google.com/scholar?q=A+geometric+unification+of+constrained+system+dynamics+Blajer"
  clusters: ["constrained dynamics", "geometric mechanics"]
  concepts: ["projection method", "null space", "maggi equations"]
  related_ids: ["aghili2005unified"]
  references_out_ids: ["udwadia2002general"]

- id: nesbit2005three
  title: "A three dimensional kinematic and kinetic study of the golf swing"
  authors:
    - "Steven M. Nesbit"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_url: "https://scholar.google.com/scholar?q=A+three+dimensional+kinematic+and+kinetic+study+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "inverse dynamics"]
  concepts: ["full body model", "joint torques", "closed chain"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: ["mackenzie2009three"]

- id: aghili2005unified
  title: "A unified approach for inverse and forward dynamics of constrained systems and their application in simulation and control"
  authors:
    - "Farhad Aghili"
  year: 2005
  venue: "IEEE Transactions on Robotics"
  scholar_url: "https://scholar.google.com/scholar?q=unified+approach+inverse+forward+dynamics+constrained+systems+Aghili"
  clusters: ["robotics", "constrained dynamics"]
  concepts: ["projection matrix", "constraint stabilization", "closed-loop"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: ["siciliano1990kinematic"]

- id: khatib1987unified
  title: "A unified approach for motion and force control of robot manipulators: The operational space formulation"
  authors:
    - "Oussama Khatib"
  year: 1987
  venue: "IEEE Journal on Robotics and Automation"
  scholar_url: "https://scholar.google.com/scholar?q=unified+approach+motion+force+control+robot+manipulators+Khatib"
  clusters: ["robotics", "control"]
  concepts: ["operational space", "null space projection", "redundancy"]
  related_ids: ["siciliano1990kinematic"]
  references_out_ids: ["siciliano1990kinematic"]

- id: nakamura1991advanced
  title: "Advanced Robotics: Redundancy and Optimization"
  authors:
    - "Yoshihiko Nakamura"
  year: 1991
  venue: "Addison-Wesley"
  scholar_url: "https://scholar.google.com/scholar?q=Advanced+Robotics+Redundancy+and+Optimization+Nakamura"
  clusters: ["robotics", "optimization"]
  concepts: ["redundancy", "null space", "singularity"]
  related_ids: ["khatib1987unified"]
  references_out_ids: []

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors:
    - "Alberto Isidori"
  year: 1995
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["nonlinear control", "mathematics"]
  concepts: ["zero dynamics", "geometric control", "invariant distributions"]
  related_ids: ["bloch2003nonholonomic"]
  references_out_ids: []

- id: bloch2003nonholonomic
  title: "Nonholonomic Mechanics and Control"
  authors:
    - "Anthony M. Bloch"
  year: 2003
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Nonholonomic+Mechanics+and+Control+Bloch"
  clusters: ["geometric mechanics", "nonholonomic systems"]
  concepts: ["lagrangian reduction", "constraints", "control theory"]
  related_ids: ["bullo2004geometric"]
  references_out_ids: ["bullo2004geometric"]

- id: siciliano1990kinematic
  title: "Kinematic control of redundant robot manipulators: A tutorial"
  authors:
    - "Bruno Siciliano"
  year: 1990
  venue: "Journal of Intelligent and Robotic Systems"
  scholar_url: "https://scholar.google.com/scholar?q=Kinematic+control+of+redundant+robot+manipulators+Siciliano"
  clusters: ["robotics", "tutorial"]
  concepts: ["redundancy resolution", "null space", "pseudo-inverse"]
  related_ids: ["khatib1987unified"]
  references_out_ids: []

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_url: "https://scholar.google.com/scholar?q=Modern+Robotics+Mechanics+Planning+and+Control+Lynch"
  clusters: ["robotics", "textbook"]
  concepts: ["screw theory", "lagrangian dynamics", "constraints"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: golub2013matrix
  title: "Matrix Computations"
  authors:
    - "Gene H. Golub"
    - "Charles F. Van Loan"
  year: 2013
  venue: "Johns Hopkins University Press"
  scholar_url: "https://scholar.google.com/scholar?q=Matrix+Computations+Golub"
  clusters: ["numerical analysis", "mathematics"]
  concepts: ["svd", "qr decomposition", "least squares"]
  related_ids: []
  references_out_ids: []

- id: siciliano2016springer
  title: "Springer Handbook of Robotics"
  authors:
    - "Bruno Siciliano"
    - "Oussama Khatib"
  year: 2016
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Springer+Handbook+of+Robotics+Siciliano"
  clusters: ["robotics", "reference"]
  concepts: ["dynamics", "control", "manipulation"]
  related_ids: ["khatib1987unified"]
  references_out_ids: []

- id: bullo2004geometric
  title: "Geometric Control of Mechanical Systems"
  authors:
    - "Francesco Bullo"
    - "Andrew D. Lewis"
  year: 2004
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["geometric control", "mechanics"]
  concepts: ["affine connection", "covariant derivative", "controllability"]
  related_ids: ["bloch2003nonholonomic"]
  references_out_ids: []

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors:
    - "Sasho J. MacKenzie"
    - "Eric J. Sprigings"
  year: 2009
  venue: "Sports Engineering"
  scholar_url: "https://scholar.google.com/scholar?q=A+three-dimensional+forward+dynamics+model+of+the+golf+swing+MacKenzie"
  clusters: ["golf biomechanics", "forward dynamics"]
  concepts: ["simulation", "flexible shaft", "optimization"]
  related_ids: ["nesbit2005three"]
  references_out_ids: []

- id: pinocchio_lib
  title: "Pinocchio: An efficient and rigid multi-body dynamics library"
  authors:
    - "Justin Carpentier"
    - "et al."
  year: 2019
  venue: "IEEE International Conference on Robotics and Automation (ICRA)"
  scholar_url: "https://scholar.google.com/scholar?q=Pinocchio+efficient+rigid+multi-body+dynamics+library"
  clusters: ["software", "implementation", "multibody dynamics"]
  concepts: ["c++", "python", "spatial algebra"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (Conceptual Overview)

_Target: Understand why the Null Space matters for golf biomechanics._

1.  **Murray, Li, Sastry (1994)** (Chapter 6) - Introduction to constrained dynamics.
2.  **Nesbit (2005)** - Applied constraints in a full-body golf model.
3.  **Siciliano (1990)** - Tutorial on using the null space for redundancy resolution (e.g., separating "swinging" from "posture").
4.  **Featherstone (2008)** (Chapter 8) - Efficient algorithms for closed-loop systems.
5.  **Lynch & Park (2017)** - Modern perspective on constraints and loop closures.

### Path 2: Deep Technical (Rigorous Derivation)

_Target: Master the projection operators and differential geometry._

1.  **Udwadia & Kalaba (2002)** - The explicit closed-form solution for constrained motion ($M\ddot{q} = \tau + \tau_c$).
2.  **Blajer (1997)** - Unified geometric framework for eliminating Lagrange multipliers.
3.  **Aghili (2005)** - Comprehensive treatment of inverse/forward dynamics for closed chains.
4.  **Khatib (1987)** - The Operational Space Formulation (pioneering null space control).
5.  **Bloch (2003)** - Nonholonomic mechanics (advanced geometric view).
6.  **Bullo & Lewis (2004)** - Rigorous differential geometric control theory.
7.  **Isidori (1995)** - Nonlinear control systems and zero dynamics.
8.  **Nakamura (1991)** - Optimization of redundant manipulators via null space.

### Path 3: Implementation (Solvers & Simulation)

_Target: Writing the code._

1.  **Golub & Van Loan (2013)** - Implementation of SVD and QR for stable null space computation.
2.  **Pinocchio Library** - State-of-the-art C++/Python library handling constrained dynamics (using proximal formulations).
3.  **MacKenzie (2009)** - Reference implementation for forward dynamics of the golf swing.
4.  **SciPy.linalg** - Documentation for `null_space`, `svd`, and `qr` in Python.
5.  **Drake (Tedrake)** - Advanced constraint handling for trajectory optimization.
