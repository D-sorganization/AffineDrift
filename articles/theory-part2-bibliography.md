# Bibliographic Analysis: Drift/Input Decomposition & Counterfactuals

## A) Concept Map

*   **Dynamics Decomposition**
    *   **Control-Affine System**: Modeling the swing as $\dot{x} = f(x) + g(x)u$.
    *   **Drift Vector Field** ($f(x)$): The system's passive evolution (inertia, gravity, Coriolis, stiffness) without active input.
    *   **Input Vector Field** ($g(x)u$): The active contribution from joint torques.
    *   **Superposition**: The additive nature of forces in the equations of motion.

*   **Counterfactual Analysis**
    *   **Zero Torque Counterfactual (ZTCF)**: A trajectory evolving purely under $f(x)$ from the same initial state (isolating history-dependent drift).
    *   **Zero Velocity Counterfactual (ZVCF)**: An instantaneous state assessment with $\dot{q}=0$ (isolating configuration-dependent stiffness/gravity).
    *   **Causal Diagnostics**: Using counterfactuals to separate "muscle" contributions from "physics" contributions.

*   **Mechanics & Control**
    *   **Inverse Dynamics (ID)**: Computing $\tau_{total}$ from observed motion.
    *   **Induced Acceleration**: The concept that a torque at one joint accelerates all joints (dynamical coupling).
    *   **Passive Dynamics**: Motion driven by energy storage/exchange (gravity, elasticity) rather than power input.
    *   **Underactuation**: The swing has fewer inputs than degrees of freedom (due to the flexible shaft or ground contact nature).

## B) Bibliography (YAML)

