# Screw Reference Review Preparation

Queued issue [#4832](https://github.com/D-sorganization/AffineDrift/issues/4832). No implementation lease or source edits.

Part of epic #4009 / corpus #4021. Complete source: `articles/screw-theory-reference.qmd` (2,002 indexed words), read at `802e9adc55698d6db4fd926456a1514e2966991d`. This is a queued technical review, not an implementation claim or accepted audit. Existing issue #4719 covers a different historical research outline.

The article's geometric language must distinguish representation, applied wrench, generalized effort, acceleration and counterfactual evaluation. Otherwise the golf-swing interpretation can falsely turn a coordinate transform or pseudoinverse into an identified player input.

Concrete findings:

1. The general twist formula omits nonzero pitch, calls the spatial linear component body-origin velocity without the reference-point correction, and conflates finite displacement with an entire time-varying motion. Treat pure translation, rest and nonunique axes explicitly.
2. Joint screw columns need configuration dependence or an explicit current-axis convention. Separate fixed home screws from the space Jacobian; keep transform directions and angular-first ordering unambiguous.
3. `tau = J_s^T F` is a load/generalized-effort dual map, not proof that arbitrary internal joint torques are an endpoint wrench. Exact inversion requires range compatibility. The pseudoinverse can leave a nonzero torque residual; its Euclidean minimum depends on units/metric and does not identify physical load sharing.
4. `B` maps inputs to n-dimensional joint effort in one equation but transforms as a six-dimensional twist in the next. Separate generalized actuation from a wrench-distribution matrix, which must transform dually with the wrench.
5. The purported drift wrench contains acceleration and adds applied loads to inertial demand without a consistent balance. Retain the correct declared coadjoint sign, derive single-body forward acceleration, and distinguish that model from assembled multibody dynamics and constraints.
6. Modal shaft coefficients need an explicit generalized-force or dual wrench map, restoring/damping signs and fixed-state assumptions. A kinematic screw is not automatically a load distribution. Fixed-state affine dependence does not imply absence of indirect input effects through evolving shaft states, nor does wrench addition imply trajectory superposition.
7. Align ZTCF and instantaneous ZVCF with `NOTATION.md`: zero the declared channel/states, distinguish acceleration from a generalized-force representation, retain specified internal state/contact mode and avoid biological-passivity claims. Correct the lay explanation as well as the equations.

Initial primary preparation: selected Modern Robotics author transcripts on [twists](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-2-twists-part-1-of-2/), [wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/), [space Jacobian](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/), [statics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/) and [rigid-body dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-2-dynamics-of-a-single-rigid-body-part-2-of-2/) read. No full book or video/figure review, and no human-golf validation. One supplied-text agy CLI Gemini 3.8 Flash inventory is non-authoritative; reject its equation of fewer-than-six task DOFs with underactuation and its claim that the Moore–Penrose minimum-norm solution itself is nonunique.

Acceptance: review the complete source and matched summaries; reuse existing screw/duality tests, add independent manufactured edge cases for actual gaps; preserve unrelated findings and the old route snapshot; render and inspect equations, responsive behavior and links; run repository-standard validation; bind only accepted evidence; update exactly one corpus row and open a regular PR. No whole-book or empirical-validation credit. Current radar/ideomotor delivery takes priority; check the claim before implementation.
