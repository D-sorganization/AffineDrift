# Concept Map

- **Lie Group SE(3)**: The configuration space of rigid bodies (rotation + translation), forming a smooth manifold.
- **Twist ($\mathcal{V}$)**: An element of the Lie algebra $\mathfrak{se}(3)$ representing instantaneous motion (angular velocity + linear velocity) as a 6-vector.
- **Wrench ($\mathcal{F}$)**: An element of the dual space $\mathfrak{se}^*(3)$ representing generalized forces (torque + force) as a 6-vector.
- **Adjoint Map ($\mathrm{Ad}_g$)**: The linear operator mapping twists from one coordinate frame to another; its dual ($\mathrm{Ad}_g^*$) maps wrenches.
- **Spatial Inertia ($I_s$)**: A $6 \times 6$ symmetric positive-definite matrix generalizing mass and rotational inertia tensor for spatial arithmetic.
- **Product of Exponentials (PoE)**: A geometric formula for forward kinematics representing the end-effector configuration as a sequence of matrix exponentials of screw axes.
- **Reciprocal Screws**: Two screws whose virtual work product is zero, fundamental for defining kinematic constraints.
- **Chasles' Theorem**: States that any general rigid body displacement can be produced by a translation along an axis and a rotation about that same axis (a screw motion).

# Bibliography

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors: "Murray, R. M., Li, Z., & Sastry, S. S."
  year: 1994
  venue: "CRC Press"
  scholar_url: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters:

  - "screw theory"
  - "robotics"
  - "nonlinear control"
    concepts:
  - "product of exponentials"
  - "adjoint map"
  - "Lie brackets"
  - "Lagrangian dynamics"
    related_ids:
  - "lynch2017modern"
  - "featherstone2008rigid"
    references_out_ids:
  - "lynch2017modern"
  - "bullo2005geometric"
  - "selig2005geometric"

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors: "Lynch, K. M., & Park, F. C."
  year: 2017
  venue: "Cambridge University Press"
  scholar_url: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters:

  - "robotics"
  - "screw theory"
  - "education"
    concepts:
  - "twist"
  - "wrench"
  - "Lagrangian dynamics"
  - "configuration space"
    related_ids:
  - "murray1994mathematical"
  - "pinocchio_lib"
    references_out_ids:
  - "featherstone2008rigid"
  - "jain2011robot"

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors: "Featherstone, R."
  year: 2008
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters:

  - "multibody dynamics"
  - "screw theory"
  - "algorithms"
    concepts:
  - "spatial vectors"
  - "articulated body algorithm"
  - "recursive newton-euler"
  - "spatial inertia"
    related_ids:
  - "jain2011robot"
  - "pinocchio_lib"
    references_out_ids:
  - "jain2011robot"
  - "pinocchio_lib"

- id: ball1900treatise
  title: "A Treatise on the Theory of Screws"
  authors: "Ball, R. S."
  year: 1900
  venue: "Cambridge University Press"
  scholar_url: "https://scholar.google.com/scholar?q=A+Treatise+on+the+Theory+of+Screws+Ball"
  clusters:

  - "screw theory"
  - "mathematical physics"
  - "history"
    concepts:
  - "screw axis"
  - "reciprocal screws"
  - "cylindroid"
  - "virtual coefficient"
    related_ids:
  - "hunt1978kinematic"
  - "selig2005geometric"
    references_out_ids:
  - "hunt1978kinematic"

- id: selig2005geometric
  title: "Geometric Fundamentals of Robotics"
  authors: "Selig, J. M."
  year: 2005
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Geometric+Fundamentals+of+Robotics+Selig"
  clusters:

  - "robotics"
  - "geometry"
  - "screw theory"
    concepts:
  - "Klein quadric"
  - "Clifford algebra"
  - "Lie groups"
  - "Grassmannians"
    related_ids:
  - "ball1900treatise"
  - "murray1994mathematical"
    references_out_ids:
  - "davidson2004robots"

- id: jain2011robot
  title: "Robot and Multibody Dynamics: Analysis and Algorithms"
  authors: "Jain, A."
  year: 2011
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Robot+and+Multibody+Dynamics+Jain"
  clusters:

  - "multibody dynamics"
  - "algorithms"
  - "screw theory"
    concepts:
  - "operator algebra"
  - "mass matrix factorization"
  - "Kalman filter"
  - "spatial operators"
    related_ids:
  - "featherstone2008rigid"
    references_out_ids:
  - "featherstone2008rigid"

