# Bibliography: Inference from Inverse Dynamics

## Concept Map

*   **Inverse Dynamics (ID)**: The computational process of determining the forces and torques required to produce a given motion.
*   **Control-Affine System**: A dynamical system where the control input enters linearly: $\dot{x} = f(x) + g(x)u$.
*   **Recursive Newton-Euler Algorithm (RNEA)**: An efficient $O(n)$ algorithm for computing inverse dynamics in kinematic chains.
*   **Drift Vector Field**: The unforced dynamics ($f(x)$) representing passive evolution under gravity, inertia, and constraints.
*   **Mass Matrix ($M(q)$)**: The symmetric, positive-definite matrix representing the inertial coupling between generalized coordinates.
*   **Coriolis and Centrifugal Forces**: Velocity-dependent fictitious forces arising from non-inertial reference frames in rotating links.
*   **Residual Analysis**: The practice of quantifying the error between measuring ground reaction forces and those predicted by inverse dynamics.
*   **Static Optimization**: A method to resolve the muscle redundancy problem at each time step, often used after ID.
*   **Zero Dynamics**: The internal dynamics of a system when the output is constrained to zero (related to ZTCF).

## Bibliography

bibliography:
  - id: Featherstone2008
    title: "Rigid Body Dynamics Algorithms"
    authors: Roy Featherstone
    year: 2008
    venue: Springer
    scholar_link: https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms
    clusters: [Robotics, Multibody Dynamics]
    concepts: [RNEA, ABA, Spatial Algebra]
    related_ids: [Lynch2017, Murray1994]
    references_out_ids: [PinocchioLib, RBDL]

  - id: Winter2009
    title: "Biomechanics and Motor Control of Human Movement"
    authors: David A. Winter
    year: 2009
    venue: Wiley
    scholar_link: https://scholar.google.com/scholar?q=Winter+Biomechanics+and+Motor+Control+of+Human+Movement
    clusters: [Biomechanics]
    concepts: [Inverse Dynamics, EMG, Kinematics]
    related_ids: [Zajac1989]
    references_out_ids: [OpenSim]

  - id: Murray1994
    title: "A Mathematical Introduction to Robotic Manipulation"
    authors: Richard M. Murray, Zexiang Li, S. Shankar Sastry
    year: 1994
    venue: CRC Press
    scholar_link: https://scholar.google.com/scholar?q=Murray+Li+Sastry+Mathematical+Introduction+to+Robotic+Manipulation
    clusters: [Robotics, Control Theory]
    concepts: [Affine Systems, Lie Brackets, Exponential Map]
    related_ids: [Lynch2017]
    references_out_ids: [Bullo2005]

  - id: Lynch2017
    title: "Modern Robotics: Mechanics, Planning, and Control"
    authors: Kevin M. Lynch, Frank C. Park
    year: 2017
    venue: Cambridge University Press
    scholar_link: https://scholar.google.com/scholar?q=Lynch+Park+Modern+Robotics
    clusters: [Robotics]
    concepts: [Screw Theory, Product of Exponentials, Lagrangian Dynamics]
    related_ids: [Murray1994, Featherstone2008]
    references_out_ids: [PinocchioLib]

  - id: Hatze2002
    title: The fundamental problem of myoskeletal inverse dynamics and its implications
    authors: H. Hatze
    year: 2002
    venue: Journal of Biomechanics
    scholar_link: https://scholar.google.com/scholar?q=Hatze+The+fundamental+problem+of+myoskeletal+inverse+dynamics
    clusters: [Biomechanics, Theory]
    concepts: [Indeterminacy, Muscle Redundancy, Measurement Error]
    related_ids: [Winter2009]

  - id: Kuo1998
    title: A least-squares estimation approach to improving the accuracy of inverse dynamics computations
    authors: A. D. Kuo
    year: 1998
    venue: Journal of Biomechanical Engineering
    scholar_link: https://scholar.google.com/scholar?q=Kuo+least-squares+estimation+approach+inverse+dynamics
    clusters: [Biomechanics, Optimization]
    concepts: [Residual Reduction, Sensor Fusion]
    related_ids: [Dumas2007]

  - id: Dumas2007
    title: Adjustment of joint moments to ensure dynamic consistency
    authors: R. Dumas, L. Cheze, J.P. Verriest
    year: 2007
    venue: Journal of Applied Biomechanics
    scholar_link: https://scholar.google.com/scholar?q=Dumas+Adjustment+of+joint+moments+dynamic+consistency
    clusters: [Biomechanics]
    concepts: [Dynamic Consistency, Residuals]
    related_ids: [Kuo1998]

  - id: Slotine1991
    title: "Applied Nonlinear Control"
    authors: Jean-Jacques Slotine, Weiping Li
    year: 1991
    venue: Prentice Hall
    scholar_link: https://scholar.google.com/scholar?q=Slotine+Li+Applied+Nonlinear+Control
    clusters: [Control Theory]
    concepts: [Feedback Linearization, Lyapunov Stability, Affine Systems]
    related_ids: [Murray1994]
    references_out_ids: [Khalil2002]

  - id: Zajac1989
    title: Muscle and tendon: properties, models, scaling, and application to biomechanics and motor control
    authors: F. E. Zajac
    year: 1989
    venue: Critical Reviews in Biomedical Engineering
    scholar_link: https://scholar.google.com/scholar?q=Zajac+Muscle+and+tendon+properties+models
    clusters: [Biomechanics, Muscle Physiology]
    concepts: [Hill-type Muscle Model, Actuation Dynamics]
    related_ids: [Winter2009]

  - id: PinocchioLib
    title: "Pinocchio: An efficient and versatile rigid body dynamics library"
    authors: Justin Carpentier, et al.
    year: 2019
    venue: IEEE RAS
    scholar_link: https://scholar.google.com/scholar?q=Pinocchio+efficient+versatile+rigid+body+dynamics+library
    clusters: [Software, Robotics]
    concepts: [RNEA, CRBA, ABA]
    related_ids: [Featherstone2008]

  - id: OpenSim
    title: "OpenSim: open-source software to create and analyze dynamic simulations of movement"
    authors: Scott L. Delp, et al.
    year: 2007
    venue: IEEE Transactions on Biomedical Engineering
    scholar_link: https://scholar.google.com/scholar?q=Delp+OpenSim+open-source+software
    clusters: [Software, Biomechanics]
    concepts: [Musculoskeletal Modeling, Inverse Kinematics, CMC]
    related_ids: [Winter2009, Zajac1989]

  - id: Bullo2005
    title: "Geometric Control of Mechanical Systems"
    authors: Francesco Bullo, Andrew D. Lewis
    year: 2005
    venue: Springer
    scholar_link: https://scholar.google.com/scholar?q=Bullo+Lewis+Geometric+Control+of+Mechanical+Systems
    clusters: [Control Theory, Mathematics]
    concepts: [Lagrangian Mechanics, Connection Theory, Nonholonomic Systems]
    related_ids: [Murray1994]

  - id: Khalil2002
    title: "Nonlinear Systems"
    authors: Hassan K. Khalil
    year: 2002
    venue: Prentice Hall
    scholar_link: https://scholar.google.com/scholar?q=Khalil+Nonlinear+Systems
    clusters: [Control Theory]
    concepts: [Stability Analysis, Nonlinear Dynamics]
    related_ids: [Slotine1991]

