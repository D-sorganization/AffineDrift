# Evidence Map: Wrist Constraints, Grip Geometry and Face Control

This companion to [the wrist article](wrist-universal-joint.qmd) separates
mechanical identities, software definitions and empirical observations. A
reference that explains a method does not establish that a particular golf
model implements it correctly. A simulation alone does not establish a human
performance advantage.

## Mechanics and Software Definitions

| Source                                                                                                                                  | Reviewed Material and Supported Use                                                   | Boundary                                                                                                        |
| --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Lynch and Park, _Modern Robotics_, [Section 8.7](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/) | Technical transcript: workless constraints, multipliers and projected dynamics        | Does not make reactions independent of actuator inputs                                                          |
| MathWorks, [Universal Joint: Multibody](https://www.mathworks.com/help/sm/ref/universaljoint.html)                                      | Joint rotations, actuation, internal mechanics and sensing                            | Two rotational primitives; documentation does not validate the author's historical model                        |
| MathWorks, [Force and Torque Sensing](https://www.mathworks.com/help/sm/ug/force-and-torque-sensing.html)                               | Technical documentation: primitive/composite signals, measurement frame and direction | Three measured torque components are not three actuator commands                                                |
| MathWorks, [Universal Joint: Driveline](https://www.mathworks.com/help/sdl/ref/universaljoint.html)                                     | Supported-shaft description and kinematic relation                                    | A different assembly from a freely moving two-axis wrist; reconcile phase conventions before comparing formulas |

The article independently derives its moving reaction axis, actuator-dependent
multiplier, joint-pair power balance, wrench transport and face sensitivity.
The [Cardan derivation](../content/wrist-as-universal-joint/MATHEMATICAL_DERIVATION.md)
checks its phase convention by differentiating the angle relation and
integrating the speed ratio over a revolution. Multiplication by a deliberately
defined reciprocal is only an internal consistency check.

## Anatomical and Motor-Control Evidence

| Source                                                                                                                                                           | Evidence Reviewed and Appropriate Use                                                        | What It Does Not Establish                                                    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Crisco et al. (2011), [_The Mechanical Axes of the Wrist Are Oriented Obliquely to the Anatomical Axes_](https://pubmed.ncbi.nlm.nih.gov/21248214/)              | Abstract and record; six cadaver wrists; motivates separating mechanical and anatomical axes | Golf-specific dynamic muscle control or superiority of a grip                 |
| Crisco et al. (2005), [_In Vivo Radiocarpal Kinematics and the Dart Thrower's Motion_](https://pubmed.ncbi.nlm.nih.gov/16322624/)                                | Abstract and record; in-vivo carpal motion; motivates qualification of ideal hinge geometry  | The separate 2011 mechanical-axes experiment or a calibrated golf wrist model |
| Scholz and Schöner (1999), [_The Uncontrolled Manifold Concept: Identifying Control Variables for a Functional Task_](https://pubmed.ncbi.nlm.nih.gov/10382616/) | Abstract and record; sit-to-stand task; analysis of variability relative to a task variable  | That golf constraint loads automatically occupy a harmless subspace           |

The Crisco studies must not be blended into one date, sample or experiment.
Uncontrolled-manifold analysis does not prove that the nervous system ignores
all variation in a task Jacobian's instantaneous null space. Such directions
can also influence the task later through the dynamics.

## Golf Evidence and Validation Scope

| Source                                                                                                                                                                                                                          | Evidence Reviewed and Appropriate Use                                                 | Remaining Limit                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Coleman and Rankin (2005), [_A Three-Dimensional Examination of the Planar Nature of the Golf Swing_](https://pubmed.ncbi.nlm.nih.gov/15966340/), _Journal of Sports Sciences_ 23(3), 227–234; DOI 10.1080/02640410410001730179 | Abstract and record; seven golfers; changing swing geometry                           | Does not test a finger-versus-palm grip intervention                                                                                                           |
| MacKenzie and Sprigings (2009), [_A Three-Dimensional Forward Dynamics Model of the Golf Swing_](https://doi.org/10.1007/s12283-009-0020-9), _Sports Engineering_ 11(4), 165–175                                                | Record and author-hosted methods excerpt; full paper not reviewed for this correction | The excerpt describes single-camera two-dimensional comparison with one golfer; this cannot establish population-level three-dimensional face-control accuracy |
| MacKenzie (2012), [_Club Position Relative to the Golfer's Swing Plane Meaningfully Affects Swing Dynamics_](https://pubmed.ncbi.nlm.nih.gov/22900397/), _Sports Biomechanics_ 11(2), 149–164; DOI 10.1080/14763141.2011.638388 | Abstract and record; model comparison of club positions                               | Does not isolate grip geometry as a causal human intervention                                                                                                  |
| Nesbit and Serrano (2005), [_Work and Power Analysis of the Golf Swing_](https://www.jssm.org/hfabst.php?id=jssm-04-520.xml)                                                                                                    | Abstract; four amateur golfers; context for work/power accounting                     | Does not identify an optimal grip or justify the demonstration inertia ratio                                                                                   |

Publication dates follow the cited journal records. No numerical example in
the wrist article is presented as a measured result from an abstract-only review.

## Reading Sequence

1. Define independent joint coordinates and allowed relative velocities. Two
   coordinates with two independent inputs can be fully actuated. Removing a
   prohibited spatial rotation does not add an unactuated independent coordinate.
2. Derive reactions from complete dynamics. A holonomic constraint may be
   expressed as a velocity equation. Its reaction annihilates allowed relative
   velocities, not necessarily actuator input directions.
3. Transform the complete wrench and inertia to a declared point and frame;
   include support acceleration for a moving grip point.
4. Define the delivery variable and propagate perturbations to impact. Torque
   projection alone does not determine face yaw or its variance.
5. Use anatomical and golf evidence to choose calibration and measurements.
   Separate fixed-input, fixed-motion and reoptimized-control comparisons.

## Bibliographic Integrity

The previous bibliography included speculative citation-network edges, with
older sources purportedly citing later publications. Those edges have been
removed. Relationships here are editorial connections, not assertions about
papers' reference lists. Unverified peripheral entries have also been removed
rather than used as evidence for numerical parameters or grip recommendations.
Restore them only after checking the original source and the precise claim.
