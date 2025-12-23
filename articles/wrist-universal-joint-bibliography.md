# Bibliographic Analysis: Constraint Torques at the Wrist (Universal Joint Model)

## A) Concept Map

- **Mechanism Analysis**
  - **Universal Joint (Cardan Joint)**: Modeling the wrist as two actuated orthogonal axes + one constrained axis.
  - **Constraint Torques**: Passive torques $\tau_{constraint}$ arising purely from geometric constraints ($\lambda$) to enforce non-holonomic or holonomic restrictions.
  - **Underactuation**: The wrist has $n=3$ rotational DOFs but only $m=2$ controls; the third (forearm rotation relative to hand) is constrained.

- **Dynamics & Transmission**
  - **Force Transmission**: Constraint forces perform zero work ($\tau \cdot \dot{q} = 0$) but transmit energy/momentum between links.
  - **Disturbance Decoupling**: Aligning the system geometry so that "noise" (variable constraint torque) enters the dynamics via a "safe" subspace (Alpha axis).
  - **Inertia Tensor Shaping**: The distinction between high-inertia (swing plane, $I_{\alpha}$) and low-inertia (face rotation, $I_{\beta}$) axes.

- **Control Theory Interpretation**
  - **Null Space / Uncontrolled Manifold**: Channelling variability into dimensions that do not affect the task variable (face angle).
  - **Geometric Rejection**: Using static configuration (grip) to solve a dynamic control problem.

- **Biomechanics Applications**
  - **Grip Mechanics**: "Finger Grip" vs "Palm Grip" as mechanical filters.
  - **Planar Constraints**: The functional role of arm-club plane separation.

## B) Bibliography (YAML)

