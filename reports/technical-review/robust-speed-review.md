# Robust-Speed Technical Review

Issue #4759 is a child of epic #4009 and continues corpus review #4021.
The complete Chapter 23 source, its figure generator, the pinned provider
chapter, and the uncertainty/control primitives and study runner were read.
The archived numerical outputs were independently summarized; the dynamical
simulation was not rerun. Prior companion findings are preserved separately.

## Scientific Decisions

1. **Figure Provenance.** The earlier figure used four programs from a different
   transmission-robustness experiment, while this chapter discussed eight coupled
   uncertainty programs. Its caption also described absent encodings and a
   frontier. The replacement plots all eight declared candidates from their
   archived arrays. Colors identify programs; two panels project four of the five
   objectives. No connecting line implies feasible interpolation or a full front.
2. **Finite Candidate Scope.** All eight held-out candidates are nondominated in
   the five reported sample summaries. This is not proof that no other admissible
   policy can dominate them, nor stochastic or case-by-case dominance. Distinguish
   policy sets, objective fronts, normalization choices, and sampled projections.
   A three-point counterexample demonstrates the untested-policy limitation.
3. **Risk Definitions.** Speed rewards have adverse lower tails; error losses
   have adverse upper tails. Removed an ungrounded numerical illustration using
   lower-tail error. Define a population quantile, integrable-loss CVaR with
   probability atoms, joint chance constraints, and set-based worst-case loss.
   These are separate criteria, not equivalent robustness labels. Counterexamples
   show CVaR differs from a strict-threshold conditional mean and marginal success
   differs from joint success.
4. **Sampling and Pairing.** The archive uses 24 global screening cases and six
   cases per training/held-out split, across 12 engineering inputs. Its permuted,
   middle-stratum jitter design is not IID golfer data or exact uniform sampling
   across each full range. Linear q10 with six cases averages the first two order
   statistics. The difference of policy q10 values differs from q10 of paired
   differences; both were independently reproduced.
5. **Actuator and Outcome Contract.** The command passes through delay and a
   rate-limited lag-state increment before velocity resistance and capacity
   clipping. The latter can change delivered-torque slopes beyond that rate
   limit. The impedance term here is velocity proportional, not measured muscle
   stiffness. Preselected schedules still produce velocity-dependent delivered
   torque. Explain signed wrist targets, passive-wrist naming, fixed 0.24 s
   endpoint, wrapped planar error, peak-force aggregation, squared-torque units,
   and speed spread. None supplies ball dispersion, metabolic cost, or human load
   tolerance. Small closure residuals alone do not establish integration accuracy.
6. **Selection and Stability.** The code selects policies from training objectives.
   Independently reproduce all seven summary fields per candidate and split,
   both objective matrices and Pareto masks, the three training selections, and
   six held-out leave-one-case-out membership counts. Chebyshev scales depend on
   the training candidate ranges. No claim of a three-way validation protocol,
   optimization convergence, or population-frontier confidence interval is made.
7. **Failure and Predictive Qualification.** Keep attempted/solved/admissible/event
   denominators distinct. Unknown numerical outcomes are not fabricated physical
   failures. Conditioning on successful solves and selective exclusion can bias
   tails. Choose holdouts for the deployment question and distinguish average
   calibration from subgroup performance. Unidentifiable parameters need not
   prevent an identifiable prediction; bounded inputs cannot detect every unknown
   model inadequacy.
8. **Mechanism and Transfer.** Early restrain and late drive differ in early torque,
   onset, and late torque, so their contrast does not isolate an opposing interval.
   Match policy information, constraints and initial-state conventions; preserve
   induced state changes. Equal tuning budgets are not proof of equal optimization
   quality. Cross-tier ranking reversals and bimodality do not identify their causes
   by themselves. Reviews provide context, not human validation of this ranking.

## Primary Evidence and Access Limits

The provider is pinned to UpstreamDrift revision
85cce4d3307bb7ad3953d9fc6e583e370803515c. Exact source blobs and their hashes are
preserved in QA. The NPZ is published byte-for-byte; the local JSON record may
receive whitespace formatting but must remain semantically equal to the provider
record. Stored code hashes match both inspected uncertainty/control modules.
The lower-level dynamics hash is outside this new code-read scope. Numerical
recomputation verifies archived summaries, not the original trajectory solution.

For the risk definition, the author's
[general-distribution CVaR paper](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf)
was inspected, especially probability atoms and the minimization formula
(Theorem 10). The linked manuscript is dated November 2001; the cited journal
publication is 2002, volume 26, pages 1443–1471. The loss convention is upper-tail
and requires an integrable loss. The chapter's four-point example is independently
calculated, not a golf result from that paper.

Glazier's author publication list and bibliographic record confirm the 2011
movement-variability article. The publisher and author-linked Drive full text
were unavailable through browsing; no detailed empirical result from it is claimed.
McPhee's identity and abstract scope were previously verified in the Chapter 3
review. Both citations supply methodological context only.

## Delegation and Adjudication

Supplied-text agy Gemini 3.8 Flash jobs support source inventory, provider text
extraction, code-contract extraction, numerical test drafting, final notation
review, and a handoff checklist. The lead rejected or narrowed the following suggestions:

- Calling all-eight nondominance an established high-dimension or small-sample
  artifact; sensitivity does not identify its cause.
- Treating hand-force/joint-torque tradeoffs as an unconditional algebraic identity.
- Adding unsourced feedback-latency numbers or declaring the downswing open-loop.
- Calling McPhee's single-author review an “et al.” paper.
- Calling the policy selections held-out selections; code uses training objectives.
- Inventing effective parameter rank three/nullity nine; the archive reports six
  at the declared threshold. This chapter does not repeat that unrelated screen.
- Calling the stratified jitter design IID full-range uniform sampling.
- Calling velocity-dependent delivered torque purely open-loop control.
- Using a dense numerical grid as the strongest available CVaR check; for the
  discrete example the convex piecewise-linear objective is checked at exact
  breakpoints, with the outer intervals handled analytically.

Final notation review improved explicit attribution of each program's error,
introduced the balanced rule under one consistent name, and made the quantile
definition apply to a scalar outcome before distinguishing reward and loss tails.
These are clarity improvements; no population guarantee is inferred from a
six-case empirical percentile.

The initial figure regression failed because it contained four points instead of
the declared eight. All seven numerical/figure checks pass after the correction.
The final221-page companion PDF is byte-identical at canonical and public paths.
The lead inspected all Chapter23 PDF pages155-161 and boundaries154/162, the
standalone figure, and all three mobile display equations. Four viewport/theme
checks pass, with zero serious/critical axe findings;29 math expressions render
without errors or page overflow. Twelve publication gates and653 source titles
pass, as do Ruff, Black837, CI-scoped mypy94 and64 affected checks.

The full configured default coverage run exits zero, with6408 passing
progress symbols and29 reported skips. Coverage is78.9% for
source plus scripts and93.0% for source alone. These tests verify the
declared mathematical and publishing contracts, not human biomechanics.

The Flash handoff draft mistook124 pending audits before this chapter's binding
and123 afterward for a contradiction. Completion credit explains that decrement.
Its 'axe0 errors' summary was narrowed to zero serious/critical findings.
Source binding and protected PR delivery remain separate checkpoint steps.