- id: hunt1978kinematic
  title: "Kinematic Geometry of Mechanisms"
  authors: "Hunt, K. H."
  year: 1978
  venue: "Clarendon Press"
  scholar_url: "https://scholar.google.com/scholar?q=Kinematic+Geometry+of+Mechanisms+Hunt"
  clusters:

  - "kinematics"
  - "screw theory"
  - "mechanisms"
    concepts:
  - "screw systems"
  - "line geometry"
  - "instantaneous invariants"
    related_ids:
  - "ball1900treatise"
  - "davidson2004robots"
    references_out_ids:
  - "ball1900treatise"

- id: brockett1984robotic
  title: "Robotic Manipulators and the Product of Exponentials Formula"
  authors: "Brockett, R. W."
  year: 1984
  venue: "Mathematical Theory of Networks and Systems"
  scholar_url: "https://scholar.google.com/scholar?q=Robotic+Manipulators+and+the+Product+of+Exponentials+Formula+Brockett"
  clusters:

  - "robotics"
  - "control theory"
  - "foundational"
    concepts:
  - "product of exponentials"
  - "Lie groups"
    related_ids:
  - "murray1994mathematical"
    references_out_ids:
  - "murray1994mathematical"

- id: bullo2005geometric
  title: "Geometric Control of Mechanical Systems"
  authors: "Bullo, F., & Lewis, A. D."
  year: 2005
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters:

  - "control theory"
  - "geometry"
  - "mechanics"
    concepts:
  - "affine connection"
  - "covariant derivative"
  - "nonholonomic constraints"
    related_ids:
  - "murray1994mathematical"
    references_out_ids:
  - "lynch2017modern"

- id: pinocchio_lib
  title: "Pinocchio: An Efficient and Versatile Rigid Body Dynamics Library"
  authors: "Carpentier, J., et al."
  year: 2019
  venue: "IEEE RAS International Conference on Humanoid Robots"
  scholar_url: "https://scholar.google.com/scholar?q=Pinocchio+Rigid+Body+Dynamics+Library"
  clusters:

  - "software"
  - "algorithms"
  - "robotics"
    concepts:
  - "spatial arithmetic"
  - "code generation"
  - "analytical derivatives"
    related_ids:
  - "featherstone2008rigid"
    references_out_ids:
  - "featherstone2008rigid"

- id: drake_lib
  title: "Drake: A Planning, Control, and Analysis Toolbox for Nonlinear Dynamical Systems"
  authors: "Tedrake, R., et al."
  year: 2019
  venue: "drake.mit.edu"
  scholar_url: "https://scholar.google.com/scholar?q=Drake+Model-Based+Design+and+Verification+for+Robotics"
  clusters:

  - "software"
  - "control theory"
  - "optimization"
    concepts:
  - "multibody plant"
  - "trajectory optimization"
  - "symbolic dynamics"
    related_ids:
  - "lynch2017modern"
    references_out_ids:
  - "underactuated_notes"

- id: davidson2004robots
  title: "Robots and Screw Theory: Applications of Kinematics and Statics to Robotics"
  authors: "Davidson, J. K., & Hunt, K. H."
  year: 2004
  venue: "Oxford University Press"
  scholar_url: "https://scholar.google.com/scholar?q=Robots+and+Screw+Theory+Davidson+Hunt"
  clusters:

  - "robotics"
  - "screw theory"
  - "kinematics"
    concepts:
  - "parallel mechanisms"
  - "singularity analysis"
  - "screw systems"
    related_ids:
  - "hunt1978kinematic"
    references_out_ids:
  - "selig2005geometric"

- id: park1995distance
  title: "Distance Metrics on the Rigid-Body Motions with Applications to Mechanism Design"
  authors: "Park, F. C."
  year: 1995
  venue: "ASME Journal of Mechanical Design"
  scholar_url: "https://scholar.google.com/scholar?q=Distance+Metrics+on+the+Rigid-Body+Motions+Park"
  clusters:

  - "geometry"
  - "design"
    concepts:
  - "Riemannian metric"
  - "bi-invariant metric"
  - "SE(3) geometry"
    related_ids:
  - "lynch2017modern"
    references_out_ids:
  - "bullo2005geometric"

