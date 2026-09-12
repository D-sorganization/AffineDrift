# Muscle Forces to Joint Torques: Review Audit

## Scope and Current State

Issue #4369, under epic #4009 and corpus #4021. September12,2026.
Both original Chapter16 sources were read completely: print5283 and web4636
approximate original whitespace words. No revised source or rendered chapter has
yet been reviewed. The chapter is not complete. PR4368 covers the preceding
strokes-gained review and is still awaiting its E2E job, run34714267081.

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