## Reading Paths

### Path 1: Fast Ramp (Foundations)
1.  **Winter2009**: The standard introduction to Inverse Dynamics in human movement.
2.  **Featherstone2008**: The definitive guide to the algorithms (RNEA) used to compute it efficiently.
3.  **Hatze2002**: A critical look at why "calculating torques" is not the same as "knowing muscle forces."
4.  **OpenSim**: The primary tool used by the community to perform these analyses.
5.  **Dumas2007**: Practical methods for dealing with the fact that measured forces and motions never perfectly match (residuals).

### Path 2: Deep Technical (The Math of Affine Systems)
1.  **Murray1994**: Establishes the $\dot{x} = f(x) + g(x)u$ framework used in the AffineDrift theory.
2.  **Lynch2017**: A modern, geometric treatment of multibody dynamics (Screw Theory).
3.  **Slotine1991**: How to control these systems (Feedback Linearization, Sliding Modes).
4.  **Bullo2005**: Advanced geometric mechanics for underactuated systems.
5.  **Khalil2002**: Rigorous stability analysis for nonlinear systems.
6.  **Kuo1998**: Optimization techniques for reconciling measurement noise in ID.
7.  **Zajac1989**: The link between the calculated torque and the actual biological actuator.
8.  **Pandy2001**: Computer modeling and simulation of human movement (Canonical optimization review).

### Path 3: Implementation (Solvers & Code)
1.  **PinocchioLib**: State-of-the-art C++ / Python library for rigid body algorithms.
2.  **OpenSim**: User-friendly GUI and API for biomechanics.
3.  **RBDL**: Rigid Body Dynamics Library (C++).
4.  **SciPy**: For implementing custom optimization routines to minimize residuals.
5.  **DartLib**: Dynamic Animation and Robotics Toolkit (Simulates contacts/constraints well).
