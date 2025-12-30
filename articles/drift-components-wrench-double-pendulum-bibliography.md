# Natural vs Active Forces and Torques in Affine Mechanical Systems

# Bibliography

## Concept Map

- **Affine Control System**: Modeling the system as $\dot{x} = f(x) + g(x)u$, separating drift from input.
- **Natural Torque Field**: The set of forces arising purely from system state (inertia, Coriolis, gravity, damping) and environment.
- **Active Torque**: Forces generated specifically by the control inputs (muscles/motors).
- **Mechanical Identity**: The axiomatic equality between internal active torques and the natural torque field for a given trajectory.
- **Double Pendulum**: The canonical 2-link model used to represent the proximal (arm) and distal (club) segments in golf.
- **Lagrangian Dynamics**: The energy-based derivation method used to obtain the equations of motion.
- **Wrench Decomposition**: Splitting the 6D force/moment at an end-effector into natural and active components.
- **Power Transfer**: Analyzing energy flow ($\vec{F} \cdot \vec{v}$) to distinguish between passive geometric transfer and active work.
- **Schur Complement**: (Implicit context) Often used in block matrix inversions for underactuated systems.

## References

bibliography:

- id: jorgensen1970dynamics
  title: "On the Dynamics of the Swing of a Golf Club"
  authors: "Jorgensen, T. P."
  year: 1970
  venue: "American Journal of Physics"
  scholar_link: "https://scholar.google.com/scholar?q=On+the+Dynamics+of+the+Swing+of+a+Golf+Club+Jorgensen"
  clusters: ["golf", "dynamics"]
  concepts: ["double pendulum", "lagrangian dynamics", "wrist torque"]
  related_ids: ["cochran1968search"]
  references_out_ids: ["sharp2009mechanics", "sprigings2000optimal"]

- id: cochran1968search
  title: "The Search for the Perfect Swing"
  authors: "Cochran, A. J., & Stobbs, J."
  year: 1968
  venue: "Heinemann"
  scholar_link: "https://scholar.google.com/scholar?q=The+Search+for+the+Perfect+Swing+Cochran+Stobbs"
  clusters: ["golf", "classic"]
  concepts: ["double pendulum", "kinematics", "model validation"]
  related_ids: ["jorgensen1970dynamics"]
  references_out_ids: ["nesbit2005work"]

