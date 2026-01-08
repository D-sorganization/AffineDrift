# Bibliography: Applications of the Control-Affine Framework

## Concept Map

*   **Counterfactual Analysis (ZTCF)**: Isolating passive mechanical contributions by simulating the system with zero active input ($u=0$).
*   **Inverse Dynamics & Torque Estimation**: Reconstructing input forces ($F_{\text{input}}$) by subtracting calculated passive drift ($F_{\text{drift}}$) from total measured forces.
*   **Flexible Multibody Dynamics**: Modeling the golf shaft not just as a rigid link but as a source of elastic potential energy and structural drift.
*   **Passive Dynamics**: The evolution of the system driven solely by inertia, gravity, and stiffness (the "Drift Field").
*   **Physics-Informed Machine Learning**: Using physical priors (Lagrangian structure, conservation laws) to constrain data-driven models of the swing.

## Bibliography

```yaml
- id: nesbit2005work
  title: Work and Power Analysis of the Golf Swing
  authors: Nesbit, S. M.
  year: 2005
  venue: Journal of Sports Science and Medicine
  scholar_url: https://scholar.google.com/scholar?q=Work+and+Power+Analysis+of+the+Golf+Swing+Nesbit
  clusters:
    - inverse dynamics
    - golf biomechanics
    - energy analysis
  concepts:
    - work-energy
    - hub path
    - torque reconstruction
  related_ids:
    - mackenzie2009three
    - winter2009biomechanics
  references_out_ids:
    - mackenzie2009three
    - winter2009biomechanics
    - featherstone2008rigid

- id: mackenzie2009three
  title: A Three-Dimensional Forward Dynamics Model of the Golf Swing
  authors: MacKenzie, S. J., & Sprigings, E. J.
  year: 2009
  venue: Sports Engineering
  scholar_url: https://scholar.google.com/scholar?q=A+three-dimensional+forward+dynamics+model+of+the+golf+swing+MacKenzie
  clusters:
    - forward dynamics
    - flexible shaft
    - optimization
  concepts:
    - forward simulation
    - shaft deflection
    - optimization
  related_ids:
    - nesbit2005work
    - featherstone2008rigid
  references_out_ids:
    - nesbit2005work
    - friswell1995updating
    - featherstone2008rigid

- id: featherstone2008rigid
  title: Rigid Body Dynamics Algorithms
  authors: Featherstone, R.
  year: 2008
  venue: Springer
  scholar_url: https://scholar.google.com/scholar?q=Rigid+Body+Dynamics+Algorithms+Featherstone
  clusters:
    - multibody dynamics
    - algorithms
    - robotics
  concepts:
    - recursive newton-euler
    - articulated body algorithm
    - spatial algebra
  related_ids:
    - pinocchio_lib
    - jain2010unified
  references_out_ids:
    - pinocchio_lib
    - jain2010unified

- id: todorov2002optimal
  title: Optimal Feedback Control as a Theory of Motor Coordination
  authors: Todorov, E., & Jordan, M. I.
  year: 2002
  venue: Nature Neuroscience
  scholar_url: https://scholar.google.com/scholar?q=Optimal+feedback+control+as+a+theory+of+motor+coordination+Todorov
  clusters:
    - motor control
    - neuroscience
    - optimal control
  concepts:
    - minimum intervention principle
    - uncontrolled manifold
    - synergy
  related_ids:
    - mcgeer1990passive
    - raibert1986legged
  references_out_ids:
    - mcgeer1990passive
    - karniadakis2021pinn

- id: mcgeer1990passive
  title: Passive Dynamic Walking
  authors: McGeer, T.
  year: 1990
  venue: The International Journal of Robotics Research
  scholar_url: https://scholar.google.com/scholar?q=Passive+Dynamic+Walking+McGeer
  clusters:
    - passive dynamics
    - robotics
    - locomotion
  concepts:
    - limit cycles
    - energy efficiency
    - natural dynamics
  related_ids:
    - raibert1986legged
    - todorov2002optimal
  references_out_ids:
    - raibert1986legged
    - todorov2002optimal
    - featherstone2008rigid

- id: brunton_piml_course
  title: "Course: Physics Informed Machine Learning"
  authors: Brunton, S. L.
  year: 2024
  venue: YouTube / University of Washington
  scholar_url: https://scholar.google.com/scholar?q=Physics+Informed+Machine+Learning+Brunton
  clusters:
    - machine learning
    - data-driven physics
    - education
  concepts:
    - SINDy
    - Lagrangian Neural Networks
    - Koopman operator
  related_ids:
    - karniadakis2021pinn
    - friswell1995updating
  references_out_ids:
    - karniadakis2021pinn
    - featherstone2008rigid

- id: karniadakis2021pinn
  title: "Physics-Informed Neural Networks: A Review"
  authors: Karniadakis, G. E., Kevrekidis, I. G., Lu, L., Perdikaris, P., Wang, S., & Yang, L.
  year: 2021
  venue: Nature Reviews Physics
  scholar_url: https://scholar.google.com/scholar?q=Physics-informed+neural+networks+review+Karniadakis
  clusters:
    - machine learning
    - computational physics
    - deep learning
  concepts:
    - PINNs
    - solving PDEs
    - data assimilation
  related_ids:
    - brunton_piml_course
    - todorov2002optimal
  references_out_ids:
    - brunton_piml_course
    - friswell1995updating

- id: friswell1995updating
  title: Finite Element Model Updating in Structural Dynamics
  authors: Friswell, M. I., & Mottershead, J. E.
  year: 1995
  venue: Springer
  scholar_url: https://scholar.google.com/scholar?q=Finite+Element+Model+Updating+in+Structural+Dynamics+Friswell
  clusters:
    - structural dynamics
    - system identification
    - optimization
  concepts:
    - model calibration
    - parameter estimation
    - sensitivity analysis
  related_ids:
    - mackenzie2009three
    - brunton_piml_course
  references_out_ids:
    - mackenzie2009three
    - featherstone2008rigid

- id: raibert1986legged
  title: Legged Robots That Balance
  authors: Raibert, M. H.
  year: 1986
  venue: MIT Press
  scholar_url: https://scholar.google.com/scholar?q=Legged+Robots+That+Balance+Raibert
  clusters:
    - robotics
    - control theory
    - balance
  concepts:
    - dynamic stability
    - hopping
    - active balance
  related_ids:
    - mcgeer1990passive
    - todorov2002optimal
  references_out_ids:
    - mcgeer1990passive
    - featherstone2008rigid

- id: pinocchio_lib
  title: "Pinocchio: An Efficient and Versatile Rigid Body Dynamics Library"
  authors: Carpentier, J., et al.
  year: 2019
  venue: IEEE-RAS International Conference on Humanoid Robots
  scholar_url: https://scholar.google.com/scholar?q=Pinocchio+library+rigid+body+dynamics+Carpentier
  clusters:
    - software
    - robotics
    - optimization
  concepts:
    - analytical derivatives
    - code generation
    - recursive algorithms
  related_ids:
    - featherstone2008rigid
    - jain2010unified
  references_out_ids:
    - featherstone2008rigid
    - jain2010unified

- id: winter2009biomechanics
  title: Biomechanics and Motor Control of Human Movement
  authors: Winter, D. A.
  year: 2009
  venue: Wiley
  scholar_url: https://scholar.google.com/scholar?q=Biomechanics+and+Motor+Control+of+Human+Movement+Winter
  clusters:
    - biomechanics
    - textbook
    - signal processing
  concepts:
    - inverse dynamics
    - electromyography
    - kinematics
  related_ids:
    - nesbit2005work
    - todorov2002optimal
  references_out_ids:
    - nesbit2005work
    - todorov2002optimal

- id: jain2010unified
  title: Robot and Multibody Dynamics
  authors: Jain, A.
  year: 2010
  venue: Springer
  scholar_url: https://scholar.google.com/scholar?q=Robot+and+Multibody+Dynamics+Jain
  clusters:
    - multibody dynamics
    - robotics
    - mathematics
  concepts:
    - spatial operator algebra
    - mass matrix factorization
    - kalman filtering
  related_ids:
    - featherstone2008rigid
    - pinocchio_lib
  references_out_ids:
    - featherstone2008rigid
    - pinocchio_lib
```

