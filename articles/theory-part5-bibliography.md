# Bibliography for Affine Control Interpretation of the Golf Swing — Part 5: Simulink Model

## A) Concept Map

- **Forward Dynamics Modeling**

  - **Simulink Implementation**: Using a block-diagram environment for equation solving.
  - **Flexible Beam Theory**: Modeling the golf shaft using finite-dimensional modal approximations (Euler-Bernoulli).
  - **Integration**: Using stiff solvers (`ode15s`) to handle the timescale separation between rigid body motion and shaft vibrations.

- **Force Decomposition**

  - **Zero Torque Counterfactual (ZTCF)**: Isolating the "passive" component of motion by killing active inputs.
  - **Zero Velocity Counterfactual (ZVCF)**: Isolating the configuration-dependent forces (gravity, stiffness) from velocity-dependent ones.
  - **Drift vs. Input**: $\tau_{\mathrm{total}} = \tau_{\mathrm{drift}} + \tau_{\mathrm{input}}$.
  - **Kill-Switches**: The numerical technique used to reset integrators/torques to evaluate counterfactuals.

- **Interaction Forces**

  - **Hand-Club Coupling**: The forces transmitted between the golfer and the club.
  - **Passive Momentum**: The contribution of the club's inertia and velocity to the felt force.

- **Validation**
  - **Numerical Identity**: $F_{\mathrm{total}} - F_{\mathrm{ZTCF}} = F_{\mathrm{ZVCF}}$.
  - **Trajectory Comparison**: Verifying that the model produces realistic clubhead speeds and kinematics.

## B) Bibliography (YAML)

