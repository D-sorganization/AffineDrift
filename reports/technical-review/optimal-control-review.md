# Paired Optimal-Control Chapter Review

Issue #4858, epic #4009/corpus #4021. Both complete canonical sources were read: Volume I `ch05_optimal_control.tex` and its Quarto counterpart. The complete current paired source and scoped presentation are locally accepted after clean broad regression; exact-source binding and protected delivery remain pending. The historical route record and prior corrections are preserved, not relabeled as newly discovered errors.

## Argument and Bounded Changes

The chapter separates optimality for a stated model/objective, numerical convergence, feedback stability and physiological inference. That separation is essential for interpreting a golf-swing optimizer: geometry changes the dynamics and their derivatives, accumulated motion determines the current state, impedance changes perturbation response, and impact weights change the optimization objective. An optimum alone identifies neither individual muscle actions nor the nervous system's objective. The existing closing argument expresses this correctly and remains intact.

The earlier #4149/#4153 corrections are mathematically sound. The review checked the costate sign convention, linear terms and Hessian dimensions, DDP dynamics-curvature contractions, iLQR's omission of those contractions, cross-cost Riccati recursion, general policy substitution with regularized gains, local convergence qualifications, finite-horizon uncontrollability example, pendulum CARE and nominal MPC terminal-decrease argument. No new numerical solver, swing-up performance table or empirical golf result is introduced.

Three bounded additions make the numerical conventions explicit:

- The local Taylor model assumes twice continuously differentiable transitions and costs near a feasible nominal trajectory, in independent perturbation coordinates. A fixed-mode flow derivative does not by itself describe a transition through impact. The reset and event-time sensitivities require an applicable hybrid treatment; this chapter does not derive them.
- The trial fraction `0 < alpha <= 1` scales the feedforward correction. Feedback uses the trial trajectory's deviation, and acceptance checks the original objective. This defines the displayed algorithm without inventing an Armijo or Goldstein implementation.
- Identity regularization presupposes declared control scales. With a fixed positive-definite metric `W`, the added quadratic penalty is `mu/2 delta_u^T W delta_u`. For constant nonsingular `delta_u = T_u delta_v`, the same penalty uses `T_u^T W T_u`. Reusing a numerical identity matrix generally changes the physical step. This is numerical regularization, not a measurement of joint damping or metabolic cost.

Long web equations are reflowed without changing their algebra. The alternative Riccati form defines the local abbreviation `A_cl,k = A_k + B_k K_k`; the print edition retains the equivalent expanded product. All original source targets are preserved.

## Independent Technical Checks

The preparation record uses a manufactured two-state nonlinear transition with a nonzero nominal successor. Exact symbolic differentiation of the composed local objective agrees with the displayed action-value gradient/Hessian, including nonzero dynamics-curvature terms omitted by iLQR. A separately chosen regularization produces actual regularized gains; direct polynomial substitution verifies the general value-gradient/Hessian update. The scalar cross-cost example independently gives feedback `-3/4` and curvature `7/8`.

For the printed pendulum example, the analytic CARE solution agrees with SciPy to approximately `1.42e-14`. Gains are approximately `43.1662479` and `13.5507324`; the closed-loop roots are approximately `-3.1621196` and `-10.4886129`. This verifies local linearized balance, not swing-up or robustness to arbitrary bounds.

Nine manufactured metric/scaling combinations preserve the physical quadratic objective and minimizing step under coordinate transformation. A separate counterexample with scaling `diag(1000,1)` shows that reusing identity regularization changes the physical step. The original chapter failed six new disclosure contracts while ten numerical cases passed. The combined new and retained suite then passed 58 cases. These are mathematical/software checks, not observations of a golfer.

## Sources and Reading Limits

