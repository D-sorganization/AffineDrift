# Bibliographic Analysis: Affine Control Interpretation of the Golf Swing — Part 4

## A) Concept Map

*   **Mathematical Physics**
    *   **Lagrangian Mechanics**: Variational derivation ($\delta \int L dt = 0$) of equations of motion.
    *   **Euler-Lagrange Equations**: $\frac{d}{dt}(\frac{\partial L}{\partial \dot{q}}) - \frac{\partial L}{\partial q} = \tau$.
    *   **Configuration Manifold**: Treating the golfer-club system as a point on a manifold $Q$.

*   **Flexible Multibody Dynamics**
    *   **Assumed Modes Method (AMM)**: Discretizing continuous shaft deformation into finite modal coordinates $\eta$.
    *   **Euler-Bernoulli Beam Theory**: Modeling the shaft stiffness and mass distribution.
    *   **Rigid-Flexible Coupling**: Inertia matrix blocks ($M_{rf}, M_{fr}$) describing energy transfer between body and shaft.
    *   **Geometric Stiffness**: Effects arising from high-speed rotation (centrifugal stiffening).

*   **Control Theory**
    *   **Control-Affine Form**: $\dot{x} = f(x) + g(x)u$.
    *   **Drift Invariance**: The property that $f(x)$ encapsulates all passive dynamics (gravity, elasticity, Coriolis) and is independent of $u$.
    *   **Underactuation**: The condition where the dimension of inputs $u$ is less than the dimension of the configuration space (due to the passive shaft).
    *   **Input-Output Decoupling**: Separation of active torque effects from passive drift.

## B) Bibliography (YAML)