- id: murray1994mathematical
  title: "A Mathematical Introduction to Robotic Manipulation"
  authors: "Murray, R. M., Li, Z., & Sastry, S. S."
  year: 1994
  venue: "CRC Press"
  scholar_link: "https://scholar.google.com/scholar?q=A+Mathematical+Introduction+to+Robotic+Manipulation+Murray"
  clusters: ["robotics", "math"]
  concepts: ["lagrangian dynamics", "affine systems", "lie brackets"]
  related_ids: ["lynch2017modern"]
  references_out_ids: ["isidori1995nonlinear", "spong2005robot"]

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors: "Featherstone, R."
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms"
  clusters: ["robotics", "simulation"]
  concepts: ["recursive algorithms", "spatial algebra", "articulated body algorithm"]
  related_ids: ["pinocchio_lib"]
  references_out_ids: ["pinocchio_lib"]

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors: "Isidori, A."
  year: 1995
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["control theory", "nonlinear systems"]
  concepts: ["affine systems", "drift vector field", "geometric control"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors: "Lynch, K. M., & Park, F. C."
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters: ["robotics", "mechanics"]
  concepts: ["configuration space", "lagrangian dynamics", "open chains"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: ["featherstone2008rigid"]

- id: sprigings2000optimal
  title: "An optimal timing strategy for the golf drive"
  authors: "Sprigings, E. J., & Neal, R. J."
  year: 2000
  venue: "Journal of Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Sprigings+Neal+2000+optimal+timing+golf"
  clusters: ["golf", "optimization"]
  concepts: ["muscle torque", "timing", "kinetic link"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: ["mackenzie2009three"]

- id: nesbit2005work
  title: "Work and power analysis of the golf swing"
  authors: "Nesbit, S. M."
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=Nesbit+2005+work+power+golf+swing"
  clusters: ["golf", "biomechanics"]
  concepts: ["work-energy", "power transfer", "joint kinetics"]
  related_ids: ["zajac2002muscle"]
  references_out_ids: ["zajac2002muscle", "robertson1980mechanical"]

- id: zajac2002muscle
  title: "Muscle coordination of movement: a perspective"
  authors: "Zajac, F. E., Neptune, R. R., & Kautz, S. A."
  year: 2002
  venue: "Journal of Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Zajac+2002+muscle+coordination+movement"
  clusters: ["biomechanics", "motor control"]
  concepts: ["muscle function", "coordination", "power flow"]
  related_ids: ["nesbit2005work"]
  references_out_ids: ["todorov2004optimality"]

- id: sharp2009mechanics
  title: "On the mechanics of the golf swing"
  authors: "Sharp, R. S."
  year: 2009
  venue: "Proceedings of the Royal Society A"
  scholar_link: "https://scholar.google.com/scholar?q=Sharp+2009+mechanics+golf+swing"
  clusters: ["golf", "dynamics"]
  concepts: ["double pendulum", "optimization", "torque profiles"]
  related_ids: ["jorgensen1970dynamics"]
  references_out_ids: []

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors: "MacKenzie, S. J., & Sprigings, E. J."
  year: 2009
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=MacKenzie+Sprigings+2009+golf+swing"
  clusters: ["golf", "simulation"]
  concepts: ["forward dynamics", "3D model", "muscle torque"]
  related_ids: ["sprigings2000optimal"]
  references_out_ids: []

- id: pinocchio_lib
  title: "Pinocchio: An efficient and rigid multi-body dynamics library"
  authors: "Carpentier, J., et al."
  year: 2019
  venue: "IEEE ICRA"
  scholar_link: "https://scholar.google.com/scholar?q=Pinocchio+efficient+rigid+multi-body+dynamics+library"
  clusters: ["software", "simulation"]
  concepts: ["c++", "rigid body algorithms", "recursive newton-euler"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []

- id: scipy_lib
  title: "SciPy 1.0: fundamental algorithms for scientific computing in Python"
  authors: "Virtanen, P., et al."
  year: 2020
  venue: "Nature Methods"
  scholar_link: "https://scholar.google.com/scholar?q=SciPy+1.0+fundamental+algorithms"
  clusters: ["software", "scientific computing"]
  concepts: ["numerical integration", "ode solvers", "optimization"]
  related_ids: []
  references_out_ids: []

- id: spong2005robot
  title: "Robot Modeling and Control"
  authors: "Spong, M. W., Hutchinson, S., & Vidyasagar, M."
  year: 2005
  venue: "Wiley"
  scholar_link: "https://scholar.google.com/scholar?q=Robot+Modeling+and+Control+Spong"
  clusters: ["robotics", "control"]
  concepts: ["lagrangian dynamics", "control affine", "trajectory tracking"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

- id: robertson1980mechanical
  title: "Mechanical energy generation, absorption and transfer amongst segments during walking"
  authors: "Robertson, D. G., & Winter, D. A."
  year: 1980
  venue: "Journal of Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Robertson+Winter+1980+mechanical+energy"
  clusters: ["biomechanics", "energy"]
  concepts: ["power flow", "segmental energy", "joint work"]
  related_ids: ["nesbit2005work"]
  references_out_ids: []

- id: todorov2004optimality
  title: "Optimality principles in sensorimotor control"
  authors: "Todorov, E."
  year: 2004
  venue: "Nature Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Todorov+optimality+principles+sensorimotor+control"
  clusters: ["motor control", "optimization"]
  concepts: ["optimal control", "minimal intervention", "feedback"]
  related_ids: ["zajac2002muscle"]
  references_out_ids: []

- id: kaner1985dynamics
  title: "Dynamics: Theory and Applications"
  authors: "Kane, T. R., & Levinson, D. A."
  year: 1985
  venue: "McGraw-Hill"
  scholar_link: "https://scholar.google.com/scholar?q=Kane+Dynamics+Theory+and+Applications"
  clusters: ["dynamics", "mechanics"]
  concepts: ["kane's method", "multibody dynamics", "generalized speeds"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []

- id: bullo2005geometric
  title: "Geometric Control of Mechanical Systems"
  authors: "Bullo, F., & Lewis, A. D."
  year: 2005
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["control theory", "mechanics"]
  concepts: ["differential geometry", "mechanical systems", "nonholonomic constraints"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: []

## Reading Paths

### Fast ramp (Foundations)

1.  [jorgensen1970dynamics] - The classic physicist's analysis of the golf swing as a double pendulum.
2.  [cochran1968search] - The "bible" of golf science, establishing the planar double pendulum model.
3.  [murray1994mathematical] - (Chapter 4) Formal introduction to Lagrangian dynamics for robotic manipulators.
4.  [nesbit2005work] - Application of work-energy principles to the golf swing, critical for understanding "active" vs "natural" contributions.
5.  [isidori1995nonlinear] - (Introduction) The rigorous definition of affine control systems ($\dot{x} = f(x) + g(x)u$).

### Deep technical (Advanced Mechanics)

1.  [featherstone2008rigid] - The gold standard for implementing rigid body dynamics algorithms efficiently (recursive methods).
2.  [lynch2017modern] - Modern treatment of robotics dynamics using screw theory and geometric mechanics.
3.  [spong2005robot] - Standard text connecting dynamics derivation to control design.
4.  [sharp2009mechanics] - A more sophisticated mathematical treatment of the double pendulum optimization in golf.
5.  [robertson1980mechanical] - Foundational paper on segmental energy analysis, distinguishing between generation and transfer.
6.  [zajac2002muscle] - Detailed review of muscle coordination and the complexities of power flow in biological systems.
7.  [kaner1985dynamics] - Kane's method offers an alternative, highly efficient formulation for complex multibody systems.
8.  [bullo2005geometric] - Advanced geometric control theory for underactuated mechanical systems.

### Implementation (Simulation & Analysis)

1.  [jorgensen1970dynamics] - Provides the basic equations of motion for the double pendulum model.
2.  [scipy_lib] - The core library for solving the differential equations (`solve_ivp`) derived in the article.
3.  [pinocchio_lib] - Advanced library for scaling this analysis to full 3D multibody models.
4.  [mackenzie2009three] - Provides realistic parameters (lengths, masses, inertias) for a golf swing model.
5.  [sprigings2000optimal] - Offers a baseline for optimization strategies and torque profiles to test against.
