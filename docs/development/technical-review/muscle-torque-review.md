# Muscle Forces to Joint Torques: Review Audit

## Scope and Current State

Issue #4369, under epic #4009 and corpus #4021. September12,2026.
Both original Chapter16 sources were read completely: print5283 and web4636
approximate original whitespace words. No revised source or rendered chapter has
yet been reviewed. The chapter is not complete. PR4368 covers the preceding
strokes-gained review and has a Python artifact-reproduction failure in run34714267081; E2E job103608499603 has now passed. The Linux discrepancy is at the last floating-point digits, not an altered scientific result.

## Original Source Findings

- The print and web matrices use rows for muscles yet interpret columns as muscles;
  their displayed transpose product gives (25,22), not the stated (31,12).
- With positive tensile force and length increasing on lengthening, skeletal work
  is minus tension times length change. Define L=dell/dq and A=-L^T explicitly;
  do not copy a transpose-only force relation from a spatial-force Jacobian.
- Axis torque needs the projection of r cross F onto a declared unit axis.
  A scalar distance and a position vector cannot share an unexplained symbol.
- The two biceps examples disagree: print asserts maximum moment arm near full
  extension; web asserts roughly90degrees. Neither generic anatomy numbers nor
  lower-limb Delp1990 establish personalized elbow moment arms.
- Nullspace algebra alone does not ensure nonnegative, capacity-bounded forces.
  A null direction may redistribute synergist force rather than co-contract.
  Co-contraction does not by itself prove asymptotic stability or useful impact
  performance. Tangent stiffness must specify held states, geometry and feedback.
- Net inverse dynamics is an estimate conditional on inertial/contact models;
  EMG is activation-related electrical evidence, not direct tensile force.
  Dynamometry does not isolate every individual muscle and need not be invasive.
- State-dependent torque feasibility, floating-base/contact equations and actuator
  states matter. A torque-controlled model does not prove unique human recruitment
  or establish what objective the nervous system optimizes.
- Biarticular force produces coupled torques; signed powers determine whether it
  generates, absorbs or transfers work. Tendon storage is a separate energy term.
- Unsupported grip percentages, muscle-specific strong/weak-grip leverage,
  forearm/wrist axis equivalence and stiff-at-impact prescriptions need evidence
  or withdrawal. Triceps heads and wrist/finger flexors need anatomical precision.
- Fix web heading/list artifacts and all eleven exercise premises and answers.

## Primary Source Reading, Precisely Bounded

Sherman, Seth and Delp2013 author PDF, DOI10.1115/DETC2013-13633:
https://nmbl.stanford.edu/wp-content/uploads/ShermanSethDelp-2013-WhatIsMuscleMomentArm-Final2-DETC2013-13633.pdf
Downloaded763426bytes through a plain public HTTP request after web tool403.
Full extracted text of nine pages, including references, read. Pages4and5 were
also rendered and inspected; page6render exists but was not yet visually read.
Relevant scope: workless-path assumptions, coupled coordinates, generalized speeds
and force transmission. It concerns modeling definitions, not validated golf advice.
Its displayed equations2/3 have a positive excursion derivative; do not claim this
paper alone verifies our negative lengthening convention. Reconcile using explicit
skeletal work and independent current implementation documentation.

OpenSim FunctionBasedPath API4.5 documentation, Detailed Description and force
method parameters, read: negative length derivative, lengthening-speed convention,
workless-path assumptions, generalized-speed distinction and positive tension.
https://opensim-org.github.io/opensim-moco-site/docs/1.3.0/html_user/classOpenSim_1_1FunctionBasedPath.html

Rice NMSM Surrogate Model Creation complete technical page read. It explicitly
uses a negative length derivative and illustrates consistent polynomial length,
velocity and moment-arm functions. No empirical golfer inference is supported.
https://nmsm.rice.edu/guides-and-publications/tool-overviews/treatment-optimization/surrogate-model/

PMC full-text URLs returned bot checks; web-tool author PDF failed403 and another
university copy cache-missed. Plain public author-PDF download succeeded without
credentials. Van den Bogert2011 abstract/search result located, not full text read.

## Next Actions

Complete primary anatomical, force-estimation and stiffness/energy source review.
Design independent virtual-work, transpose, feasible-force, power and stiffness
examples and tests before implementation. Preserve all original destinations and
paired chapter structure, with shared numerical code/figures where useful. Review
all final PDF pages and full web reading, not only formula presence or title counts.
Do not commit downloaded papers/screenshots as redistributable deliverables.