```yaml
- id: shabana2020dynamics
  title: "Dynamics of Multibody Systems"
  authors:
    - "Ahmed A. Shabana"
  year: 2020
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Multibody+Systems+Shabana"
  clusters: ["multibody dynamics", "flexible bodies"]
  concepts: ["floating frame of reference", "finite element method", "flexible multibody"]
  related_ids: ["simo1986dynamics", "book1984recursive"]
  references_out_ids: []

- id: meirovitch2001fundamentals
  title: "Fundamentals of Vibrations"
  authors:
    - "Leonard Meirovitch"
  year: 2001
  venue: "McGraw-Hill"
  scholar_link: "https://scholar.google.com/scholar?q=Fundamentals+of+Vibrations+Meirovitch"
  clusters: ["vibrations", "structural dynamics"]
  concepts: ["modal analysis", "euler-bernoulli beam", "lagrangian dynamics"]
  related_ids: ["clough1993dynamics"]
  references_out_ids: []

- id: simo1986dynamics
  title: "On the dynamics of flexible beams under large overall motions—The plane case: Part I and II"
  authors:
    - "Juan C. Simo"
    - "Loc Vu-Quoc"
  year: 1986
  venue: "Journal of Applied Mechanics"
  scholar_link: "https://scholar.google.com/scholar?q=On+the+dynamics+of+flexible+beams+under+large+overall+motions+Simo"
  clusters: ["flexible multibody", "computational mechanics"]
  concepts: ["geometrically exact beam", "large deformation", "dynamics"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: ["shabana2020dynamics"]

- id: book1984recursive
  title: "Recursive Lagrangian dynamics of flexible manipulator arms"
  authors:
    - "Wayne J. Book"
  year: 1984
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Recursive+Lagrangian+dynamics+of+flexible+manipulator+arms+Book"
  clusters: ["robotics", "flexible bodies"]
  concepts: ["recursive algorithms", "lagrangian dynamics", "flexible manipulators"]
  related_ids: ["de_luca1991closed"]
  references_out_ids: ["de_luca1991closed"]

- id: de_luca1991closed
  title: "Closed-form dynamic model of planar multi-link lightweight robots"
  authors:
    - "Alessandro De Luca"
    - "Bruno Siciliano"
  year: 1991
  venue: "IEEE Transactions on Systems, Man, and Cybernetics"
  scholar_link: "https://scholar.google.com/scholar?q=Closed-form+dynamic+model+of+planar+multi-link+lightweight+robots+De+Luca"
  clusters: ["robotics", "flexible bodies", "control"]
  concepts: ["assumed modes", "lagrangian dynamics", "inverse dynamics"]
  related_ids: ["book1984recursive"]
  references_out_ids: []

- id: lanczos1970variational
  title: "The Variational Principles of Mechanics"
  authors:
    - "Cornelius Lanczos"
  year: 1970
  venue: "Dover Publications"
  scholar_link: "https://scholar.google.com/scholar?q=The+Variational+Principles+of+Mechanics+Lanczos"
  clusters: ["physics", "mathematical foundations"]
  concepts: ["principle of least action", "hamilton's principle", "generalized coordinates"]
  related_ids: ["goldstein2002classical"]
  references_out_ids: ["goldstein2002classical"]

- id: tedrake2023underactuated
  title: "Underactuated Robotics: Algorithms for Walking, Running, Swimming, Flying, and Manipulation"
  authors:
    - "Russ Tedrake"
  year: 2023
  venue: "Course Notes (MIT)"
  scholar_link: "https://scholar.google.com/scholar?q=Underactuated+Robotics+Tedrake"
  clusters: ["robotics", "nonlinear control", "optimization"]
  concepts: ["passive dynamics", "trajectory optimization", "partial feedback linearization"]
  related_ids: ["spong2005robot", "slotine1991applied"]
  references_out_ids: []

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors:
    - "Richard M. Murray"
    - "Zexiang Li"
    - "S. Shankar Sastry"
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "mathematical theory"]
  concepts: ["lie algebra", "screw theory", "lagrangian dynamics"]
  related_ids: ["lynch2017modern"]
  references_out_ids: ["lynch2017modern"]

- id: slotine1991applied
  title: "Applied Nonlinear Control"
  authors:
    - "Jean-Jacques E. Slotine"
    - "Weiping Li"
  year: 1991
  venue: "Prentice Hall"
  scholar_link: "https://scholar.google.com/scholar?q=Applied+Nonlinear+Control+Slotine"
  clusters: ["nonlinear control", "robotics"]
  concepts: ["lyapunov stability", "feedback linearization", "robust control"]
  related_ids: ["isidori1995nonlinear"]
  references_out_ids: ["isidori1995nonlinear"]

- id: hughes1986spacecraft
  title: "Spacecraft Attitude Dynamics"
  authors:
    - "Peter C. Hughes"
  year: 1986
  venue: "Wiley"
  scholar_link: "https://scholar.google.com/scholar?q=Spacecraft+Attitude+Dynamics+Hughes"
  clusters: ["aerospace", "multibody dynamics"]
  concepts: ["flexible spacecraft", "angular momentum", "stability"]
  related_ids: ["junkins1993introduction"]
  references_out_ids: []

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters: ["robotics", "screw theory"]
  concepts: ["exponential coordinates", "dynamics", "control"]
  related_ids: ["murray1994mathematical"]
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
  clusters: ["robotics", "control"]
  concepts: ["lagrangian dynamics", "inverse dynamics", "control"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["multibody dynamics", "algorithms"]
  concepts: ["recursive algorithms", "articulated body algorithm", "spatial algebra"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: ["shabana2020dynamics"]

- id: goldstein2002classical
  title: "Classical Mechanics"
  authors:
    - "Herbert Goldstein"
    - "Charles Poole"
    - "John Safko"
  year: 2002
  venue: "Addison Wesley"
  scholar_link: "https://scholar.google.com/scholar?q=Classical+Mechanics+Goldstein"
  clusters: ["physics", "foundational"]
  concepts: ["lagrangian mechanics", "hamiltonian mechanics", "rigid body motion"]
  related_ids: ["lanczos1970variational"]
  references_out_ids: []

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors:
    - "Alberto Isidori"
  year: 1995
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["nonlinear control", "mathematical theory"]
  concepts: ["affine systems", "differential geometry", "zero dynamics"]
  related_ids: ["slotine1991applied"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (The Theoretical Basics)
*Target: Understand the equation $\dot{x} = f(x) + g(x)u$ and where it comes from.*
1.  **Spong, Hutchinson, Vidyasagar (2005)** - *Robot Modeling and Control*. Best starting point for Lagrangian dynamics.
2.  **Slotine & Li (1991)** - *Applied Nonlinear Control*. Explains the control-affine structure.
3.  **Tedrake (2023)** - *Underactuated Robotics*. Bridges dynamics and control for passive systems.
4.  **Lynch & Park (2017)** - *Modern Robotics*. A comprehensive modern reference.
5.  **Meirovitch (2001)** - *Fundamentals of Vibrations*. Intro to modes (the $\eta$ coordinates).

### Path 2: Deep Technical (Derivation Verification)
*Target: Verify the block matrix inversions and modal approximations.*
1.  **Lanczos (1970)** - *The Variational Principles of Mechanics*. The rigorous foundation for $\delta \int L dt = 0$.
2.  **Shabana (2020)** - *Dynamics of Multibody Systems*. The reference for $M_{rf}$ (rigid-flexible coupling).
3.  **Simo & Vu-Quoc (1986)** - *On the dynamics of flexible beams*. For deep understanding of why simple beam theory fails at high speeds (geometric stiffness).
4.  **Book (1984)** - *Recursive Lagrangian dynamics*. Specific to robot arms with flexibility.
5.  **De Luca & Siciliano (1991)** - *Closed-form dynamic model*. Directly relevant to the "planar pendulum with flexibility" example.
6.  **Hughes (1986)** - *Spacecraft Attitude Dynamics*. Canonical text for coupled rigid-flexible systems (like a satellite with solar panels... or a golfer with a club).
7.  **Isidori (1995)** - *Nonlinear Control Systems*. For the strict definition of drift invariance and input decoupling.

### Path 3: Implementation (Simulation Engines)
*Target: Numerical implementation of the equations.*
1.  **Featherstone (2008)** - *Rigid Body Dynamics Algorithms*. How to compute $M$ and $C$ efficiently (recursive Newton-Euler).
2.  **Pinocchio (Carpentier et al.)** - Modern C++ library implementing Featherstone's algorithms.
3.  **SymPy (Python)** - Use `sympy.physics.mechanics` to symbolically derive the matrices in Appendix A.
4.  **NumPy/SciPy** - For solving the linear system $M \dot{v} = \tau - C v - G$.
5.  **Matlab/Simulink** - (Reference `theory-part5.qmd`) Traditional tool for block-diagram simulation.
