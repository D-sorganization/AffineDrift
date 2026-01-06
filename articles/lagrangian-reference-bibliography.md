# Bibliography: Lagrangian Reference for Control-Affine Multibody Dynamics

## Concept Map

- **Lagrangian Mechanics**: The fundamental framework deriving dynamics from energy ($\mathcal{L} = T - V$).
- **Control-Affine Systems**: The structural form $\dot{x} = f(x) + g(x)u$ central to the AffineDrift theory.
- **Drift Field ($f(x)$)**: The passive dynamics vector field (inertia, Coriolis, gravity, potential).
- **Input Field ($g(x)$)**: The control authority vector field mapping inputs to state evolution.
- **Configuration Manifold ($\mathcal{Q}$)**: The curved space describing all possible system poses.
- **Tangent Bundle ($T\mathcal{Q}$)**: The state space of positions and velocities.
- **Flexible Multibody Dynamics**: Extension of rigid body theory to include deformations (shaft modes).
- **Geometric Control**: Analysis of mechanical systems using differential geometry (connections, curvature).

## References

```yaml
- id: goldstein2002classical
  title: "Classical Mechanics"
  authors: "Goldstein, H., Poole, C., & Safko, J."
  year: 2002
  venue: "Addison Wesley"
  scholar_link: "https://scholar.google.com/scholar?q=Classical+Mechanics+Goldstein"
  clusters: ["mechanics", "physics"]
  concepts:
    ["lagrangian mechanics", "hamiltonian mechanics", "variational principles"]
  related_ids: ["lanczos2012variational", "greenwood2006advanced"]
  references_out_ids: ["arnold1989mathematical"]

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors: "Murray, R. M., Li, Z., & Sastry, S. S."
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "control"]
  concepts: ["manipulator dynamics", "lagrange-euler", "lie groups"]
  related_ids: ["bullo2004geometric", "spong2020robot"]
  references_out_ids: ["lynch2017modern"]

- id: bullo2004geometric
  title: "Geometric Control of Mechanical Systems"
  authors: "Bullo, F., & Lewis, A. D."
  year: 2004
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["geometric control", "mechanics"]
  concepts: ["affine connection", "covariant derivative", "controllability"]
  related_ids: ["bloch2015nonholonomic", "marsden2013introduction"]
  references_out_ids: ["bloch2015nonholonomic"]

- id: shabana2020dynamics
  title: "Dynamics of Multibody Systems"
  authors: "Shabana, A. A."
  year: 2020
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Multibody+Systems+Shabana"
  clusters: ["multibody dynamics", "flexible bodies"]
  concepts:
    ["floating frame of reference", "assumed modes", "flexible dynamics"]
  related_ids: ["simo1986dynamics", "meirovitch2010methods"]
  references_out_ids: ["simo1986dynamics"]

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors: "Isidori, A."
  year: 1995
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["nonlinear control", "systems theory"]
  concepts: ["control-affine form", "zero dynamics", "feedback linearization"]
  related_ids: ["sastry1999nonlinear", "slotine1991applied"]
  references_out_ids: ["sastry1999nonlinear"]

- id: lanczos2012variational
  title: "The Variational Principles of Mechanics"
  authors: "Lanczos, C."
  year: 2012
  venue: "Dover Publications"
  scholar_link: "https://scholar.google.com/scholar?q=The+Variational+Principles+of+Mechanics+Lanczos"
  clusters: ["mechanics", "mathematics"]
  concepts:
    ["variational calculus", "generalized coordinates", "canonical equations"]
  related_ids: ["goldstein2002classical", "arnold1989mathematical"]
  references_out_ids: []

- id: spong2020robot
  title: "Robot Modeling and Control"
  authors: "Spong, M. W., Hutchinson, S., & Vidyasagar, M."
  year: 2020
  venue: "Wiley"
  scholar_link: "https://scholar.google.com/scholar?q=Robot+Modeling+and+Control+Spong"
  clusters: ["robotics", "introductory"]
  concepts: ["lagrangian dynamics", "motion control", "passivity"]
  related_ids: ["murray1994mathematical", "siciliano2010robotics"]
  references_out_ids: ["siciliano2010robotics"]

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors: "Featherstone, R."
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["algorithms", "simulation"]
  concepts:
    ["recursive newton-euler", "articulated body algorithm", "spatial algebra"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: ["pinocchio_lib"]

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors: "Lynch, K. M., & Park, F. C."
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters: ["robotics", "geometric mechanics"]
  concepts: ["screw theory", "product of exponentials", "lagrangian dynamics"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: ["bullo2004geometric"]

- id: meirovitch2010methods
  title: "Methods of Analytical Dynamics"
  authors: "Meirovitch, L."
  year: 2010
  venue: "Dover Publications"
  scholar_link: "https://scholar.google.com/scholar?q=Methods+of+Analytical+Dynamics+Meirovitch"
  clusters: ["dynamics", "vibrations"]
  concepts: ["analytical mechanics", "hamilton's principle", "flexible systems"]
  related_ids: ["goldstein2002classical", "shabana2020dynamics"]
  references_out_ids: []

- id: simo1986dynamics
  title: "On the Dynamics of Flexible Beams Under Large Overall Motions - The Plane Case: Part I and II"
  authors: "Simo, J. C., & Vu-Quoc, L."
  year: 1986
  venue: "Journal of Applied Mechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Flexible+Beams+Simo+Vu-Quoc"
  clusters: ["flexible dynamics", "mechanics"]
  concepts: ["geometrically exact beam", "large deformation", "dynamics"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: []

- id: arnold1989mathematical
  title: "Mathematical Methods of Classical Mechanics"
  authors: "Arnold, V. I."
  year: 1989
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Mathematical+Methods+of+Classical+Mechanics+Arnold"
  clusters: ["mathematical physics", "geometric mechanics"]
  concepts: ["symplectic geometry", "manifolds", "hamiltonian systems"]
  related_ids: ["goldstein2002classical", "bullo2004geometric"]
  references_out_ids: []

- id: slotine1991applied
  title: "Applied Nonlinear Control"
  authors: "Slotine, J. J. E., & Li, W."
  year: 1991
  venue: "Prentice Hall"
  scholar_link: "https://scholar.google.com/scholar?q=Applied+Nonlinear+Control+Slotine"
  clusters: ["nonlinear control", "adaptive control"]
  concepts: ["passivity-based control", "lyapunov stability", "robot control"]
  related_ids: ["isidori1995nonlinear"]
  references_out_ids: []

- id: sastry1999nonlinear
  title: "Nonlinear Systems: Analysis, Stability, and Control"
  authors: "Sastry, S. S."
  year: 1999
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Systems+Sastry"
  clusters: ["nonlinear control", "systems theory"]
  concepts:
    [
      "exterior differential systems",
      "input-output linearization",
      "drift vector field",
    ]
  related_ids: ["isidori1995nonlinear", "murray1994mathematical"]
  references_out_ids: []

- id: siciliano2010robotics
  title: "Robotics: Modelling, Planning and Control"
  authors: "Siciliano, B., Sciavicco, L., Villani, L., & Oriolo, G."
  year: 2010
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Robotics+Modelling+Planning+and+Control+Siciliano"
  clusters: ["robotics", "textbook"]
  concepts: ["dynamic modeling", "trajectory planning", "force control"]
  related_ids: ["spong2020robot"]
  references_out_ids: []

- id: udwadia2007analytical
  title: "Analytical Dynamics: A New Approach"
  authors: "Udwadia, F. E., & Kalaba, R. E."
  year: 2007
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Analytical+Dynamics+Udwadia+Kalaba"
  clusters: ["dynamics", "constraints"]
  concepts: ["gauss's principle", "constrained motion", "moore-penrose inverse"]
  related_ids: ["goldstein2002classical"]
  references_out_ids: []

- id: bloch2015nonholonomic
  title: "Nonholonomic Mechanics and Control"
  authors: "Bloch, A. M."
  year: 2015
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonholonomic+Mechanics+and+Control+Bloch"
  clusters: ["geometric mechanics", "control"]
  concepts:
    [
      "nonholonomic constraints",
      "lagrange-d'alembert principle",
      "optimal control",
    ]
  related_ids: ["bullo2004geometric", "arnold1989mathematical"]
  references_out_ids: []

- id: greenwood2006advanced
  title: "Advanced Dynamics"
  authors: "Greenwood, D. T."
  year: 2006
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Advanced+Dynamics+Greenwood"
  clusters: ["dynamics", "advanced mechanics"]
  concepts: ["virtual work", "gibbs-appell equations", "impact dynamics"]
  related_ids: ["goldstein2002classical"]
  references_out_ids: []

- id: sympy_lib
  title: "SymPy: symbolic computing in Python"
  authors: "Meurer, A., et al."
  year: 2017
  venue: "PeerJ Computer Science"
  scholar_link: "https://scholar.google.com/scholar?q=SymPy+symbolic+computing+in+Python"
  clusters: ["software", "symbolic math"]
  concepts: ["lagrangian derivation", "code generation", "python"]
  related_ids: []
  references_out_ids: []

- id: pinocchio_lib
  title: "Pinocchio: An efficient and rigid multi-body dynamics library"
  authors: "Carpentier, J., et al."
  year: 2019
  venue: "IEEE ICRA"
  scholar_link: "https://scholar.google.com/scholar?q=Pinocchio+efficient+rigid+multi-body+dynamics+library"
  clusters: ["software", "robotics"]
  concepts: ["constructive dynamics", "code generation", "optimization"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []
```