## Elbow Geometry Source: Complete Reading

Murray, Delp and Buchanan1995, Journal of Biomechanics28(5),513-525,
DOI10.1016/0021-9290(94)00114-j. Author copy:
https://nmbl.stanford.edu/publications/pdf/Murray1995.pdf
Retrieved879802bytes. Thirteen scanned PDF pages have no extractable text; all
were rendered and visually read, including the blank fourth page, figures, tables,
methods, discussion and references. This is a two-cadaver study (ages90and82)
and a geometric model, not measurements of golfers. It supports configuration
and forearm-position dependence, not a universal maximum at full extension.

The paper's methods and Figure4 caption explicitly negate the tendon-excursion
slope for their positive-flexion convention. Its displayed equation1 omits that
minus; the chapter must declare its own sign and check skeletal virtual work.
The discussion identifies path approximation, measurement and sample limitations.
Do not turn model/specimen discrepancies or population-size unknowns into coaching
rules. The author publication list located this exact PDF; a general lower-limb
model citation was inadequate evidence for the chapter's elbow-specific numbers.


## Independent Mechanics Checkpoint

Eight tests in `tests/test_muscle_torque_rigor.py` pass locally (September 12).
They verify constructed mechanics examples, not the still-unrevised chapter or
empirical golfer parameters. Black100 formats the file; no production utility is added.

1. A rotating insertion and fixed anchor give the same torque from the physical
   cross product and minus tension times a central finite difference of length.
2. With muscle-by-coordinate L=[[-.05,0],[-.02,-.04]], tensions (500,300) N
   produce (31,12) Nm through -L transpose. At speeds (2,-3) rad/s, path rates
   are (-.10,.08) m/s and skeletal power is 26 W, equal to -F dot length rate.
3. The second muscle alone produces joint powers (12,-12) W at speeds (2,-1),
   but absorbs 24 W at (2,-3). Biarticular anatomy does not determine power flow.
4. For A=[[.04,.02,-.03],[0,.03,.02]], F0=(100,200,50) N, capacity
   (400,300,250) N, and null vector (13,-8,12), F0+t*n preserves torque
   (6.5,7) Nm. Nonnegative capacity bounds restrict t to [-25/6,50/3].
5. Independent linear programs give coordinate maxima (22,14) Nm, yet that
   simultaneous torque pair is infeasible. A rectangle of separate limits is
   insufficient for coupled muscle feasibility.
6. The constraint q=(s,2s) changes effective arms to (.05,.10) m and reduced
   torque to 55 Nm; virtual work agrees with the unreduced torque projection.
7. A fitted arm field (.02+.01*q2,.01) has a nonzero closed-loop work integral
   (-1 J at fixed 100 N tension around the unit square). It cannot be minus the
   gradient of one smooth, single-valued path length on that region.
8. A taut positive-stiffness spring between an anchor and rotating insertion
   has negative angular energy curvature at its maximum-length alignment:
   Kq=k*(length derivative)^2+F*(length curvature)=-20/3 Nm/rad.
   Finite differences of energy confirm the geometric term. Positive material
   stiffness alone does not establish a stable joint equilibrium.

These independent examples will guide the correction and worked exercises.
For configuration-only workless paths, derive skeletal power explicitly; for
moving guides or explicit time dependence, include the additional guide work.
Do not promote a fixed-state elastic example into a universal physiological law.

## Upper-Extremity Model Source: Bounded Reading

Holzbaur, Murray and Delp (2005), DOI10.1007/s10439-005-3320-7, author PDF:
https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf
The prior reading covered extracted pages1-3,5-9 (one figure caption truncated),
and pages10-11 through the discussion/conclusion. Table page4 was subsequently rendered and fully inspected; its footnotes distinguish measured architecture from compartment PCSA distribution fitted to maximum isometric moments. Full visual figure/reference review remains outstanding. The model has15 degrees of freedom
and50 muscle compartments; it omits intrinsic hand muscles. Muscle parameters
were partly adjusted against joint-moment measurements, while selected coupling
comparisons offered separate checks. Prescribed scapular motion, generic geometry
and tendon-slack-length sensitivity limit inference. This is useful evidence for
stating what was calibrated and tested; it does not validate golf grip prescriptions.

Checkpoint root validation: 5305 passed,29 skipped,132 deselected,59 warnings; exit0. Log: `muscle-checkpoint-root.log`. Six unrelated generated outputs were checked and restored: date-only JSON or formatting/line endings.
