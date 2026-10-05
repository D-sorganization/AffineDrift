# Golf Capstone Review: Decisions and Evidence

Issue #4921, epic #4009, corpus #4021. Complete chapter ch10_golf_swing_project.tex, generated listing and canonical swing_analysis.py reviewed. Bounded Volume V preface wording corrected; other volume chapters remain outside this acceptance. Parent N source passed its frozen regression and is now regular PR #4922, delivery head 4bac438c1. Corpus remains 407 rows, 64 pending-prefix rows until this batch is accepted.

## Conceptual Corrections

The prior code returned same-state joint-acceleration norms while calling them clubhead acceleration. The chapter also described the same-state response M^-1 tau as a difference between whole trajectories. New signed vectors make the algebra inspectable; the existing norm method remains documented as such. Norm medians have rad/s^2 units and do not claim complementary percentages. With tau=bias, nonzero vectors cancel: the norms cannot partition net acceleration or muscular effort.

The chapter derives Cartesian acceleration J qdd + Jdot qdot and the signed speed derivative only where speed is positive. Relative angles start from horizontal at the base. For aligned vertical rods, gravity and Christoffel generalized forces vanish, while Cartesian centripetal acceleration can remain. Straight horizontal alignment does not eliminate gravity. Finite-time trajectory separation includes f(x_driven)-f(x_zero), not merely the input response. A release experiment must specify the full state, retained passive terms, intervention and endpoint. The energy identity E_dot=qdot^T tau answers a different question from acceleration attribution or peak ordering.

Synthetic samples now include both endpoints, with ceil(T/dt) intervals. Analytic first and second derivatives avoid the old mismatch between linspace spacing and the gradient timestep. Torques are the model inverse-dynamics requirement Mqdd+Cv+g for that prescribed motion. No actuator limits, forward integration, optimization or empirical motion are claimed. The equations hold at samples up to model/numerical error; the same model used on both sides is not an independent model validation.

The full-pipeline claim is replaced with a bounded executable core and explicit extensions. Experimental inverse dynamics needs external wrench assumptions and residuals; EMG is not a direct muscle-force measurement. Muscle recruitment, feedback, funnels/contact events and ensemble task-null-space analysis have distinct evidence requirements. Holding prescribed kinematics fixed while changing mass cannot change tip speed; changing the plant in a forward-control experiment asks a different question.

## Flash Delegation and Adjudication

Five successful agy Gemini 3.8 Flash responses: original chapter/module reviews, test proposal and final chapter/module reviews. All were embedded-source, reasoning-only tasks. Lead implemented sources and repaired the test proposal. Raw responses and exit files are retained as evidence, not authoritative findings.

Accepted: same-state/trajectory and joint/Cartesian distinctions, inconsistent synthetic torques, timestep mismatch, boundary validation, cancellation counterexample, missing TeX backslash (also found by compilation), and clearer scalar-sum wording.

Rejected or repaired: original chapter reviewer called vanishing joint Christoffel terms false, then derived why they vanish; its trajectory-difference equation had the wrong sign on drift separation. Module reviewer invented empirical driver mass/inertia values and a universal factor-two acceleration inference for a coupled chain. All joint coordinates here are angular, so unequal link lengths do not make their joint norm dimensionally heterogeneous (coordinate dependence remains). Final module reviewer alleged wrong analytic derivatives, then derived the implemented expressions correctly; np.vectorize tuple outputs work on tested multi- and single-sample cases. A one-sample state evaluation is intentional and has zero elapsed duration. Relative-coordinate agreement is verified against GolfModel; no guessed mismatch or unsupported Python-version defect accepted.

The helper test proposal invented synthetic_swing keyword arguments and a dictionary summary, omitted the matrix-vector product in Cv, and silently repaired the malformed shape it claimed to test. Lead repaired these and used analytic second derivatives to avoid a tautological inverse-dynamics test. RED: 26 failing and 14 passing focused cases; GREEN: all 40 pass. No failing test was weakened to accommodate the old defect.

## Primary Reading Scope

Northwestern's Modern Robotics official transcripts: Space Jacobian (description and full transcript), Lagrangian Formulation Part 1 (full transcript), and Forward Dynamics of Open Chains (full transcript), read 2026-10-05. Added three explicit transcript references with structured and printed URLs. These support the distinction between point-coordinate and spatial-twist Jacobians, forward/inverse dynamics, generalized mechanical power, simulation and energy/refinement checks. The capstone's three-link calculations and counterexamples were independently derived; no full book or human experiment was reviewed for this batch. An initially guessed dynamics URL failed; the correct chapter-prefixed URL was followed from the official navigation.

- https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/
- https://modernrobotics.northwestern.edu/nu-gm-book-resource/chapter-8-1-lagrangian-formulation-of-dynamics-part-1-of-2/
- https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-5-forward-dynamics-of-open-chains/

## Mathematical and Visual Checks

Six independent manufactured checks, 100 cases each, seed 4921, maximum absolute error 5.637e-8 below 1e-5: position derivative versus model tip speed; Cartesian acceleration versus velocity derivative; signed same-state addition; mechanical energy derivative versus generalized power; analytic time scaling; and x_dot=x^2+u with driven tan(t) versus unforced zero. Script and JSON retained. These are model/math checks, not biological or complete forward-trajectory validation.

PDF: 49 pages, 19 bibliography entries. Physical pages 3–5 and 39–49 visually inspected at final pass 7, including the entire capstone, listing, contents and bibliography. Title shortening removed an awkward hyphen and one page. No unresolved citations/references. All 78 combined listing/reference/audit tests pass after refreshing the changed bibliography digest in the book ledger. The initial four stale-evidence failures are retained. Five pre-existing overfull boxes in other chapters (platform, comparison, simulation, parameter-estimation title) remain outside scope; no capstone or bibliography overflow. Historical duplicate PDF destinations/package warnings remain. Initial build failed because a TeX end-equation backslash was missing; repaired, subsequent builds pass.

## Delivery and Coordination

Own issue lease through 03:42 UTC, receipt 5986684189; expanded presence through 03:54 UTC, receipt 5986779427. Central inbox still returns historical identity and page-limit errors, so total absence of messages is not proven. C/J/M leases renewed by exact REST protocol after central GraphQL failures: receipts 5986837245, 5986837517 and 5986837734, through 04:01 UTC. No conflicting fresh claim labels found.

Regular parent PR #4922 was created and pushed successfully. App attachment failed at the thread's 100-attachment cap; retain the PR URL. #4889 remains on main, with build/browser/visual checks passing and accessibility still in progress. Later accepted batches remain stacked; retarget only after actual parent remote-main delivery, arm via central guard and verify Git-blob hashes. Use topic branches and protected PR delivery.
