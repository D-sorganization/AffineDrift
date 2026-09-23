# Contraction Lay Article: Technical Review — #4441

## Scope and Investigation

Read the complete Contraction_Tangent_LAYMAN.qmd, including equations,
benchmark table, software claims, questions, accessible summary and critics'
responses. Read the corrected technical companion and existing numerical
helper and tests. The lay source is the longest remaining entry marked Full
Technical Audit Pending in the 405-source index. This review supersedes its
limited September 13 route review, not the review state of other series pages.
Parent: #4021; epic: #4009; historical route batch: #4056.

The revised argument follows a physical model through feasible feedback,
perturbation response and the delivered impact outcome. It distinguishes
mathematical error length, mechanical impedance, cost, finite-time task
sensitivity and empirical human performance. The numerical examples are
declared ideal models, not experiments on golfers.

## Corrected Findings

1. **P1 — Incremental Stability:** A damped pendulum retains an unstable upright
   equilibrium. A spring without damping need not reduce errors. Feedback
   examples, energy loss and target attraction do not automatically prove
   contraction. State the common feedback rule, metric bounds, domain,
   containment and reference feasibility.
2. **P1 — Geometry and Riccati Rates:** Differentiate the implemented closed
   loop and the metric along its flow. Include Q, feedback cost and metric
   normalization in the Riccati rate. Distinguish value from Hessian, finite
   horizon from asymptotic behavior, and spectral from monotone metric decay.
   A flat metric can support contraction; it is not physical stiffness,
   inertia, curvature, or a force-producing surface. Tangent dynamics are
   exact for infinitesimal variations, not finite displacements.
3. **P1 — Unsupported Results and Software:** Withdraw cart-pole success
   percentages, basin volumes, speed overhead and solver transcript. No
   corresponding reproducible experiment package was provided. Replace the
   unverified implementation URL with an executable scalar certificate using
   the extant repository helper. A decay rate uses inverse seconds, not an
   oscillation-frequency interpretation; a requested rate must actually pass.
4. **P1 — Optimization and Implementation:** A finite penalty is not a hard
   constraint. Joint nonlinear metric/controller/trajectory optimization is
   not generally convex; distinguish the fixed linear feasibility case.
   Distinguish DDP from iLQR, sampled feedback from continuous feedback, and
   sampled recovery or capture estimates from a verified invariant domain.
5. **P1 — Human and Golf Interpretation:** Separate inertia, stiffness,
   damping, activation history and feedback. A muscle factorization does not
   identify a neural contraction objective. Remove the unsupported patient
   prediction and directional coffee-cup stiffness prescription. Explain
   finite remaining time, output sensitivity, independent noise, persistent
   forcing, phase and event timing, constraints and impact jumps.
6. **P2 — Accessible Presentation:** Replace the legacy custom disclosures
   with native keyboard-operable details elements and apply the same limits
   to the summary and critics. Reuse existing disclosure styling and the
   reading-size equation rule from force-mobility.css; no shared CSS changes.
   Add a Related Articles section with accurate scope annotations.

## Independent Evidence

The corrected red run had nine expected failures: eight surviving false or
unsupported source claims and the absent executable example. Eleven mechanics
checks already passed. An initial test-authoring exact-float comparison was
corrected to a numerical tolerance before recording that red baseline.

The twenty new cases in tests/test_contraction_lay_rigor.py check the published
code and specific regression claims, cost rescaling, upright-pendulum
instability, undamped energy conservation, fixed-damping stiffness changes,
nonnormal transient growth, continuing forcing, sampled-control instability,
phase/event distinction and task sensitivity. They do not substitute for the
whole-article mathematical reread. Together with existing reference, chapter
and link checks, 56 focused cases pass.

- Scalar LQR: S = 3, feedback gain 3, closed-loop rate 2 inverse seconds.
  Rescaling the whole objective by seven preserves gain and rate; the old
  unnormalized formula would change from 4.5 to 31.5.
- The normalized upright pendulum Jacobian has a positive eigenvalue despite
  damping. The undamped oscillator preserves the quadratic energy metric.
- With unit inertia and damping 0.2, stiffness 1 or 4 gives spectral real
  parts -0.1. More stiffness does not increase this envelope decay rate.
- The matrix with diagonal -1 and upper-right entry 4 is Hurwitz but has a
  negative Euclidean contraction candidate rate and observable transient
  norm growth.
- Held feedback on an integrator has multiplier 1 - 2h. A continuous-time
  rate of 2 does not prevent the h = 1.25 discrete implementation expanding.
- Equal event position can coexist with different arrival times; a smaller
  full-state norm can coexist with a larger measured output error.

Existing tests independently cover the finite-horizon degeneracy,
double-integrator generalized eigenvalue, metric-derivative, covariance and
hybrid distinctions reused from the technical reference. No production
numerical module was changed or duplicated.

## Primary Sources and Access Limits

Read the [Lohmiller–Slotine preprint](https://web.mit.edu/nsl/www/preprints/contraction.pdf)
for differential distances, changing metrics and regional containment; the
[MIT LQR chapter](https://underactuated.mit.edu/lqr.html) for value and feedback
conventions; and [MIT trajectory optimization](https://underactuated.mit.edu/trajopt.html)
for DDP/iLQR scope. The article's counterexamples are independently computed
illustrations, not reported experimental results from these references.

The [Kong et al. saltation review](https://arxiv.org/abs/2306.06862) supports
the reset-plus-event-time sensitivity distinction. No claim of a newly
validated golf contact model is made.

The [Burdet et al. publisher record](https://www.nature.com/articles/35106566)
provides the abstract and accessible supporting material about arm impedance
adaptation using a robotic interface. The main participant-data article is
subscription restricted. No full-text experimental reanalysis, effect-size
estimate, clinical inference or transfer to golf is claimed.

## Publication Evidence

Exact source and rendered checks are recorded separately in
contraction-lay-render-verification.json. The initial mobile render reduced
display equations to about 13px, motivating reuse of the existing
reading-size rule. The source must be committed before the audit inventory
is rebound to its immutable revision; the temporary route deferment keeps
the old limited review from being silently attached to new bytes.

The full-corpus inventory remains incomplete. Neither this corrected page
nor site-wide browser coverage establishes acceptance of unreviewed sources.