The review consulted MIT's [trajectory-optimization notes](https://underactuated.mit.edu/trajopt.html) and [LQR notes](https://underactuated.mit.edu/lqr.html) for local optimization and Riccati context. It independently retained the chapter's semidefinite/positive-definite distinctions rather than copying broad shorthand. Kong et al.'s [saltation-matrix tutorial, Section III-A and the Section III-B derivation through the first-order reset/time variation](https://arxiv.org/html/2306.06862v3) supports the bounded impact-sensitivity qualification. Its existing bibliography entry is reused. No grazing-impact or simultaneous-contact differentiability guarantee is asserted.

The MPC publisher landing page was inspected, but linked book PDF retrieval failed; this is not a new primary-theorem reading. The existing nominal terminal-decrease statement was assessed mathematically and retained, with its feasibility, admissibility, positive-cost and regularity assumptions. It is not upgraded to a robust or arbitrary-local-solver guarantee.

## Presentation and Preservation

The original six chapter pages were inspected. After the paired additions, the enclosing volume compiled to 149 pages and the seven revised chapter pages (PDF 79–85; printed 65–71) were inspected without clipping. The rest of the volume was compiled, not reviewed. Final compilation reported no unresolved references or overfull boxes. Temporary BibTeX path fixes affected only generated auxiliary files. The inspected enclosing-volume PDF replaces the tracked download; this carries the current sources without expanding the chapter review scope.

A standalone Quarto preview initially exposed mobile clipping but did not use the production theme. A root-project scoped render then established the actual layout. Deployment-equivalent asset bundling/synchronization, removal of the legacy math polyfill and a generator-produced scoped route manifest were applied only to the isolated preview. The first revised root render passed four browser/axe cells, yet manual inspection identified a clipped equation number and long MPC inequality. Further equivalent reflow now passes four browser/axe cells, with the revised DRE number and MPC inequality manually verified. Sixteen web captures across both revisions were inspected; automated body-overflow checks alone are not presentation acceptance. Existing small mobile display-math type and floating-control overlap are separate layout limitations.

The prior-review record preserves 52 protected source/evidence files and the identities/dispositions of the other 250 routes. The two original corpus rows can advance only with the separately bound accepted source; whole-book consistency remains separate. No prior empirical critique, whole-book review or whole-corpus completion is implied.

## Flash Delegation and Lead Adjudication

Eight successful text-only agy CLI `gemini-3.8-flash-low` helpers supplied TeX/Quarto inventories, an independent-QA draft, an issue draft, a copy review a validation checklist, a PR draft and a result-summary script. Lead review rejected an unstable system being called stable, overgeneralized iLQR convergence and clamping claims, a wrongly centered value approximation, arbitrary gains called regularized, and a claim that Hessians transform tensorially under arbitrary nonlinear coordinates. The accepted scaling statement is explicitly constant and linear.

The checklist's suggestions for new Armijo/Goldstein tests, reset finite differences, solver benchmarks and gradient-descent rate claims exceed this bounded chapter change and were not accepted. Its instruction to “preserve” unspecified saltation matrices is not evidence that this chapter implements hybrid derivatives. Helpers had no edit, merge or scientific acceptance authority.

The first broad run passed 6,841 cases and failed four book-audit checks because the rebuilt PDF retained old dependency hashes in that separate audit. The repair changes those hashes only; see `optimal-control-dependency-carry-forward.json`. Content lint passed 199 cases with four skips. The initial coverage result (79.83%) includes scripts and source code; it is not directly comparable to earlier source-only coverage. The clean retry at `d9e7884697da3308102f4280aef591588eb0c722` passed 6,800 tests, with 29 skips and 201 deselections, in 584.67 seconds (93.24% source coverage). All 74 focused checks and 16 publication gates pass. No test bounds were relaxed. Lead corrected the PR draft: printed Chapter 6, analytic/SciPy matrix difference rather than CARE residual, and 58 combined cases rather than 58 scaling cases.

The Flash summary draft was reviewed before use: decimal coverage parsing, required nonempty leaf test suites/attributes, and staged-change detection were corrected. JUnit elapsed time (584.538 s) and pytest summary time (584.67 s) are recorded separately. All 52 protected files and 250 other route identities remain exact; the separate book-audit repair preserves every non-digest field.
