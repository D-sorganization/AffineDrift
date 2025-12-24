# Bibliographic Analysis: Drift/Input Decomposition and Counterfactuals

## A) Concept Map

- **Decomposition Frameworks**

  - **Affine Control Systems**: The structural basis $\dot{x} = f(x) + g(x)u$.
  - **Passive vs. Active**: Separating natural dynamics ($f$) from forced response ($g$).
  - **Underactuation**: Systems where dim($u$) < dim($q$), relying on drift.

- **Counterfactual Diagnostics**

  - **Zero Torque Counterfactual (ZTCF)**: Simulating the "drift-only" trajectory ($u=0$).
  - **Zero Velocity Counterfactual (ZVCF)**: Isolating configuration-dependent forces (gravity, stiffness).
  - **Causal Attribution**: Using model interventions to assign cause to forces.

- **Dynamics & Mechanics**

  - **Passive Dynamic Walking**: Exploiting natural gait dynamics (McGeer).
  - **Impedance/Admittance**: How systems respond to external forces.
  - **Geometric Control**: Analyzing vector fields on manifolds.

- **Biomechanics Context**
  - **Muscle Synergy**: Coordinated activation to manage degrees of freedom.
  - **Inverse Dynamics Interpretation**: The danger of interpreting net torque as "effort".

## B) Bibliography (YAML)