## Reading Paths

### Fast ramp (Foundations)

1.  [spong2020robot] - Accessible introduction to derivation of Euler-Lagrange equations for robots.
2.  [murray1994mathematical] - The standard reference connecting mechanics to control theory (Chapters 4 & 6).
3.  [goldstein2002classical] - The definitive source for the derivation of $\mathcal{L} = T - V$.
4.  [slotine1991applied] - Explicitly bridges Lagrangian dynamics to the $\dot{x} = f(x) + g(x)u$ form.
5.  [sympy_lib] - Tool for verifying your manual derivations symbolically.

### Deep technical (Geometric & Flexible)

1.  [bullo2004geometric] - Rigorous treatment of mechanics on manifolds ($T\mathcal{Q}$).
2.  [arnold1989mathematical] - Deep insight into the symplectic geometry underlying the physics.
3.  [shabana2020dynamics] - Essential for understanding the "extended state" with flexible modes.
4.  [simo1986dynamics] - The seminal work on geometrically exact beam theory (for the shaft).
5.  [isidori1995nonlinear] - Advanced control properties of the resulting affine systems.
6.  [bloch2015nonholonomic] - For when constraints (like the hands on the grip) become complex.
7.  [lanczos2012variational] - A philosophical deep dive into why the variational principles work.
8.  [udwadia2007analytical] - Modern approach to constraints using generalized inverses.

### Implementation (Simulation & Computation)

1.  [featherstone2008rigid] - How to actually compute these terms efficiently ($O(N)$) without symbolic explosion.
2.  [pinocchio_lib] - State-of-the-art C++/Python library implementing Featherstone's algorithms.
3.  [sympy_lib] - Best for deriving the equations of motion for simple models (like the double pendulum).
4.  [shabana2020dynamics] - Provides the floating frame of reference formulation used in many flexible body codes.
5.  [murray1994mathematical] - Reference for the properties of the Mass and Coriolis matrices useful in numerical stability checks.
