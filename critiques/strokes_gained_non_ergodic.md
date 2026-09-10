---
title: "Critique: Strokes Gained Limitations and Ecological Fallacy"
description: "Corrected critique distinguishing strokes-gained accounting from individual forecasting, hidden-state models, and tournament objectives."
---

## Critique: Strokes Gained Limitations and Ecological Fallacy

## Summary of Concern

**Technical correction, September 10, 2026:** The original critique correctly
raised questions about forecasting a changing golfer and choosing tournament
strategies. It incorrectly presented stationarity, full observation, and risk
neutrality as requirements of strokes-gained accounting. Those claims are
withdrawn. This correction preserves the critique's identity and its governed
open status; it does not silently adjudicate the trust ledger.

The revised [article](../articles/strokes-gained-limitations.html) separates
three questions: how recorded strokes are allocated, what a golfer is likely
to do next, and what would change under an intervention. The remaining concern
is whether a particular predictive or decision model has adequate states,
validated transitions, an appropriate objective, and uncertainty estimates.

## Location

- **Article:** `articles/strokes-gained-limitations.qmd`.
- **Relevant Sections:** Policy Evaluation; Individual Continuation and
  Category Boundaries; Heterogeneity, Selection, and Causal Inference; Hidden
  States and Tournament Objectives.

## Nature of the Issue

For a fixed benchmark $B$ and complete hole with counted costs $c_t$,

$$
\sum_t[B(s_t)-c_t-B(s_{t+1})]=B(s_0)-\sum_t c_t,
$$

because the final holed-state value is zero. This holds without assuming an
optimal policy, stationary skill, or a Markov process. Omitted factors can
limit how well the benchmark predicts or interprets individual shots without
invalidating that cancellation.

A policy value $V_i^\pi$ requires a specified continuation policy and transition
model. Its state may need environmental conditions, player identity, history,
or beliefs about hidden variables. A distance-and-lie conditional mean can
still be defined when those observations are insufficient for a closed Markov
recursion. Adding a symbol for confidence does not establish its causal effect.

## Why This Is a Problem

The same physical leave can have different continuation values for different
players. Yet “worse putter” does not establish a larger proximity benefit:
probability levels do not order distance derivatives. A pooled regression also
mixes state-dependent player weights and observed conditions. Calling that
regression an individual treatment-response function needs justification beyond
its fit to the observed data.

Time variation can undermine a static forecast, but an individual's mean need
not equal a heterogeneous population mean even under stationarity. Dependence
alone does not establish non-ergodicity. The earlier argument conflated these
distinct issues and provided no golf-specific stochastic model establishing
its proposed non-ergodicity conclusion.

## Evidence and References {#evidence-references}

- [Broadie's author preprint, Section 2](https://www.columbia.edu/~mnb2/broadie/Assets/strokes_gained_pga_broadie_20110408.pdf)
  establishes the benchmark definition and additivity and describes the
  additional near-optimal-strategy approximation in its DP discussion.
- [Sutton and Barto, Sections 3.5–3.6](https://www.andrew.cmu.edu/course/10-703/textbook/BartoSutton.pdf)
  distinguish policy evaluation from optimal values.
- [Gelman (2006)](https://sites.stat.columbia.edu/gelman/research/published/multi2.pdf)
  separates predictive pooling from causal interpretation of observational
  coefficients.

The previous general references to fat tails, prospect theory, and optimal
feedback control did not establish the claimed failure of SG accounting.
They are not retained as evidence for those withdrawn assertions.

## Severity

**Medium, governed open.** The concern is consequential when making individual
forecasts or prescriptions. It is not evidence that complete SG totals cease
to account for counted strokes.

## Suggested Remedies

### 1. Test State Sufficiency {#address-non-markovian-hidden-states}

Compare predictions across relevant conditions and future time periods. Examine
whether omitted history improves held-out predictions and whether measured
changes support the proposed mechanism. Avoid interpreting a negative SG value
as a diagnosis of anxiety or mechanical error.

### 2. State the Decision Objective {#discuss-risk-sensitivity}

Expected-score minimization and maximizing the chance of beating a threshold
can prefer different actions. The article's constructed four-stroke safe
outcome versus a three-or-seven risky outcome demonstrates this without
assigning universal risk preferences to golfers. Counted score is a cost;
worse expected scoring means a higher stroke count. SG can report either
policy's consequences without deciding which objective the golfer should use.

### 3. Separate Time Variation From Population Differences {#differentiate-ensemble-vs-time-averages}

Specify the process and time horizon before claiming nonstationarity or
non-ergodicity. Use repeated measurements, time-ordered validation, and
uncertainty that respects dependence. Personalization can improve forecasting;
causal claims still require a defined intervention and an identification
argument. The source and numerical review is tracked in
[issue #4358](https://github.com/D-sorganization/AffineDrift/issues/4358).
