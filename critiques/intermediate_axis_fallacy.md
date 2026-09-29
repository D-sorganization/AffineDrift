---
title: "Critique: Free-Body Stability and Putter Claims"
description: "Critique and response context for Secondary Axis Stability in Golf Clubs in AffineDrift's control-affine golf-swing framework."
---

## Critique: Secondary Axis Stability in Golf Clubs

## Summary of Concern

The intermediate-axis theorem concerns a torque-free rigid body spinning near a principal-axis motion. It does not establish increased grip effort, poorer face control, or superiority of a central-spine putter in a supported stroke. The original article repeatedly made those inferences without a forced club–shaft–hand model or equipment measurements.

This critique's original response went too far in the other direction: it called the effect necessarily negligible at putting speeds and mixed torque with force units. The defensible objection is the missing model and evidence, not a universal conclusion that inertia-driven effects cannot matter.

## Location

- [Secondary Axis Stability](../articles/secondary-axis-stability.html): free-body theorem, hypothetical inertia comparison, practical design claims and control-theory synthesis.
- The article's accessible summary and critic/author dialogue previously repeated stronger performance claims than the mechanics supported.

## Nature of the Issue

For distinct principal moments $I_1<I_2<I_3$, linearization of torque-free rotation about axis 2 gives the transverse growth rate

$$
\sigma=|\Omega|\sqrt{
\frac{(I_3-I_2)(I_2-I_1)}{I_1I_3}}.
$$

The relevant finite-interval quantity is $\sigma T$, with the initial perturbation and validity of the linear model also specified. The quadratic scaling of $\omega\times I\omega$ does not make this first-order growth rate quadratic in nominal spin. Nor is its time constant simply $1/|\Omega|$ independent of inertia ratios.

An attached club has applied forces and couples, support motion and potentially flexible states. The corresponding perturbation system can differ from the free-body one. Grip stiffness and damping should be modeled or measured; their dominance cannot be asserted from a low angular speed alone. Conversely, the presence of a hand constraint does not automatically prove every possible forced mode stable.

## Why This Is a Problem

The original design ranking used $I_3-I_2$ as an instability indicator and treated its halving as a stability improvement. The actual rate contains both moment gaps and the product $I_1I_3$. Using the article's hypothetical spectra, the rate coefficient is about 0.76709 for A and 0.48529 for B. B has 36.7% lower growth at equal spin rate, but 15.3% higher growth at equal angular momentum along the respective intermediate axes. Neither condition alone represents a measured putting stroke.

The original grid-model attribution lacks a reproducible geometry or calculation. The corrected article labels these numbers hypothetical and separates principal moments from physical head-axis orientation. A smaller moment gap does not identify a mass layout or show that a player will deliver the face more consistently.

Torque comparisons require **N·m**, a common reference point and the same component. Statements comparing a gyroscopic moment in millinewtons with a grip torque in newtons are dimensionally invalid. Collision effects are often usefully expressed as angular impulses, in N·m·s; comparing them with pre-impact torque amplitudes additionally requires the time history.

## Evidence / References

[MIT's rigid-body chapter, §2.4](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/6fe39e8d5ce4ce746ca256dfea665eda_MIT8_09F14_Chapter_2.pdf) derives the Euler balance and free principal-axis perturbation result. It does not validate a putter design. The revised article supplies the explicit table arithmetic and connects the free model to the externally forced balance. Repository tests independently compare component growth rates with finite-difference Jacobians and check the fixed-spin/fixed-momentum reversal.

## Severity

**High for the original inference.** The error changes the article's central engineering conclusion. Correcting it does not establish that any particular architecture is beneficial or harmful to golfers.

## Suggested Remedies

Retain the free-body derivation as a bounded mechanical example. State the support, actuation, deformation and comparison conditions needed for the stroke. Remove unsupported benefits, neural explanations and equipment recommendations. Evaluate impact response and pre-impact delivery together, using specified outputs and uncertainty.

Diagonalizing a tensor by changing coordinates does not improve the physical club. Physically aligning principal directions with a selected motion or load can alter a response, but requires a declared experiment. Do not substitute “inertial alignment” for “stability” and retain the same unverified performance conclusion. The corrected article addresses the mathematical overreach; comparative player outcomes remain unestablished.