```yaml
- id: mcgeer1990passive
  title: "Passive Dynamic Walking"
  authors:
    - "Tad McGeer"
  year: 1990
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Passive+Dynamic+Walking+McGeer"
  clusters: ["passive dynamics", "robotics", "locomotion"]
  concepts: ["limit cycles", "natural dynamics", "energy efficiency"]
  related_ids: ["tedrake2023underactuated", "collins2005efficient"]
  references_out_ids: []

- id: bullo2004geometric
  title: "Geometric Control of Mechanical Systems"
  authors:
    - "Francesco Bullo"
    - "Andrew D. Lewis"
  year: 2004
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["geometric control", "nonlinear systems", "mathematics"]
  concepts: ["affine connection", "lagrangian mechanics", "controllability"]
  related_ids: ["murray1994mathematical", "isidori1995nonlinear"]
  references_out_ids: ["isidori1995nonlinear"]

- id: pearl2009causality
  title: "Causality: Models, Reasoning, and Inference"
  authors:
    - "Judea Pearl"
    - "TS Verlinden"
  year: 2009
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Causality+Models+Reasoning+and+Inference+Pearl"
  clusters: ["causality", "logic", "statistics"]
  concepts: ["counterfactuals", "intervention", "do-calculus"]
  related_ids: []
  references_out_ids: []

- id: todorov2002optimal
  title: "Optimal feedback control as a theory of motor coordination"
  authors:
    - "Emanuel Todorov"
    - "Michael I. Jordan"
  year: 2002
  venue: "Nature Neuroscience"
  scholar_link: "https://scholar.google.com/scholar?q=Optimal+feedback+control+as+a+theory+of+motor+coordination+Todorov"
  clusters: ["motor control", "neuroscience", "optimal control"]
  concepts:
    ["minimum intervention principle", "uncontrolled manifold", "feedback"]
  related_ids: ["zajac1993muscle", "latash2008synergy"]
  references_out_ids: []

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Mechanics+Planning+and+Control+Lynch"
  clusters: ["robotics", "mechanics"]
  concepts: ["screw theory", "lagrangian dynamics", "motion planning"]
  related_ids: ["murray1994mathematical", "spong2005robot"]
  references_out_ids: ["murray1994mathematical"]

- id: khatib1987unified
  title: "A unified approach for motion and force control of robot manipulators: The operational space formulation"
  authors:
    - "Oussama Khatib"
  year: 1987
  venue: "IEEE Journal on Robotics and Automation"
  scholar_link: "https://scholar.google.com/scholar?q=A+unified+approach+for+motion+and+force+control+Khatib"
  clusters: ["robotics", "control"]
  concepts: ["operational space", "dynamic decoupling", "force control"]
  related_ids: ["hogan1985impedance"]
  references_out_ids: ["hogan1985impedance"]

- id: collins2005efficient
  title: "Efficient bipedal robots based on passive-dynamic walkers"
  authors:
    - "Steve Collins"
    - "Andy Ruina"
    - "Russ Tedrake"
    - "Martijn Wisse"
  year: 2005
  venue: "Science"
  scholar_link: "https://scholar.google.com/scholar?q=Efficient+bipedal+robots+based+on+passive-dynamic+walkers"
  clusters: ["robotics", "passive dynamics"]
  concepts: ["energy efficiency", "passive walking", "biomimetics"]
  related_ids: ["mcgeer1990passive", "tedrake2023underactuated"]
  references_out_ids: []

- id: latash2008synergy
  title: "Synergy"
  authors:
    - "Mark L. Latash"
  year: 2008
  venue: "Oxford University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Synergy+Latash"
  clusters: ["motor control", "biomechanics"]
  concepts: ["uncontrolled manifold", "motor redundancy", "coordination"]
  related_ids: ["todorov2002optimal", "bernstein1967coordination"]
  references_out_ids: ["bernstein1967coordination"]

- id: bernstein1967coordination
  title: "The Co-ordination and Regulation of Movements"
  authors:
    - "Nikolai A. Bernstein"
  year: 1967
  venue: "Pergamon Press"
  scholar_link: "https://scholar.google.com/scholar?q=The+Co-ordination+and+Regulation+of+Movements+Bernstein"
  clusters: ["motor control", "foundational"]
  concepts: ["degrees of freedom problem", "motor control", "biomechanics"]
  related_ids: ["latash2008synergy"]
  references_out_ids: []

- id: spong1998underactuated
  title: "Underactuated mechanical systems"
  authors:
    - "Mark W. Spong"
  year: 1998
  venue: "Control Problems in Robotics and Automation"
  scholar_link: "https://scholar.google.com/scholar?q=Underactuated+mechanical+systems+Spong"
  clusters: ["nonlinear control", "robotics"]
  concepts: ["partial feedback linearization", "passivity", "acrobot"]
  related_ids: ["tedrake2023underactuated", "bullo2004geometric"]
  references_out_ids: []

- id: vaughan1982biomechanics
  title: "The biomechanics of the golf swing"
  authors:
    - "Christopher L. Vaughan"
  year: 1982
  venue: "Science of Golf"
  scholar_link: "https://scholar.google.com/scholar?q=The+biomechanics+of+the+golf+swing+Vaughan"
  clusters: ["golf biomechanics"]
  concepts: ["kinematics", "kinetics", "optimization"]
  related_ids: ["nesbit2005three", "cochran1968search"]
  references_out_ids: []

- id: nijmeijer1990nonlinear
  title: "Nonlinear Dynamical Control Systems"
  authors:
    - "Henk Nijmeijer"
    - "Arjan van der Schaft"
  year: 1990
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Nonlinear+Dynamical+Control+Systems+Nijmeijer"
  clusters: ["nonlinear control", "mathematics"]
  concepts: ["input-output decoupling", "zero dynamics", "hamiltonian systems"]
  related_ids: ["isidori1995nonlinear", "slotine1991applied"]
  references_out_ids: []

- id: harris1998signal
  title: "Signal-dependent noise determines motor planning"
  authors:
    - "Christopher M. Harris"
    - "Daniel M. Wolpert"
  year: 1998
  venue: "Nature"
  scholar_link: "https://scholar.google.com/scholar?q=Signal-dependent+noise+determines+motor+planning+Harris"
  clusters: ["motor control", "neuroscience"]
  concepts: ["trajectory planning", "noise", "optimal control"]
  related_ids: ["todorov2002optimal"]
  references_out_ids: []

- id: winter2009biomechanics
  title: "Biomechanics and Motor Control of Human Movement"
  authors:
    - "David A. Winter"
  year: 2009
  venue: "John Wiley & Sons"
  scholar_link: "https://scholar.google.com/scholar?q=Biomechanics+and+Motor+Control+of+Human+Movement+Winter"
  clusters: ["biomechanics", "motor control"]
  concepts: ["inverse dynamics", "electromyography", "kinetics"]
  related_ids: ["zajac1993muscle"]
  references_out_ids: []

- id: anderson2001dynamic
  title: "Dynamic optimization of human walking"
  authors:
    - "Frank C. Anderson"
    - "Marcus G. Pandy"
  year: 2001
  venue: "Journal of Biomechanical Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=Dynamic+optimization+of+human+walking+Anderson"
  clusters: ["biomechanics", "optimization"]
  concepts: ["dynamic optimization", "walking", "metabolic energy"]
  related_ids: ["mackenzie2009three", "pandy2001computer"]
  references_out_ids: ["pandy2001computer"]

- id: pandy2001computer
  title: "Computer modeling and simulation of human movement"
  authors:
    - "Marcus G. Pandy"
  year: 2001
  venue: "Annual Review of Biomedical Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=Computer+modeling+and+simulation+of+human+movement+Pandy"
  clusters: ["biomechanics", "simulation"]
  concepts: ["musculoskeletal modeling", "forward dynamics", "simulation"]
  related_ids: ["anderson2001dynamic", "opensim_lib"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (The "Why" of Drift)

_Target: Understand why we separate active and passive forces._

1.  **McGeer (1990)** - _Passive Dynamic Walking_. The classic proof that "dumb" physics can look like "smart" control.
2.  **Collins et al. (2005)** - _Efficient bipedal robots..._. Demonstrates passive dynamics in physical robots.
3.  **Vaughan (1982)** - _Biomechanics of the golf swing_. Early biomechanical context for golf.
4.  **Todorov & Jordan (2002)** - _Optimal feedback control..._. Introduces the "minimum intervention" principle (only control what matters, let drift handle the rest).
5.  **Pearl (2009)** - _Causality_ (Introductory chapters). The logic of "Intervention" ($do(u=0)$) which is the basis for the ZTCF.

### Path 2: Deep Technical (Geometric & Control Theory)

_Target: The mathematical machinery for $\dot{x} = f(x) + g(x)u$._

1.  **Bullo & Lewis (2004)** - _Geometric Control of Mechanical Systems_. Rigorous treatment of mechanical drift and controllability.
2.  **Spong (1998)** - _Underactuated Mechanical Systems_. Analyzing systems where you can't push in every direction directly.
3.  **Nijmeijer & van der Schaft (1990)** - _Nonlinear Dynamical Control Systems_. For the definitions of input-affine systems.
4.  **Lynch & Park (2017)** - _Modern Robotics_. A comprehensive modern reference.
5.  **Khatib (1987)** - _Operational Space_. How to project dynamics into task space.
6.  **Bernstein (1967)** - _Co-ordination and Regulation of Movements_. The foundational definition of the degrees-of-freedom problem.
7.  **Latash (2008)** - _Synergy_. Deep dive into the "Uncontrolled Manifold" hypothesis which aligns with drift.
8.  **Harris & Wolpert (1998)** - _Signal-dependent noise_. Theoretical justification for why brains minimize active torque (input minimization).

### Path 3: Implementation (Simulation & Analysis)

_Target: Tools for calculating these counterfactuals._

1.  **Pandy (2001)** - _Computer modeling..._. Overview of forward dynamics simulation in biomechanics.
2.  **Anderson & Pandy (2001)** - _Dynamic optimization..._. Practical example of large-scale forward simulation.
3.  **Drake (Tedrake et al.)** - (See Part 1) The gold standard for passive/active dynamics analysis.
4.  **Pinocchio** - (See Part 1) Fast recursive algorithms for $M(q)$ and Coriolis terms.
5.  **SciPy (<code>solve_ivp</code>)** - Using standard integrators to run the ZTCF ($u=0$) trajectory.
