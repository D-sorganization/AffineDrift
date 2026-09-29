---
title: "Critique: Gravity and Inertia in Putter Design"
description: "Critique and response context for Misattribution of Stability (Gravity vs. Inertia) in Putter Design in AffineDrift's control-affine golf-swing framework."
---

## Critique: Misattribution of Stability (Gravity vs. Inertia) in Putter Design

## Summary of Concern

The original article attributed putter-design benefits to inertial alignment and intermediate-axis dynamics without comparing gravity, applied moments and support conditions. Those omissions matter. However, this critique originally replaced the unsupported inertial explanation with an equally unsupported claim that gravitational balance necessarily dominates and explains observed benefits. No such measured benefits or causal comparison were supplied.

The corrected question is which moment components and response mechanisms matter for a stated motion and support model. Gravitational balance, inertia, elastic stiffness and damping are distinct quantities.

## Location

- [Secondary Axis Stability](../articles/secondary-axis-stability.html): forced-body balance, practical consequences and AffineDrift synthesis.
- This critique's original maximum-gravity estimate, low-speed limit and proposed “zero torque” explanation also required correction.

## Nature of the Issue

About a fixed support point $O$, the gravitational moment is

$$
\tau_{g,O}=r_{G/O}\times m g_B.
$$

Here $g_B$ is gravitational acceleration expressed in the same body frame as $r_{G/O}$. Its magnitude and projection onto a chosen axis depend on geometry and pose. About the center of mass $G$, uniform gravity has no moment; support forces still contribute moments there. A torque balance cannot mix those origins. A moving support introduces additional acceleration terms, while a flexible shaft may require its own states.

About the center of mass or a body point held fixed in an inertial frame, a rigid body with constant body-frame inertia satisfies

$$
I\dot\omega+\omega\times(I\omega)=\tau_{\rm external}.
$$

If gravity is separated from other moments about an appropriate fixed origin, it is one term in $\tau_{\rm external}$. Taking $\omega\to0$ suppresses the gyroscopic term, but does **not** imply $\dot\omega\to0$. Thus low speed alone does not reduce the applied-moment requirement to the negative of gravity. Static balance additionally requires zero acceleration and accounting for every other moment.

## Why This Is a Problem

Use an illustrative scalar model about a fixed horizontal pivot axis with angle measured from downward vertical. For $m=0.35\ \mathrm{kg}$, $\ell=0.02\ \mathrm m$ and $g=9.81\ \mathrm{m/s^2}$,

$$
\tau_g=-mg\ell\sin\theta,
\qquad mg\ell=0.06867\ \mathrm{N\,m}.
$$

A cross-inertia term with $I_{xy}=10^{-4}\ \mathrm{kg\,m^2}$ and angular acceleration $5\ \mathrm{rad/s^2}$ has magnitude $0.0005\ \mathrm{N\,m}$. The former number is a **maximum over angle**. Its ratio to the latter is 137.34 when $|\sin\theta|=1$ and zero when $\sin\theta=0$. A valid comparison also matches the reference point and moment component. These synthetic values do not justify a universal statement about all putting strokes, and the ratio alone does not predict delivered face error.

A zero gravitational moment is not a stability certificate. At both the downward and upward pendulum equilibria the moment is zero; its slope has opposite signs. With positive pivot inertia, the lower equilibrium is restoring and the upper one destabilizing in the unforced ideal model. Without dissipation, restoring motion need not settle. Finite grip stiffness, damping and feedback can alter this result and must be specified rather than inferred.

Likewise, balancing the gravity-moment projection about a shaft axis under a test condition does not show that the entire potential gradient vanishes or that every hand load disappears during an accelerated stroke. A product description such as “zero torque” is not sufficient evidence for those stronger statements.

## Evidence / References

[Peraire and Widnall's rigid-body notes](https://ocw.mit.edu/courses/16-07-dynamics-fall-2009/5e1d8699338146e5127080b880b906d6_MIT16_07F09_Lec28.pdf) derive the external-moment balance about a center of mass or fixed point. The revised article derives its support-origin relation and worked comparison explicitly. Independent repository checks verify the parallel-axis shift, gravity-moment derivatives at both equilibria, and the difference between conservative restoring action and dissipative damping.

No manufacturer claim is used here as evidence of a physical mechanism or a measured player benefit. No empirical ranking of gravitational, inertial and grip effects is established by the assumed numbers.

## Severity

**High for the original causal attribution.** The article needed a complete balance before assigning a dominant mechanism. The critique itself also needed to withdraw its universal gravitational explanation.

## Suggested Remedies

Declare the origin, axes, mass properties, support motion and commanded or measured loads. Compare torque components and propagated delivery effects along the same stroke, with uncertainty. Distinguish static balance, dynamic response and asymptotic attraction. Measure or reconstruct a design's actual center of mass and tensor before connecting its layout to those properties.

The revised article now makes these distinctions and treats putter superiority as unestablished. A future claim that a design improves face delivery, reduces grip effort or changes scoring requires an appropriate comparative dataset and an identifiable mechanism. Merely including gravity in the drift term of an input-affine model supplies neither result.