```yaml
- id: olson2024two
  title: Two Hand Golf Swing Model
  authors:
    - Dieter Olson
  year: 2024
  venue: MATLAB Central File Exchange
  scholar_link: https://scholar.google.com/scholar?q=Dieter+Olson+Two+Hand+Golf+Swing+Model
  clusters:
    - simulation_and_modeling
    - golf_dynamics
    - software
  concepts:
    - forward_dynamics
    - zero_torque_counterfactual
    - simulink_implementation
    - flexible_beams
  related_ids:
    - mackenzie2009three
    - shabana2020dynamics
  references_out_ids:
    - mackenzie2009three
    - nesbit2005three
    - shabana2020dynamics
    - shampine1997matlab
    - featherstone2008rigid

- id: mackenzie2009three
  title: A three-dimensional forward dynamics model of the golf swing
  authors:
    - Sasho J. MacKenzie
    - Eric J. Sprigings
  year: 2009
  venue: Sports Engineering
  scholar_link: https://scholar.google.com/scholar?q=MacKenzie+Sprigings+three-dimensional+forward+dynamics+model+golf+swing
  clusters:
    - golf_dynamics
    - simulation_and_modeling
  concepts:
    - forward_dynamics
    - golf_swing
    - optimization
  related_ids:
    - nesbit2005three
    - sprigings2000insight
  references_out_ids:
    - nesbit2005three
    - sprigings2000insight
    - olson2024two

- id: nesbit2005three
  title: A three dimensional kinematic and kinetic study of the golf swing
  authors:
    - Steven M. Nesbit
  year: 2005
  venue: Journal of Sports Science & Medicine
  scholar_link: https://scholar.google.com/scholar?q=Nesbit+three+dimensional+kinematic+kinetic+study+golf+swing
  clusters:
    - golf_dynamics
    - inverse_dynamics
  concepts:
    - inverse_dynamics
    - joint_kinetics
    - work_and_power
  related_ids:
    - mackenzie2009three
    - sharp2009shoulder
  references_out_ids:
    - mackenzie2009three
    - sharp2009shoulder
    - winter2009biomechanics

- id: shabana2020dynamics
  title: Dynamics of Multibody Systems
  authors:
    - Ahmed A. Shabana
  year: 2020
  venue: Cambridge University Press
  scholar_link: https://scholar.google.com/scholar?q=Shabana+Dynamics+of+Multibody+Systems
  clusters:
    - multibody_dynamics
    - flexible_multibody_dynamics
  concepts:
    - flexible_bodies
    - floating_frame_of_reference
    - lagrangian_dynamics
  related_ids:
    - simo1986dynamics
    - featherstone2008rigid
  references_out_ids:
    - simo1986dynamics
    - featherstone2008rigid
    - meirovitch2001principles

- id: shampine1997matlab
  title: The MATLAB ODE Suite
  authors:
    - Lawrence F. Shampine
    - Mark W. Reichelt
  year: 1997
  venue: SIAM Journal on Scientific Computing
  scholar_link: https://scholar.google.com/scholar?q=Shampine+Reichelt+MATLAB+ODE+Suite
  clusters:
    - numerical_methods
    - simulation_and_modeling
  concepts:
    - stiff_solvers
    - ode15s
    - numerical_integration
  related_ids:
    - hairer1996solving
  references_out_ids:
    - hairer1996solving
    - mathworks2024simscape

- id: featherstone2008rigid
  title: Rigid Body Dynamics Algorithms
  authors:
    - Roy Featherstone
  year: 2008
  venue: Springer
  scholar_link: https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms
  clusters:
    - multibody_dynamics
    - simulation_and_modeling
  concepts:
    - recursive_algorithms
    - spatial_algebra
    - forward_dynamics
  related_ids:
    - lynch2017modern
    - shabana2020dynamics

- id: hairer1996solving
  title: "Solving Ordinary Differential Equations II: Stiff and Differential-Algebraic Problems"
  authors:
    - Ernst Hairer
    - Gerhard Wanner
  year: 1996
  venue: Springer
  scholar_link: https://scholar.google.com/scholar?q=Hairer+Wanner+Solving+Ordinary+Differential+Equations+II
  clusters:
    - numerical_methods
  concepts:
    - stiff_equations
    - dae_solvers
    - implicit_methods
  related_ids:
    - shampine1997matlab

- id: simo1986dynamics
  title: On the dynamics of flexible beams under large overall motions—The plane case
  authors:
    - Juan C. Simo
    - Loc Vu-Quoc
  year: 1986
  venue: Journal of Applied Mechanics
  scholar_link: https://scholar.google.com/scholar?q=Simo+Vu-Quoc+dynamics+flexible+beams+large+overall+motions
  clusters:
    - flexible_multibody_dynamics
  concepts:
    - beam_theory
    - large_deformation
    - geometrically_exact_beam
  related_ids:
    - shabana2020dynamics

- id: lynch2017modern
  title: "Modern Robotics: Mechanics, Planning, and Control"
  authors:
    - Kevin M. Lynch
    - Frank C. Park
  year: 2017
  venue: Cambridge University Press
  scholar_link: https://scholar.google.com/scholar?q=Lynch+Park+Modern+Robotics
  clusters:
    - control_theory
    - multibody_dynamics
  concepts:
    - lagrangian_dynamics
    - control_affine_form
    - lie_groups
  related_ids:
    - spong2005robot
    - featherstone2008rigid

- id: spong2005robot
  title: Robot Modeling and Control
  authors:
    - Mark W. Spong
    - Seth Hutchinson
    - M. Vidyasagar
  year: 2005
  venue: Wiley
  scholar_link: https://scholar.google.com/scholar?q=Spong+Hutchinson+Robot+Modeling+and+Control
  clusters:
    - control_theory
  concepts:
    - control_affine_systems
    - feedback_linearization
    - lagrangian_dynamics
  related_ids:
    - lynch2017modern

- id: mcgeer1990passive
  title: Passive Dynamic Walking
  authors:
    - Tad McGeer
  year: 1990
  venue: The International Journal of Robotics Research
  scholar_link: https://scholar.google.com/scholar?q=McGeer+Passive+Dynamic+Walking
  clusters:
    - passive_dynamics
    - control_theory
  concepts:
    - passive_dynamics
    - limit_cycles
    - drift_dynamics
  related_ids:
    - collins2005efficient

- id: sharp2009shoulder
  title: Shoulder complex kinetics during the golf swing
  authors:
    - N. C. Sharp
  year: 2009
  venue: Proceedings of the Institution of Mechanical Engineers, Part P
  scholar_link: https://scholar.google.com/scholar?q=Sharp+Shoulder+complex+kinetics+golf+swing
  clusters:
    - golf_dynamics
  concepts:
    - joint_kinetics
    - shoulder_mechanics
  related_ids:
    - nesbit2005three

- id: sprigings2000insight
  title: An insight into the importance of wrist torque in driving the golf ball
  authors:
    - Eric J. Sprigings
    - Robert J. Neal
  year: 2000
  venue: Journal of Applied Biomechanics
  scholar_link: https://scholar.google.com/scholar?q=Sprigings+Neal+importance+wrist+torque+golf+ball
  clusters:
    - golf_dynamics
  concepts:
    - wrist_torque
    - forward_dynamics
    - kinetic_chain
  related_ids:
    - mackenzie2009three

- id: meirovitch2001principles
  title: Principles and Techniques of Vibrations
  authors:
    - Leonard Meirovitch
  year: 2001
  venue: Prentice Hall
  scholar_link: https://scholar.google.com/scholar?q=Meirovitch+Principles+and+Techniques+of+Vibrations
  clusters:
    - flexible_multibody_dynamics
    - numerical_methods
  concepts:
    - modal_analysis
    - assumed_modes_method
    - beam_vibration
  related_ids:
    - shabana2020dynamics

- id: kane1985dynamics
  title: "Dynamics: Theory and Applications"
  authors:
    - Thomas R. Kane
    - David A. Levinson
  year: 1985
  venue: McGraw-Hill
  scholar_link: https://scholar.google.com/scholar?q=Kane+Levinson+Dynamics+Theory+and+Applications
  clusters:
    - multibody_dynamics
  concepts:
    - kanes_method
    - multibody_dynamics
    - generalized_speeds
  related_ids:
    - featherstone2008rigid

- id: mathworks2024simscape
  title: Simscape Multibody Documentation
  authors:
    - MathWorks
  year: 2024
  venue: MathWorks
  scholar_link: https://scholar.google.com/scholar?q=Simscape+Multibody+Documentation
  clusters:
    - software
    - simulation_and_modeling
  concepts:
    - multibody_simulation
    - physical_modeling
    - causal_modeling
  related_ids:
    - olson2024two
```