```yaml
- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Mechanics+Planning+and+Control+Lynch"
  clusters: ["robotics", "mechanics"]
  concepts: ["constrained dynamics", "universal joints", "pfaffian constraints"]
  related_ids: ["murray1994mathematical", "kane1985dynamics"]
  references_out_ids: ["murray1994mathematical", "featherstone2008rigid"]

- id: kane1985dynamics
  title: "Dynamics: Theory and Applications"
  authors:
    - "Thomas R. Kane"
    - "David A. Levinson"
  year: 1985
  venue: "McGraw-Hill"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+Theory+and+Applications+Kane"
  clusters: ["multibody dynamics", "foundational"]
  concepts: ["nonholonomic constraints", "constraint forces", "kane's method"]
  related_ids: ["udwadia1996analytical"]
  references_out_ids: ["udwadia1996analytical"]

- id: udwadia1996analytical
  title: "Analytical Dynamics: A New Approach"
  authors:
    - "Firdaus E. Udwadia"
    - "Robert E. Kalaba"
  year: 1996
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Analytical+Dynamics+A+New+Approach+Udwadia"
  clusters: ["mechanics", "mathematical theory"]
  concepts:
    ["fundamental equation of constrained motion", "gauss principle", "generalized inverse"]
  related_ids: ["kane1985dynamics"]
  references_out_ids: ["kane1985dynamics"]

- id: mackenzie2009three
  title: "A three-dimensional forward dynamics model of the golf swing"
  authors:
    - "Sasho J. MacKenzie"
    - "Eric J. Sprigings"
  year: 2009
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=A+three-dimensional+forward+dynamics+model+of+the+golf+swing+MacKenzie"
  clusters: ["golf biomechanics", "simulation"]
  concepts: ["forward dynamics", "shaft deflection", "structural dynamics"]
  related_ids: ["nesbit2005three"]
  references_out_ids: ["nesbit2005three", "sprigings2000insight"]

- id: sprigings2000insight
  title: "An insight into the importance of wrist torque in driving the golf ball: a simulation study"
  authors:
    - "Eric J. Sprigings"
    - "Robert J. Neal"
  year: 2000
  venue: "Journal of Applied Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=An+insight+into+the+importance+of+wrist+torque+in+driving+the+golf+ball+Sprigings"
  clusters: ["golf biomechanics", "simulation"]
  concepts: ["wrist kinetics", "torque generation", "impact"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: ["mackenzie2009three"]

- id: koike2006analysis
  title: "Analysis of the wrist action in golf swing"
  authors:
    - "Sekiya Koike"
    - "H. Iida"
    - "H. Shiraki"
  year: 2006
  venue: "Theoretical and Applied Mechanics Japan"
  scholar_link: "https://scholar.google.com/scholar?q=Analysis+of+the+wrist+action+in+golf+swing+Koike"
  clusters: ["golf biomechanics", "kinematics"]
  concepts: ["wrist angles", "3d kinematics", "cocking"]
  related_ids: ["nesbit2005three"]
  references_out_ids: []

- id: todorov2004optimality
  title: "Optimality principles in sensorimotor control"
  authors:
    - "Emanuel Todorov"
  year: 2004
  venue: "Nature Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Optimality+principles+in+sensorimotor+control+Todorov"
  clusters: ["motor control", "neuroscience"]
  concepts: ["uncontrolled manifold", "minimal intervention", "task-relevant variability"]
  related_ids: ["latash2008synergy"]
  references_out_ids: ["latash2008synergy", "bernstein1967coordination"]

- id: coleman2005three
  title: "A three-dimensional examination of the planar nature of the golf swing"
  authors:
    - "S. G. Coleman"
    - "A. J. Rankin"
  year: 2005
  venue: "Journal of Sports Sciences"
  scholar_link: "https://scholar.google.com/scholar?q=A+three-dimensional+examination+of+the+planar+nature+of+the+golf+swing+Coleman"
  clusters: ["golf biomechanics", "kinematics"]
  concepts: ["swing plane", "planar motion", "kinematic geometry"]
  related_ids: ["kwon2012validity"]
  references_out_ids: []

- id: kwon2012validity
  title: "Validity of the X-Factor computation methods and relationship between the X-Factor parameters and clubhead velocity in skilled golfers"
  authors:
    - "Young-Hoo Kwon"
    - "K. H. Han"
    - "C. Como"
  year: 2012
  venue: "Sports Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Validity+of+the+X-Factor+computation+methods+Kwon"
  clusters: ["golf biomechanics", "kinematics"]
  concepts: ["x-factor", "kinematic sequence", "torso rotation"]
  related_ids: ["coleman2005three"]
  references_out_ids: []

- id: tinmark2010elite
  title: "Elite golfers' kinematic sequence in full-swing and partial-swing shots"
  authors:
    - "F. Tinmark"
    - "J. Hellström"
    - "K. Halvorsen"
    - "A. Thorstensson"
  year: 2010
  venue: "Sports Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Elite+golfers'+kinematic+sequence+Tinmark"
  clusters: ["golf biomechanics", "motor control"]
  concepts: ["kinematic sequence", "coordination", "proximal-to-distal"]
  related_ids: ["nesbit2005three"]
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
  clusters: ["robotics", "control theory"]
  concepts: ["so(3)", "twist coordinates", "exponential map"]
  related_ids: ["lynch2017modern"]
  references_out_ids: ["lynch2017modern", "featherstone2008rigid"]

- id: latash2008synergy
  title: "Synergy"
  authors:
    - "Mark L. Latash"
  year: 2008
  venue: "Oxford University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Synergy+Latash"
  clusters: ["motor control", "biomechanics"]
  concepts: ["principle of abundance", "motor synergies", "variability"]
  related_ids: ["todorov2004optimality"]
  references_out_ids: ["todorov2004optimality"]

- id: zatsiorsky1998kinematics
  title: "Kinematics of Human Motion"
  authors:
    - "Vladimir M. Zatsiorsky"
  year: 1998
  venue: "Human Kinetics"
  scholar_link: "https://scholar.google.com/scholar?q=Kinematics+of+Human+Motion+Zatsiorsky"
  clusters: ["biomechanics", "textbook"]
  concepts: ["joint coordinate systems", "euler angles", "helical axes"]
  related_ids: ["winter2009biomechanics"]
  references_out_ids: []

- id: nesbit2005three
  title: "A three dimensional kinematic and kinetic study of the golf swing"
  authors:
    - "Steven M. Nesbit"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=A+three+dimensional+kinematic+and+kinetic+study+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "inverse dynamics"]
  concepts: ["joint torques", "work and power", "full-body model"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: ["mackenzie2009three"]

- id: winter2009biomechanics
  title: "Biomechanics and Motor Control of Human Movement"
  authors:
    - "David A. Winter"
  year: 2009
  venue: "John Wiley & Sons"
  scholar_link: "https://scholar.google.com/scholar?q=Biomechanics+and+Motor+Control+of+Human+Movement+Winter"
  clusters: ["biomechanics", "motor control"]
  concepts: ["kinematics", "kinetics", "electromyography"]
  related_ids: ["zajac1993muscle"]
  references_out_ids: []

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["multibody dynamics", "simulation"]
  concepts: ["recursive algorithms", "spatial vectors", "articulated body algorithm"]
  related_ids: ["murray1994mathematical"]
  references_out_ids: ["pinocchio_lib"]

- id: shabana2020dynamics
  title: "Dynamics of Multibody Systems"
  authors:
    - "Ahmed A. Shabana"
  year: 2020
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamics+of+Multibody+Systems+Shabana"
  clusters: ["multibody dynamics", "flexible bodies"]
  concepts: ["floating frame of reference", "flexible multibody", "assumed modes"]
  related_ids: ["featherstone2008rigid"]
  references_out_ids: []

- id: isidori1995nonlinear
  title: "Nonlinear Control Systems"
  authors:
    - "Alberto Isidori"
  year: 1995
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Control+Systems+Isidori"
  clusters: ["nonlinear control", "mathematical theory"]
  concepts: ["affine systems", "zero dynamics", "drift vector field"]
  related_ids: ["slotine1991applied"]
  references_out_ids: []

- id: bernstein1967coordination
  title: "The Co-ordination and Regulation of Movements"
  authors:
    - "Nikolai A. Bernstein"
  year: 1967
  venue: "Pergamon Press"
  scholar_link: "https://scholar.google.com/scholar?q=The+Co-ordination+and+Regulation+of+Movements+Bernstein"
  clusters: ["motor control", "foundational"]
  concepts: ["degrees of freedom problem", "motor control", "coordination"]
  related_ids: ["latash2008synergy"]
  references_out_ids: []

- id: mathworks2024simscape
  title: "Simscape Multibody Documentation"
  authors:
    - "MathWorks"
  year: 2024
  venue: "MathWorks Website"
  scholar_link: "https://scholar.google.com/scholar?q=Simscape+Multibody+Documentation"
  clusters: ["software", "simulation"]
  concepts: ["universal joint block", "sensed torque", "multibody simulation"]
  related_ids: []
  references_out_ids: []

- id: delp2007opensim
  title: "OpenSim: open-source software to create and analyze dynamic simulations of movement"
  authors:
    - "Scott L. Delp"
    - "et al."
  year: 2007
  venue: "IEEE Transactions on Biomedical Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=OpenSim+Delp"
  clusters: ["software", "biomechanics"]
  concepts: ["musculoskeletal modeling", "simulation", "wrist model"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (The Mechanics of Constraints)

_Target: Understand why "locking" a degree of freedom creates a torque._

1.  **Lynch & Park (2017)** - _Modern Robotics_ (Chapter 8.7: Constrained Dynamics). The best modern text explaining $\tau = J^T \lambda$.
2.  **Kane & Levinson (1985)** - _Dynamics_. Explicitly deals with "nonholonomic" constraints which is how universal joints are often treated in advanced dynamics.
3.  **Todorov (2004)** - _Optimality principles_. Explains the "Null Space" concept—how the brain exploits dimensions that don't matter (or matter less).
4.  **Koike et al. (2006)** - _Analysis of wrist action_. Specific data on what the wrist actually does during the swing.
5.  **MacKenzie & Sprigings (2009)** - _Forward dynamics_. Context for how these torques drive the Club.

### Path 2: Deep Technical (Advanced Dynamics)

_Target: Calculating the Lagrange Multipliers and modeling the system._

1.  **Udwadia & Kalaba (1996)** - _Analytical Dynamics_. Provides the "Fundamental Equation of Constrained Motion"—the explicit closed-form solution for constraint forces.
2.  **Murray, Li, Sastry (1994)** - _Mathematical Introduction_. Geometric view of constraints and rigid body systems.
3.  **Zatsiorsky (1998)** - _Kinematics of Human Motion_. Detailed joint modeling issues (Cardan angles vs U-joints).
4.  **Featherstone (2008)** - _Rigid Body Dynamics Algorithms_. The computational implementation of constrained multibody systems (e.g., recursive constraints).
5.  **Shabana (2020)** - _Dynamics of Multibody Systems_. General formulation for constrained systems including flexible bodies.
6.  **Isidori (1995)** - _Nonlinear Control Systems_. For understanding "drift invariance" and affine control structures.
7.  **Bernstein (1967)** - _The Co-ordination and Regulation of Movements_. The foundational framing of the "Degrees of Freedom Problem" that constraints help solve.
8.  **Coleman & Rankin (2005)** - _Planar nature_. Geometry of the swing plane which relates to the "Alpha" axis.
9.  **Sprigings & Neal (2000)** - _Importance of wrist torque_. Validation of the torque magnitudes.

### Path 3: Implementation (Simulation)

_Target: Building the Universal Joint model._

1.  **Simscape Multibody Documentation** (`mathworks2024simscape`) - Specifically the "Universal Joint" block reference, which explains the "sensed torque" outputs.
2.  **MacKenzie (2009)** - Parameters for the club inertia ($I_{\alpha}$ vs $I_{\beta}$).
3.  **Nesbit (2005)** - Inverse dynamics data to check against.
4.  **Kwon (2012)** - Kinematic data for validation.
5.  **OpenSim (Delp)** (`delp2007opensim`) - For comparing with detailed wrist muscle models.