```yaml
- id: bullo2004geometric
  title: "Geometric Control of Mechanical Systems"
  authors:
    - "Francesco Bullo"
    - "Andrew D. Lewis"
  year: 2004
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Geometric+Control+of+Mechanical+Systems+Bullo"
  clusters: ["geometric control", "nonlinear systems"]
  concepts: ["affine connection", "mechanical systems", "lagrangian dynamics"]
  related_ids: ["murray1994mathematical", "bloch2003nonholonomic"]
  references_out_ids: ["bloch2003nonholonomic"]

- id: zajac1989determining
  title: "Determining muscle's force and action in multi-joint movement"
  authors:
    - "Felix E. Zajac"
    - "M. E. Gordon"
  year: 1989
  venue: "Exercise and Sport Sciences Reviews"
  scholar_link: "https://scholar.google.com/scholar?q=Determining+muscle's+force+and+action+in+multi-joint+movement+Zajac"
  clusters: ["biomechanics", "motor control"]
  concepts: ["induced acceleration", "dynamical coupling", "muscle actuation"]
  related_ids: ["zajac1993muscle", "pandy2001computer"]
  references_out_ids: ["pandy2001computer"]

- id: mcgeer1990passive
  title: "Passive Dynamic Walking"
  authors:
    - "Tad McGeer"
  year: 1990
  venue: "The International Journal of Robotics Research"
  scholar_link: "https://scholar.google.com/scholar?q=Passive+Dynamic+Walking+McGeer"
  clusters: ["robotics", "passive dynamics"]
  concepts: ["limit cycles", "energy efficiency", "natural dynamics"]
  related_ids: ["collins2005efficient", "tedrake2023underactuated"]
  references_out_ids: ["collins2005efficient"]

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - "Kevin M. Lynch"
    - "Frank C. Park"
  year: 2017
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Modern+Robotics+Lynch+Park"
  clusters: ["robotics", "textbook"]
  concepts: ["screw theory", "lagrangian dynamics", "control"]
  related_ids: ["murray1994mathematical", "spong2005robot"]
  references_out_ids: ["mason2001mechanics"]

- id: featherstone2008rigid
  title: "Rigid Body Dynamics Algorithms"
  authors:
    - "Roy Featherstone"
  year: 2008
  venue: "Springer"
  scholar_link: "https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone"
  clusters: ["multibody dynamics", "simulation", "algorithms"]
  concepts: ["recursive algorithms", "articulated body algorithm", "spatial vectors"]
  related_ids: ["murray1994mathematical", "shabana2020dynamics"]
  references_out_ids: ["shabana2020dynamics"]

- id: nesbit2005three
  title: "A three dimensional kinematic and kinetic study of the golf swing"
  authors:
    - "Steven M. Nesbit"
  year: 2005
  venue: "Journal of Sports Science and Medicine"
  scholar_link: "https://scholar.google.com/scholar?q=A+three+dimensional+kinematic+and+kinetic+study+of+the+golf+swing+Nesbit"
  clusters: ["golf biomechanics", "inverse dynamics"]
  concepts: ["full-body model", "joint torques", "work and power"]
  related_ids: ["mackenzie2009three", "cochran1968search"]
  references_out_ids: ["mackenzie2009three"]

- id: deleva1996adjustments
  title: "Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters"
  authors:
    - "Paolo de Leva"
  year: 1996
  venue: "Journal of Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Adjustments+to+Zatsiorsky-Seluyanov's+segment+inertia+parameters"
  clusters: ["biomechanics", "anthropometry"]
  concepts: ["body segment parameters", "inertia tensors", "center of mass"]
  related_ids: ["dumas2007adjustments", "dempster1955space"]
  references_out_ids: ["dumas2007adjustments"]

- id: dumas2007adjustments
  title: "Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters"
  authors:
    - "Raphaël Dumas"
    - "et al."
  year: 2007
  venue: "Journal of Biomechanics"
  scholar_link: "https://scholar.google.com/scholar?q=Adjustments+to+Zatsiorsky-Seluyanov's+segment+inertia+parameters+Dumas"
  clusters: ["biomechanics", "anthropometry"]
  concepts: ["segmental inertia", "kinetics", "scaling"]
  related_ids: ["deleva1996adjustments"]
  references_out_ids: []

- id: pandy2001computer
  title: "Computer modeling and simulation of human movement"
  authors:
    - "Marcus G. Pandy"
  year: 2001
  venue: "Annual Review of Biomedical Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=Computer+modeling+and+simulation+of+human+movement+Pandy"
  clusters: ["biomechanics", "simulation"]
  concepts: ["forward dynamics", "muscle models", "optimal control"]
  related_ids: ["zajac1989determining", "anderson2001dynamic"]
  references_out_ids: ["anderson2001dynamic"]

- id: pearl1995causality
  title: "Causality: Models, Reasoning, and Inference"
  authors:
    - "Judea Pearl"
  year: 2000
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Causality+Models+Reasoning+and+Inference+Pearl"
  clusters: ["causality", "statistics"]
  concepts: ["counterfactuals", "do-calculus", "structural models"]
  related_ids: []
  references_out_ids: ["woodward2003making"]

- id: woodward2003making
  title: "Making Things Happen: A Theory of Causal Explanation"
  authors:
    - "James Woodward"
    - "2003"
  year: 2003
  venue: "Oxford University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Making+Things+Happen+Woodward"
  clusters: ["philosophy of science", "causality"]
  concepts: ["interventionism", "invariance", "manipulability"]
  related_ids: ["pearl1995causality"]
  references_out_ids: []

- id: collins2005efficient
  title: "Efficient bipedal robots based on passive-dynamic walkers"
  authors:
    - "Steve Collins"
    - "Andy Ruina"
    - "Tedrake"
    - "Wisse"
  year: 2005
  venue: "Science"
  scholar_link: "https://scholar.google.com/scholar?q=Efficient+bipedal+robots+based+on+passive-dynamic+walkers+Collins"
  clusters: ["robotics", "passive dynamics"]
  concepts: ["energy efficiency", "passive walking", "trajectory optimization"]
  related_ids: ["mcgeer1990passive"]
  references_out_ids: []

- id: keener1988dynamics
  title: "The dynamics of the golf swing"
  authors:
    - "James P. Keener"
  year: 1988
  venue: "SIAM Journal on Applied Mathematics"
  scholar_link: "https://scholar.google.com/scholar?q=The+dynamics+of+the+golf+swing+Keener"
  clusters: ["golf biomechanics", "applied math"]
  concepts: ["double pendulum", "variable length", "optimization"]
  related_ids: ["cochran1968search"]
  references_out_ids: []

- id: springings2000examining
  title: "Examining the delayed release in the golf swing"
  authors:
    - "Eric J. Sprigings"
    - "Sasho J. MacKenzie"
  year: 2000
  venue: "Sports Engineering"
  scholar_link: "https://scholar.google.com/scholar?q=Examining+the+delayed+release+in+the+golf+swing+Sprigings"
  clusters: ["golf biomechanics", "kinetics"]
  concepts: ["wrist torque", "passive release", "timing"]
  related_ids: ["mackenzie2009three"]
  references_out_ids: []

- id: abraham1978foundations
  title: "Foundations of Mechanics"
  authors:
    - "Ralph Abraham"
    - "Jerrold E. Marsden"
  year: 1978
  venue: "Addison-Wesley"
  scholar_link: "https://scholar.google.com/scholar?q=Foundations+of+Mechanics+Abraham+Marsden"
  clusters: ["mathematical physics", "geometric mechanics"]
  concepts: ["hamiltonian systems", "symplectic geometry", "manifolds"]
  related_ids: ["bullo2004geometric"]
  references_out_ids: ["marsden1999intro"]

- id: shabana2013computational
  title: "Computational Continuum Mechanics"
  authors:
    - "Ahmed A. Shabana"
  year: 2013
  venue: "Cambridge University Press"
  scholar_link: "https://scholar.google.com/scholar?q=Computational+Continuum+Mechanics+Shabana"
  clusters: ["continuum mechanics", "flexible bodies"]
  concepts: ["absolute nodal coordinate formulation", "large deformation"]
  related_ids: ["shabana2020dynamics"]
  references_out_ids: []

- id: pandas_lib
  title: "pandas: powerful Python data analysis toolkit"
  authors:
    - "Wes McKinney"
  year: 2010
  venue: "Python Data Analysis Library"
  scholar_link: "https://scholar.google.com/scholar?q=pandas+python+data+analysis+toolkit"
  clusters: ["software", "data analysis"]
  concepts: ["time series", "dataframes", "io"]
  related_ids: ["scipy_lib"]
  references_out_ids: []

- id: plotly_lib
  title: "Plotly: Interactive Graphing Library"
  authors:
    - "Plotly Technologies Inc."
  year: 2015
  venue: "Montreal, QC"
  scholar_link: "https://scholar.google.com/scholar?q=Plotly+Interactive+Graphing+Library"
  clusters: ["software", "visualization"]
  concepts: ["interactive plots", "dashboards", "web-based"]
  related_ids: []
  references_out_ids: []

- id: brockett1983asymptotic
  title: "Asymptotic stability and feedback stabilization"
  authors:
    - "Roger W. Brockett"
  year: 1983
  venue: "Differential Geometric Control Theory"
  scholar_link: "https://scholar.google.com/scholar?q=Asymptotic+stability+and+feedback+stabilization+Brockett"
  clusters: ["nonlinear control", "mathematical theory"]
  concepts: ["brockett's condition", "stabilization", "vector fields"]
  related_ids: ["bullo2004geometric"]
  references_out_ids: []
```