## Reading Paths

### Path 1: Fast Ramp (Biomechanics Focus)
Essential reading for understanding the application of mechanical principles to the golf swing.

- **Winter (2009)**: The foundational text for biomechanics and inverse dynamics.
- **Nesbit (2005)**: Direct application of inverse dynamics to calculate work and power in the golf swing.
- **MacKenzie (2009)**: Moving from inverse to forward dynamics, introducing flexible shaft models.
- **McGeer (1990)**: A classic example of "passive dynamics" doing the heavy lifting, analogous to the drift field.
- **Todorov (2002)**: Bridges the gap between mechanics and the nervous system's control strategy.

### Path 2: Deep Technical (Dynamics & Control)
Rigorous mathematical and algorithmic foundations for the simulation framework.

- **Featherstone (2008)**: The bible of recursive rigid body algorithms ($O(N)$ formulations).
- **Jain (2010)**: Advanced spatial operator algebra, essential for understanding mass matrix factorization.
- **Friswell (1995)**: Techniques for updating model parameters to match experimental data (calibration).
- **Raibert (1986)**: Early, impactful work on dynamic balance and active control of unstable systems.
- **Karniadakis (2021)**: Modern techniques for blending physics (ODEs) with neural networks (PINNs).

### Path 3: Implementation (Simulation & ML)
Tools and methods for building the simulators and data pipelines.

- **Pinocchio Lib**: The core C++/Python library used for high-performance rigid body computations.
- **Brunton (Course)**: Practical introduction to data-driven engineering and physics-informed ML.
- **MacKenzie (2009)**: Provides the validation benchmark for forward dynamics simulators.
- **Nesbit (2005)**: Provides the baseline for inverse dynamics validation.
