# Degrees-of-Freedom Chapter Review

Issue #4845; epic #4009 / corpus #4021. Baseline `66c166693f2bba2120d9d3b9af59a27648ba69f9`. Scope: complete Volume IV Chapter 1 source, its printed reaching example, diagram and exercises, plus the Chapter 1 landing summary. The lead read the complete original and revised chapter. Full regression and final acceptance binding are pending; no original-corpus row has yet received credit.

## Argument and Corrections

The chapter connects three questions: which variations preserve a declared outcome, which trajectories the body and implement can physically realize, and which observations distinguish competing control mechanisms. A golfer can preserve club position while changing delivery velocity, contact location or subsequent loading. Task equivalence is therefore conditional on the chosen output, state, event and uncertainty.

1. **Rank and Force Feasibility.** Replace unconditional degree counts with local constant-rank level-set dimension. Separate configuration freedom from muscle-force allocation, activation dynamics and trajectory feasibility. A tensile-force example shows how bounds can reduce a one-dimensional equality solution to one feasible point.
2. **Golf Task State.** A rigid pose alone does not specify impact or ball flight. Define a terminal state map and distinguish its domain from a configuration-only Jacobian. Remove unsupported anatomical counts and a universal delay-based control dimension.
3. **Curvature and Singularities.** Distinguish exact task level sets from tangent kernels. The circle example gives a second-order residual and a singular point where Jacobian nullity overcounts exact solutions.
4. **Metrics and Statistics.** Declare coordinate scaling, orthogonality, relative numerical rank and the sample covariance convention. Normalize projected variance by subspace dimension; absent groups and zero denominators are undefined. A variance ratio is neither a significance test nor task-output covariance.
5. **Control Inference.** Two stable stochastic systems have the same stationary covariance despite different restoring dynamics and noise. This manufactured counterexample limits neural inference from covariance alone; it does not reanalyze participants or fit a golfer.
6. **Executable Example.** Replace the incomplete printed UCM routine with a tested importable decomposition and a complete three-link reaching example. Six constructed points produce a known 9:1 ratio; an isotropic control gives 1, and finite endpoint displacement exposes the linearization error.
7. **Learning and Drift.** Bound the freezing/freeing interpretation rather than asserting a universal sequence or exact dimension reduction. Explain why small joint motion, mechanical locking, stiffness and changed policy differ. Connect passive mechanics to admissible trajectories without identifying wrist release with zero muscle action.

## Primary Reading and Limits

- [Latash, 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3532046/): complete main prose and figure caption read (web extraction lines 62–123). Figure pixels and linked studies were not inspected. This mini-review develops the author's motor-abundance interpretation; it is not a direct golf experiment or proof of one neural implementation.
- [Scholz and Schöner, 1999](https://www.ini.rub.de/upload/file/1531404969_54ebac4c9aedb006e95d/ScholzSchoner99.pdf): selected primary PDF text read (extraction lines 0–95, 255–346, 553–649 and 836–904), including the nine-participant sit-to-stand context, local task decomposition and sensitivity discussion. Other text and all figure pixels remain unread. The chapter uses an explicitly stated sample denominator, not a claim to reproduce the original numerical analysis or its convention.
- Existing Bernstein and Agrachev–Sachkov references remain background. No complete-book reading or page-specific quotation is claimed. The unverified Bernstein epigraph was removed. Previously corrected Volume III muscle-accounting and Volume IV biological-dynamics material informed consistency checks without conferring whole-book acceptance.

The mathematical examples are independent manufactured checks of the declared idealizations. No human dataset, raw experimental replication, clinical efficacy or golf-coaching outcome is established. Historical notebook links are preserved and explicitly excluded from this numerical review.

## Validation and Publication Scope

The initial module test run failed because the implementation did not yet exist (20 failures, two independent identity passes). The printed-example red run failed because the old listing did not expose the complete reaching helpers and results. After implementation, 24 focused cases passed. These are test-development records, not a claim that every red case demonstrated a defect in the old numerical output.

The native 72-page PDF builds successfully. All seven revised chapter pages and the two changed final bibliography pages were visually inspected after the final source edit. The chapter has no overfull boxes or unresolved citations/references. All 54 later body pages preserve normalized text; all 44 previous bibliography entries survive, with Latash2012 added. Citation numbers and pagination change. Untouched layout warnings elsewhere remain outside this acceptance.

The one-route browser matrix passes at 390/1440 pixels in light/dark themes, with zero serious/critical axe violations. Settled section screenshots are legible and their links were inspected. The local preview required a scoped manifest because the checkout's placeholder index lacked an H1; initial failure artifacts remain in QA. This is not a full-site or deployed-site pass. Render evidence and explicit dependency carry-forward are separate JSON records. Earlier scientific review dates, commits and scopes are retained in the prior-record snapshot.

The last two agy Gemini 3.8 Flash generation requests failed for insufficient credits. No fresh helper output is claimed; the lead performed this review. Broader gates, full regression, final source binding and delivery remain pending at this checkpoint.

The broader audit check rejected an initial change to historical finding rationales and evidence-path lists. Those fields were restored; the dependency explanation lives in a separate carry-forward record. The test now consults both historical snapshots while preserving the same immutability assertion. A final numerical red test reproduced finite-input SVD overflow being misclassified as zero rank; the implementation now rejects nonfinite singular values.

At the pre-regression checkpoint, all 149 selected UCM, printed-example, prior motor-control, book-audit, claim-inventory, handoff and SPEC cases pass, including 25 new numerical cases. Ruff, Black100, configured mypy (98 existing source files), strict module mypy, the Python quality checker, 665 title checks, all twelve publication gates and generated-report freshness pass. The quality checker initially flagged missing docstrings in untracked QA helpers; those local helpers were corrected without changing product behavior. Full regression remains pending.
