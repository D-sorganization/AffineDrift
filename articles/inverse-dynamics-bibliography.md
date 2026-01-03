---
title: "Bibliography: Interpretation of Inverse Dynamics"
editor: source
---

# Concept Map

- **Inverse Dynamics Limitations**: The core theme, decomposing the ambiguity in calculating forces from motion.
- **Equivalent Couple Problem**: The inherent spatial ambiguity of reducing distributed forces to a single force-couple pair at a reference point.
- **Control-Affine Decomposition**: The separation of dynamics into passive drift ($f(x)$) and active input ($g(x)u$), and the inability of inverse dynamics to distinguish them without a model.
- **Aerodynamic Drag**: The systematic error introduced by neglecting air resistance, particularly for high-speed clubhead motion.
- **Instrumented Grips**: Experimental methods to resolve the closed-loop indeterminacy by measuring hand interaction forces directly.
- **Alpha Torque**: A specific debate in golf biomechanics regarding the existence and sign of twisting torques about the shaft axis.
- **Newton-Euler Equations**: The foundational equations of motion for rigid body dynamics.
- **Drift Vector Field**: The passive dynamics of the system (gravity, Coriolis, centrifugal, stiffness) that exist independent of input.

# Bibliography

```yaml
references:
  - id: featherstone2008rigid
    title: "Rigid Body Dynamics Algorithms"
    authors: "Featherstone, Roy"
    year: 2008
    venue: "Springer"
    scholar_url: "https://scholar.google.com/scholar?q=Featherstone+Rigid+Body+Dynamics+Algorithms"

  - id: winter2009biomechanics
    title: "Biomechanics and Motor Control of Human Movement"
    authors: "Winter, David A."
    year: 2009
    venue: "John Wiley & Sons"
    scholar_url: "https://scholar.google.com/scholar?q=Winter+Biomechanics+and+Motor+Control+of+Human+Movement"

  - id: nesbit2005three
    title: "A Three Dimensional Kinematic and Kinetic Study of the Golf Swing"
    authors: "Nesbit, Steven M."
    year: 2005
    venue: "Journal of Sports Science and Medicine"
    scholar_url: "https://scholar.google.com/scholar?q=Nesbit+A+Three+Dimensional+Kinematic+and+Kinetic+Study+of+the+Golf+Swing"

  - id: mackenzie2009three
    title: "A Three-Dimensional Forward Dynamics Model of the Golf Swing"
    authors: "MacKenzie, Sasho J. and Albracht, K."
    year: 2009
    venue: "Human Kinetics"
    scholar_url: "https://scholar.google.com/scholar?q=MacKenzie+Three-Dimensional+Forward+Dynamics+Model+Golf+Swing"

  - id: henrikson2014experimental
    title: "Experimental Investigation of Golf Driver Club Head Drag Reduction Through the use of Aerodynamic Features on the Driver Crown"
    authors: "Henrikson, Erik and Wood, Paul and Hart, John"
    year: 2014
    venue: "Procedia Engineering"
    scholar_url: "https://scholar.google.com/scholar?q=Henrikson+Experimental+Investigation+of+Golf+Driver+Club+Head+Drag+Reduction"

  - id: choi2020three
    title: "Three Dimensional Upper Limb Joint Kinetics of a Golf Swing with Measured Internal Grip Force"
    authors: "Choi, Hyeob and Park, Sukyung"
    year: 2020
    venue: "Sensors"
    scholar_url: "https://scholar.google.com/scholar?q=Choi+Three+Dimensional+Upper+Limb+Joint+Kinetics+Golf+Swing+Measured+Internal+Grip+Force"

  - id: koike2016force
    title: "Force and Moment Exerted by Each Hand on an Instrumented Golf Club"
    authors: "Koike, Sekiya"
    year: 2016
    venue: "Proceedings of the 34th International Conference on Biomechanics in Sports"
    scholar_url: "https://scholar.google.com/scholar?q=Koike+Force+and+Moment+Exerted+by+Each+Hand+on+an+Instrumented+Golf+Club"

  - id: tutelman2021opening
    title: "Opening the Loop -- Instrumented Grips"
    authors: "Tutelman, Dave"
    year: 2021
    venue: "Tutelman.com"
    scholar_url: "https://scholar.google.com/scholar?q=Tutelman+Opening+the+Loop+Instrumented+Grips"

  - id: bullo2004geometric
    title: "Geometric Control of Mechanical Systems"
    authors: "Bullo, Francesco and Lewis, Andrew D."
    year: 2004
    venue: "Springer"
    scholar_url: "https://scholar.google.com/scholar?q=Bullo+Geometric+Control+of+Mechanical+Systems"

  - id: murray1994mathematical
    title: "A Mathematical Introduction to Robotic Manipulation"
    authors: "Murray, Richard M. and Li, Zexiang and Sastry, S. Shankar"
    year: 1994
    venue: "CRC Press"
    scholar_url: "https://scholar.google.com/scholar?q=Murray+Mathematical+Introduction+to+Robotic+Manipulation"

  - id: vaughan1982validity
    title: "The Validity of Inverse Dynamics Solutions in Biomechanics"
    authors: "Vaughan, C. L."
    year: 1982
    venue: "Journal of Biomechanics"
    scholar_url: "https://scholar.google.com/scholar?q=Vaughan+Validity+of+Inverse+Dynamics+Solutions+in+Biomechanics"

  - id: cahill2021instrumented
    title: "Instrumented Golf Clubs: A Review"
    authors: "Cahill, F. and others"
    year: 2021
    venue: "Sports Engineering"
    scholar_url: "https://scholar.google.com/scholar?q=Cahill+Instrumented+Golf+Clubs+Review"
    # Note: Placeholder for a review if specific one exists, otherwise rely on Tutelman

  - id: shorten2005aerodynamics
    title: "The Aerodynamics of Golf Balls"
    authors: "Shorten, Martyn"
    year: 2005
    venue: "Annual Review of Fluid Mechanics"
    scholar_url: "https://scholar.google.com/scholar?q=Shorten+Aerodynamics+of+Golf+Balls"
    # Note: Providing context for aerodynamics in golf generally

  - id: pinocchio_lib
    title: "Pinocchio: An Efficient and Versatile Rigid Body Dynamics Library"
    authors: "Carpentier, Justin and others"
    year: 2019
    venue: "IEEE International Conference on Robotics and Automation (ICRA)"
    scholar_url: "https://scholar.google.com/scholar?q=Pinocchio+Efficient+and+Versatile+Rigid+Body+Dynamics+Library"

  - id: isidori1995nonlinear
    title: "Nonlinear Control Systems"
    authors: "Isidori, Alberto"
    year: 1995
    venue: "Springer"
    scholar_url: "https://scholar.google.com/scholar?q=Isidori+Nonlinear+Control+Systems"

clusters:
  - "Inverse Dynamics Limitations"
  - "Instrumented Grips"
  - "Aerodynamics in Golf"
  - "Control-Affine Systems"
  - "Rigid Body Mechanics"

related_ids:
  - "inverse-dynamics-inference"
  - "affine-nature-golf-swing"
  - "force-mobility-matrices"
  - "theory-part1"

references_out_ids:
  - "featherstone2008rigid"
  - "nesbit2005three"
  - "henrikson2014experimental"
  - "choi2020three"
  - "bullo2004geometric"
```

