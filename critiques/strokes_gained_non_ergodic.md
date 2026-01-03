# Critique: Strokes Gained Limitations and Ecological Fallacy

## Summary of Concern

The article `articles/strokes-gained-limitations.qmd` correctly identifies the "Ecological Fallacy" (applying population statistics to individuals) but fails to address the deeper problem of **Non-Ergodicity** and **Statistical Non-Stationarity** in human performance.
Strokes Gained assumes that a player's skill state is a fixed random variable sampled from a distribution. In reality, skill is time-varying (fatigue, psychology, "hot streaks").
Furthermore, the "Value Function" $J(x)$ assumes a **Markov Property** (state depends only on current lie). Real golf involves hidden states (confidence, previous hole outcome) that violate the Markov assumption.

## Location

- **File:** `articles/strokes-gained-limitations.qmd`
- **Section:** "Strokes gained as a population conditional expectation" & "A concrete putting example"

## Nature of the Issue

- **Hidden State / Non-Markovian Dynamics:** The formulation $J(d, c)$ assumes the state is fully observable. It ignores $S_t$ (Internal State).
- **Ergodicity Violation:** The "Expected Value" is an ensemble average. An individual player is a single time-series. If the process is not ergodic, the time-average does not equal the ensemble average.
- **Risk Neutrality Assumption:** The Bellman equation assumes risk-neutral minimization of expected strokes. Real players optimize a utility function $U(S)$ that includes variance minimization (avoiding double bogeys) or "hero shots" (convex utility) depending on tournament position.

## Why This Is a Problem

The article critiques the "Slope Mismatch" ($J'_i \neq J'_{ref}$) but misses the **Structure Mismatch**.
Even if we calculate a personal $J_i$, the _functional form_ is likely wrong because it assumes risk neutrality and state independence.
A player leading a tournament plays differently than one missing the cut. Strokes Gained treats a 5-footer on Thursday the same as a 5-footer to win the Masters. This is a failure of the **Cost Function Definition**.

## Evidence / References

- **Taleb, N. N.** - "Statistical Consequences of Fat Tails" (Ergodicity economics).
- **Kahneman & Tversky** - Prospect Theory (Loss aversion in putting).
- **Todorov** - "Optimal Feedback Control" (Risk-sensitive control).

## Severity

- **Medium** (The current article is good, but misses the "Control Theory" perspective on _why_ the metrics fail).

## Suggested Remedies

### 1. Address Non-Markovian Hidden States

Explicitly state that $J(x)$ is actually $J(x, \theta)$ where $\theta$ is a hidden internal state.

> "The Markov assumption—that the next shot depends only on the ball's position—ignores the 'hot hand', fatigue, and psychological pressure, which act as hidden state variables."

### 2. Discuss Risk Sensitivity

The objective function isn't just $E[Score]$. It's $E[U(Score)]$.

> "Strokes Gained assumes a linear utility function (risk neutrality). However, tournament dynamics often induce risk-averse (concave) or risk-seeking (convex) behaviors that fundamentally alter the optimal policy $\mu^*$, making the benchmark policy irrelevant."

### 3. Differentiate Ensemble vs Time Averages

> "Strokes Gained is an ensemble metric. A single player's season is a single realization of a stochastic process. Assuming this time-series converges to the population mean requires ergodicity, which is far from guaranteed in biological systems."