- id: stramigioli2001modeling
  title: "Modeling and IPC Control of Interactive Mechanical Systems: A Coordinate-Free Approach"
  authors: "Stramigioli, S."
  year: 2001
  venue: "Springer"
  scholar_url: "https://scholar.google.com/scholar?q=Modeling+and+IPC+Control+of+Interactive+Mechanical+Systems+Stramigioli"
  clusters:

  - "control theory"
  - "port-hamiltonian"
  - "screw theory"
    concepts:
  - "port-hamiltonian systems"
  - "intrinsically passive control"
  - "spatial vectors"
    related_ids:
  - "bullo2005geometric"
    references_out_ids:
  - "duindam2009modeling"

- id: mason2001mechanics
  title: "Mechanics of Robotic Manipulation"
  authors: "Mason, M. T."
  year: 2001
  venue: "MIT Press"
  scholar_url: "https://scholar.google.com/scholar?q=Mechanics+of+Robotic+Manipulation+Mason"
  clusters:
  - "robotics"
  - "mechanics"
  - "manipulation"
    concepts:
  - "frictional contact"
  - "quasistatics"
  - "screw theory"
    related_ids:
  - "murray1994mathematical"
    references_out_ids:
  - "lynch2017modern"

# Reading Paths

## Fast ramp

1.  **Modern Robotics (Ch 3-4)**: The most accessible and comprehensive modern introduction to Screw Theory and $SE(3)$.
    - Ref: `lynch2017modern`
2.  **MLS94 (Ch 2)**: The classic text that popularized the Lie Group formulation in robotics; mathematically rigorous yet concise.
    - Ref: `murray1994mathematical`
3.  **Rigid Body Dynamics Algorithms (Ch 2)**: Defines "Spatial Vectors" (6D), the computational implementation of Screw Theory used in most physics engines.
    - Ref: `featherstone2008rigid`
4.  **Pinocchio Documentation**: See how these concepts translate into efficient C++/Python code.
    - Ref: `pinocchio_lib`
5.  **Mechanics of Robotic Manipulation (Ch 2)**: Excellent intuition on the geometry of twists and wrenches.
    - Ref: `mason2001mechanics`

## Deep technical

1.  **A Treatise on the Theory of Screws**: The original 1900 masterpiece by Sir Robert Ball; verbose but profoundly geometric.
    - Ref: `ball1900treatise`
2.  **Geometric Fundamentals of Robotics**: Connects Screw Theory to Clifford Algebras and the Klein Quadric.
    - Ref: `selig2005geometric`
3.  **Kinematic Geometry of Mechanisms**: The standard reference for screw systems in closed-chain mechanisms.
    - Ref: `hunt1978kinematic`
4.  **Geometric Control of Mechanical Systems**: A rigorous differential geometric treatment of mechanics using affine connections.
    - Ref: `bullo2005geometric`
5.  **Robotic Manipulators and PoE**: The seminal paper introducing the Product of Exponentials formula.
    - Ref: `brockett1984robotic`
6.  **Robots and Screw Theory**: A specialized text bridging classical kinematics and modern robotics.
    - Ref: `davidson2004robots`
7.  **Distance Metrics on SE(3)**: Deep dive into the metric properties of the rigid body manifold.
    - Ref: `park1995distance`
8.  **Modeling and IPC Control**: Advanced coordinate-free modeling using Port-Hamiltonian systems and spatial vectors.
    - Ref: `stramigioli2001modeling`

## Implementation

1.  **Pinocchio Library**: The state-of-the-art rigid body dynamics library using Featherstone's spatial algebra.
    - Ref: `pinocchio_lib`
2.  **Drake Toolbox**: A planning and control toolbox heavily utilizing the $SE(3)$ / Screw Theory formulation.
    - Ref: `drake_lib`
3.  **Rigid Body Dynamics Algorithms**: The book serves as the pseudocode manual for implementing your own physics engine.
    - Ref: `featherstone2008rigid`
4.  **Robot and Multibody Dynamics**: Focuses on the Operator Algebra approach, which is implementation-friendly for complex chains.
    - Ref: `jain2011robot`
5.  **Modern Robotics Code Library**: Python/MATLAB/C++ implementations of the algorithms in the book.
    - Ref: `lynch2017modern`