## C) Reading Paths

### Path 1: Fast Ramp (The "Why" and "How")
*Target: Understand why we separate drift and input, and how to do it.*
1.  **Zajac & Gordon (1989)** - *Determining muscle's force...*. The foundational text for understanding that muscles accelerate everything (dynamical coupling), necessitating careful decomposition.
2.  **McGeer (1990)** - *Passive Dynamic Walking*. The most vivid example of "drift dynamics" doing useful work without input.
3.  **Nesbit (2005)** - *A 3D... study of the golf swing*. A concrete example of inverse dynamics applied to golf.
4.  **Keener (1988)** - *Dynamics of the golf swing*. A classic mathematical treatment of the double pendulum that ignores complex muscle models, focusing on passive physics.
5.  **Pearl (2000)** - *Causality*. (Introduction/Chapter 1). Just to understand the philosophical grounding of "Counterfactuals" ($do(x)$ operator).

### Path 2: Deep Technical (Geometric & Passive Dynamics)
*Target: Rigorous formulation of the control-affine dynamics.*
1.  **Bullo & Lewis (2004)** - *Geometric Control of Mechanical Systems*. The definitive reference for the mathematical structure of mechanical drift.
2.  **Lynch & Park (2017)** - *Modern Robotics*. Excellent modern treatment of Lagrangian dynamics and control.
3.  **Featherstone (2008)** - *Rigid Body Dynamics Algorithms*. Essential for implementing the Recursive Newton-Euler Algorithm (RNEA) needed for ID.
4.  **De Leva (1996)** - *Adjustments to Zatsiorsky...*. You cannot calculate drift without accurate inertia parameters ($M(q)$).
5.  **Sprigings & MacKenzie (2000)** - *Examining the delayed release*. A deep dive into the passive vs. active debate in golf wrist mechanics.
6.  **Abraham & Marsden (1978)** - *Foundations of Mechanics*. For those who want the symplectic geometry underpinnings (advanced).
7.  **Pandy (2001)** - *Computer modeling...*. connects the theory to large-scale simulation.
8.  **Brockett (1983)** - *Asymptotic stability...*. Fundamental constraints on stabilizing driftless or underactuated systems (relevant to the "input" limitations).

### Path 3: Implementation (Counterfactual Engine)
*Target: Building the ZTCF/ZVCF tools.*
1.  **Pinocchio / RBDL** - Libraries for computing `rnea(q, v, a)` (Inverse Dynamics).
2.  **SciPy (`solve_ivp`)** - For integrating the ZTCF trajectory $\dot{x} = f(x)$.
3.  **Pandas** - For managing the time-series data of the swing (kinematics).
4.  **Plotly** - For visualizing the difference between Actual vs. ZTCF trajectories.
5.  **NumPy** - For tensor operations when calculating the Drift vector field manually if needed.