## C) Reading Paths

### Path 1: Fast Ramp (Foundations)

_Target: Understand the simulation context._

1.  **Olson (2024)** - _Two Hand Golf Swing Model_. The codebase for the simulation.
2.  **MacKenzie & Sprigings (2009)** - _Forward dynamics model_. The standard for why we build these models.
3.  **Shampine & Reichelt (1997)** - _MATLAB ODE Suite_. Essential for the numerical "kill switch" implementation.
4.  **Featherstone (2008)** - _Rigid Body Dynamics Algorithms_. The physics engine underlying the blocks.
5.  **Spong et al. (2005)** - _Robot Modeling and Control_. The theoretical language.

### Path 2: Deep Technical (Theory & Methods)

_Target: Master the flexible MBD and stiff integration._

1.  **Shabana (2020)** - _Dynamics of Multibody Systems_. Deep dive into flexible body dynamics.
2.  **Simo & Vu-Quoc (1986)** - _Dynamics of flexible beams_. The rigorous beam theory.
3.  **Hairer & Wanner (1996)** - _Solving ODEs II_. Why stiff solvers are needed.
4.  **Kane & Levinson (1985)** - _Dynamics_. Alternate formulation often used in validation.
5.  **Nesbit (2005)** - _Inverse dynamics_. The counter-perspective to forward simulation.
6.  **McGeer (1990)** - _Passive Dynamic Walking_. The origin of "drift" as a useful concept.
7.  **Lynch & Park (2017)** - _Modern Robotics_. Geometric insights.
8.  **Meirovitch (2001)** - _Vibrations_. Modal analysis background.

### Path 3: Implementation (Software & Validation)

_Target: Replicating the results._

1.  **Olson (2024)** - _Two Hand Golf Swing Model_. (Download from MathWorks).
2.  **Shampine (1997)** - _MATLAB ODE Suite_. (Reference for ode15s/ode23t).
3.  **MathWorks (2024)** - _Simscape Multibody_. (The engine documentation).
4.  **MacKenzie (2009)** - _Validation Data_. Compare swing speeds/torques.
5.  **Sprigings & Neal (2000)** - _Wrist Torque_. Validation of specific joint loading.
