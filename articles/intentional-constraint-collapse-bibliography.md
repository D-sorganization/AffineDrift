# Intentional Constraint Collapse at Impact
# Bibliography

## Concept Map

- **Constraint Jacobian**: The linear mapping between joint velocities and constraint violations.
- **Nullspace**: The subspace of joint configurations or velocities that do not affect the primary task (clubhead motion).
- **Impedance Control**: Regulating the dynamic relationship between force and motion (stiffness/damping).
- **Redundancy**: Having more degrees of freedom than required for the task.
- **Anisotropy**: Direction-dependent properties (e.g., stiff in one direction, compliant in another).

## References

bibliography:
  - id: hogan1985
    title: "The mechanics of multi-joint posture and movement control"
    authors: "Hogan, N."
    year: 1985
    venue: "Biological Cybernetics"
    scholar_link: "https://scholar.google.com/scholar?q=Hogan+mechanics+multi-joint+posture"
    clusters: ["motor control", "impedance"]
    concepts: ["impedance control", "muscle mechanics", "stability"]
    related_ids: ["latash2010"]
    references_out_ids: []

  - id: latash2010
    title: "Neurophysiological Basis of Motor Control"
    authors: "Latash, M. L."
    year: 2010
    venue: "Human Kinetics"
    scholar_link: "https://scholar.google.com/scholar?q=Latash+Neurophysiological+Basis+Motor+Control"
    clusters: ["motor control", "neuroscience"]
    concepts: ["synergies", "uncontrolled manifold", "redundancy"]
    related_ids: ["hogan1985"]
    references_out_ids: []

  - id: yoshikawa1990
    title: "Foundations of Robotics: Analysis and Control"
    authors: "Yoshikawa, T."
    year: 1990
    venue: "MIT Press"
    scholar_link: "https://scholar.google.com/scholar?q=Yoshikawa+Foundations+of+Robotics"
    clusters: ["robotics", "manipulability"]
    concepts: ["redundancy", "manipulability ellipsoid", "dynamics"]
    related_ids: ["murray1994mathematical"]
    references_out_ids: []

  - id: murray1994mathematical
    title: "A Mathematical Introduction to Robotic Manipulation"
    authors: "Murray, R. M., Li, Z., & Sastry, S. S."
    year: 1994
    venue: "CRC Press"
    scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
    clusters: ["robotics", "math"]
    concepts: ["lagrangian dynamics", "constraints", "nullspace"]
    related_ids: ["yoshikawa1990"]
    references_out_ids: []

  - id: khatib1987unified
    title: "A unified approach for motion and force control of robot manipulators"
    authors: "Khatib, O."
    year: 1987
    venue: "IEEE Journal of Robotics and Automation"
    scholar_link: "https://scholar.google.com/scholar?q=Khatib+unified+approach+motion+force+control"
    clusters: ["robotics", "control"]
    concepts: ["operational space", "force control", "decoupling"]
    related_ids: ["hogan1985"]
    references_out_ids: []

  - id: bernstein1967coordination
    title: "The Co-ordination and Regulation of Movements"
    authors: "Bernstein, N. A."
    year: 1967
    venue: "Pergamon Press"
    scholar_link: "https://scholar.google.com/scholar?q=Bernstein+Coordination+Regulation+Movements"
    clusters: ["motor control", "classic"]
    concepts: ["degrees of freedom problem", "coordination", "variability"]
    related_ids: ["latash2010"]
    references_out_ids: []

  - id: mackenzie2009three
    title: "A three-dimensional forward dynamics model of the golf swing"
    authors: "MacKenzie, S. J., & Sprigings, E. J."
    year: 2009
    venue: "Sports Engineering"
    scholar_link: "https://scholar.google.com/scholar?q=MacKenzie+Sprigings+2009+golf+swing"
    clusters: ["golf", "simulation"]
    concepts: ["forward dynamics", "muscle torque", "kinematics"]
    related_ids: ["nesbit2005three"]
    references_out_ids: []

  - id: nesbit2005three
    title: "A three dimensional kinematic and kinetic study of the golf swing"
    authors: "Nesbit, S. M."
    year: 2005
    venue: "Journal of Sports Science and Medicine"
    scholar_link: "https://scholar.google.com/scholar?q=Nesbit+2005+golf+swing+kinematic+kinetic"
    clusters: ["golf", "biomechanics"]
    concepts: ["inverse dynamics", "joint work", "energy"]
    related_ids: ["mackenzie2009three"]
    references_out_ids: []

  - id: featherstone2008rigid
    title: "Rigid Body Dynamics Algorithms"
    authors: "Featherstone, R."
    year: 2008
    venue: "Springer"
    scholar_link: "https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms"
    clusters: ["robotics", "simulation"]
    concepts: ["spatial algebra", "recursive algorithms", "constraints"]
    related_ids: ["yoshikawa1990"]
    references_out_ids: []

  - id: todorov2004optimality
    title: "Optimality principles in sensorimotor control"
    authors: "Todorov, E."
    year: 2004
    venue: "Nature Neuroscience"
    scholar_link: "https://scholar.google.com/scholar?q=Todorov+optimality+principles+sensorimotor+control"
    clusters: ["motor control", "optimization"]
    concepts: ["optimal control", "minimal intervention", "feedback"]
    related_ids: ["hogan1985"]
    references_out_ids: []

  - id: siciliano1990kinematic
    title: "Kinematic Control of Redundant Robot Manipulators: A Tutorial"
    authors: "Siciliano, B."
    year: 1990
    venue: "Journal of Intelligent and Robotic Systems"
    scholar_link: "https://scholar.google.com/scholar?q=Siciliano+Kinematic+Control+Redundant"
    clusters: ["robotics", "redundancy"]
    concepts: ["redundancy resolution", "pseudoinverse", "nullspace"]
    related_ids: ["yoshikawa1990"]
    references_out_ids: []

