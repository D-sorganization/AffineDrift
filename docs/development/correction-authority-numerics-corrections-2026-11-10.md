# Correction-Authority Numerics Corrections — 2026-11-10

Parent epic: [AffineDrift#5565](https://github.com/D-sorganization/AffineDrift/issues/5565).
Adversarial architecture review (2026-11-09), panel-validated numerics wave (NC family).

This note records **public, factual corrections** to simulation-only correction-authority
margins. It does not restate private security findings.

## What Was Wrong

### NC-01 (#5566) — LTV reachability Gramian recursion

The offline evaluator in `src/affine_control/correction_authority_evaluator.py` used a
backward sweep that matches the horizon-end reachability Gramian only when the linearization
is time-invariant. For time-varying `(A_k, B_k)` along a swing linearization, reported Gramians
and any margin derived from them could be materially wrong (panel repro: relative Frobenius
error about 0.72 on a random four-step LTV case).

**Status:** fixed on `main` in [AffineDrift#5569](https://github.com/D-sorganization/AffineDrift/pull/5569)
(refs #5566). Branches that have not merged that fix still run the old recursion.

### NC-02 (#5567) — Cauchy-Schwarz outer bound on correction authority

The same evaluator reported a correction-authority radius via a Cauchy-Schwarz rescaling of the
Gramian quadratic form. That quantity is an **outer** bound: it can label targets as recoverable
when they are not (panel example: double integrator along a tested direction, exact margin 0.5,
evaluator treated 0.55 as recoverable).

**Status:** open; tracked as [#5567](https://github.com/D-sorganization/AffineDrift/issues/5567).
Replacement uses a peak-per-channel support function under the declared input bound.

## What Readers Should Not Trust Yet

Until **both** #5566 and #5567 are fixed on the branch that feeds a page, and committed
artifacts are regenerated:

- Any numeric **margin**, **recoverable** flag, or **lead-time** summary produced by
  `evaluate_correction_authority_along_trajectory` or Option A comparison exports
  (`data/humanoid_robotics/option_a/comparison_result_v1.json` when present).
- Any prose that treats those numbers as final simulation evidence rather than preregistered,
  pre-regeneration placeholders.

Closed-form oracles in `correction_authority_contract.py` for declared toy systems are not
affected by NC-01/NC-02; governed trust panels that cite only analytic DCR or reachability
bounds without the offline evaluator are out of scope for this note.

## Pages Carrying an Under-Correction Banner

| Surface | Rationale |
| --- | --- |
| [Drift-Control Ratio](../../articles/drift-control-ratio.qmd) | Describes the preregistered correction-authority analysis contract and evaluator gates (`κ_max`). |
| Option A comparison results doc and trust panel | When merged (#5209), cite evaluator-derived margins; add the same banner at publication time. |

## Removal Criteria

Remove banners and update this note when:

1. #5566 and #5567 are closed on the publishing branch,
2. evaluator-derived artifacts are regenerated and cited numbers updated, and
3. governance tests that lock comparison exports pass on CI.

Refs #5565, #5566, #5567.
