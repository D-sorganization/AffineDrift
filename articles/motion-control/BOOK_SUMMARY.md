# Control Is Motion - Complete Textbook

## Book Overview

This textbook presents a revolutionary framework for nonlinear control theory,
shifting from the classical "setpoint control" paradigm to a "trajectory control"
approach specifically designed for systems that move through the world.

## Key Themes

- **Control is Motion, not Destination**: The fundamental insight that control
  systems should be designed around trajectories, not fixed points
- **Moving Target Systems**: Systems whose objectives are defined by kinematics
  at specific intersections, independent of timing
- **Geometric Approach**: Treating trajectories as geometric objects with
  intrinsic curvature and structure
- **Underactuation as Advantage**: Exploiting passive dynamics rather than
  fighting them

## Chapter Summary

### Chapter 1: Throwing Away the Target

- Introduces the central thesis: "Control is motion"
- Contrasts classical setpoint control with trajectory control
- Defines moving target systems using the golf swing as primary example
- Establishes the philosophical and mathematical foundation

### Chapter 2: Curves in State Space

- Mathematical treatment of trajectories as geometric curves
- Arc length parameterization and path-timing separation
- Curvature, torsion, and their relationship to control difficulty
- Frenet-Serret frames and coordinate-independent descriptions

### Chapter 3: Configuration Manifolds

- Beyond Euclidean state spaces: Lie groups and curved manifolds
- Special treatment of rotational motion and SO(3)
- Riemannian metrics derived from kinetic energy
- Constraints and submanifolds in mechanical systems

### Chapter 4: Orbital Stability and Transverse Linearization

- Rethinking stability for moving systems
- Orbital stability vs. classical Lyapunov stability
- Transverse linearization and moving Poincaré sections
- Floquet theory for periodic motions

### Chapter 5: Underactuation and Passive Dynamics

- Embracing underactuation as a design principle
- Zero dynamics and the structure of underactuated systems
- The whip effect and sequential energy transfer
- Applications to the golf swing kinetic chain

### Chapter 6: Trajectory Optimization

- Moving target optimal control problems
- Direct collocation methods for complex systems
- Multi-phase optimization and cost function design
- From optimization to implementable trajectories

### Chapter 7: Funnel Synthesis

- Beyond point tracking: finite-time guarantees
- Forward invariant funnels and barrier functions
- Sum-of-squares programming for funnel computation
- Robust funnels under model uncertainty

### Chapter 8: Phase-Variable Control

- Decoupling path shape from timing
- Virtual constraints and hybrid zero dynamics
- Central pattern generators as phase oscillators
- Applications to locomotion and rhythmic motions

### Chapter 9: Stochastic Trajectories and Motor Variability

- Signal-dependent noise in biological actuators
- Minimum-variance theory of human movement
- Why optimal trajectories are naturally smooth
- Covariance steering for robust trajectory design

### Chapter 10: Learning to Move

- Iterative learning control for trajectory improvement
- Policy search and trajectory libraries
- Maintaining stability while adapting performance
- Applications to athletic skill development

### Chapter 11: Case Study - The Complete Golf Swing

- Full application of the entire framework
- 15-DOF musculoskeletal model optimization
- Funnel synthesis for the complete swing
- Integration of all theoretical concepts

## Technical Features

- Rigorous mathematical treatment with geometric insight
- Extensive use of examples from athletics and robotics
- Practical algorithms and computational methods
- End-of-chapter exercises ranging from conceptual to computational
- Beautiful visual presentations using TikZ graphics

## Target Audience

- Graduate students in robotics, control theory, and biomechanics
- Researchers working on underactuated systems and trajectory control
- Engineers designing systems for complex motions
- Anyone interested in the intersection of control theory and human movement

## Unique Contributions

This textbook is the first comprehensive treatment of trajectory-based control
theory for moving target systems. It bridges classical control theory with
modern geometric methods, providing both theoretical foundations and practical
tools for designing controllers for systems that must move through the world
with purpose and precision.