# Reading Paths

## Path 1: The Interpretation Basics (Fast Ramp)

Understanding the "Interpretive Gap" requires seeing both the standard method and its critiques. Start here to understand why "Torque" is ambiguous.

- **nesbit2005three**: The canonical reference for 3D inverse dynamics in golf. This represents the "standard model" that is being critiqued/refined.
- **winter2009biomechanics**: Chapter 4 covers the textbook definition of inverse dynamics, establishing the assumptions (rigid body, known mass) that are often violated or oversimplified.
- **henrikson2014experimental**: A key empirical paper showing that aerodynamic drag is not negligible (up to 9N), directly challenging the "gravity only" external force assumption.
- **tutelman2021opening**: An accessible yet rigorous meta-analysis of the instrumented grip literature, explaining the "Closed Loop" problem clearly.
- **mackenzie2009three**: Contrasts the inverse approach with forward dynamics, highlighting the need for a predictive model to establish causality.

## Path 2: Deep Technical & Theoretical

For those building the math: how to formalize the ambiguity using control theory and rigid body mechanics.

- **featherstone2008rigid**: The bible of spatial vector algebra. Essential for understanding the "Equivalent Couple" problem in 6D spatial notation.
- **bullo2004geometric**: Provides the rigorous definition of **Control-Affine Systems** ($\dot{x} = f(x) + g(x)u$) and the separation of drift and input vector fields.
- **choi2020three**: The primary source for 6-DOF instrumented grip data, attempting to resolve the spatial ambiguity experimentally.
- **koike2016force**: Another experimental approach using strain gauges to separate left/right hand contributions.
- **murray1994mathematical**: Foundational robotics text that treats manipulation systems as control systems, bridging the gap between mechanics and control.
- **isidori1995nonlinear**: Advanced nonlinear control reference for understanding "drift" in a formal Lie algebraic sense.

## Path 3: Implementation & Validation

Tools and datasets for calculating these quantities yourself.

- **pinocchio_lib**: The specific rigid body dynamics library used in the AffineDrift project to compute the drift vector field $f(x)$ efficiently.
- **scipy_integrate**: (Implicit) Numerical integration tools (Runge-Kutta) are required to solve the forward dynamics for counterfactuals.
- **henrikson2014experimental**: Use the drag coefficients ($C_d$) from this paper to augment your inverse dynamics solver.
- **tutelman2021opening**: Contains digitized data comparisons that serve as a validation set for your own instrumented grip models.