## Reading Paths

### Fast ramp (Start here)
1.  [hogan1985] - Foundational text on impedance control in biological systems, explaining how stiffness is modulated.
2.  [mackenzie2009three] - Key golf-specific forward dynamics model to understand the baseline system.
3.  [latash2010] - Introduction to the concept of synergies and redundancy in human movement.
4.  [nesbit2005three] - Empirical background on forces and torques in the golf swing.
5.  [todorov2004optimality] - Connects control theory to biological optimality, relevant for "intentional" collapse.

### Deep technical (The math)
1.  [yoshikawa1990] - Standard reference for redundancy, manipulability ellipsoids, and dynamic manipulability.
2.  [murray1994mathematical] - Rigorous mathematical treatment of constraints, Lagrangians, and nullspaces.
3.  [khatib1987unified] - The operational space formulation, crucial for understanding task-space vs. joint-space control.
4.  [featherstone2008rigid] - Essential for the efficient computation of dynamics in constrained systems.
5.  [siciliano1990kinematic] - Tutorial on redundancy resolution, directly applicable to the nullspace discussion.
6.  [isidori1995nonlinear] - (From general list) Background on affine control systems structure.
7.  [shabana2020dynamics] - (From general list) For understanding flexible body dynamics if expanding on shaft effects.
8.  [lynch2017modern] - (From general list) Modern geometric approach to robotics dynamics.

### Implementation (How to simulate)
1.  [latash2010] - Detailed discussion on muscle synergies and redundancy, useful for biological plausibility.
2.  [featherstone2008rigid] - Algorithms for implementing the constraint dynamics in simulation.
3.  [mackenzie2009three] - Specific parameters and model structure for the golf swing.
4.  [pinocchio_lib] - (From general list) Library for rigid body dynamics implementation.
5.  [drake_lib] - (From general list) Tool for trajectory optimization and control simulation.
6.  [scipy_lib] - (From general list) For numerical integration and optimization routines.
