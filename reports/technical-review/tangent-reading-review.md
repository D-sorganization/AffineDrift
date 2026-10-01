# Tangent Reading Guide Technical Review

Issue #4736; epic #4009. Base3e7d6958c20ffc01a3d35f1ae43d7ff527fe370f. Entire source articles/tangent-hyperplane-articles/TABLE_OF_CONTENTS.qmd read and revised. This is a full review of the guide, not a new certification of every linked manuscript. Publication and repository validation remain to be finalized before the inventory completion entry.

## Corrections and Rationale

1. Separate tangent vector spaces, exact first variations and finite nonlinear predictions. C1 alone gives little-o, not a uniform quadratic remainder. Retain finite-horizon/domain conditions.
2. Derive the finite-error equation r_dot=A r+N and retain transition-matrix propagation. Define scaled state/input coordinates, nominal motion, joint Hessian norm and the actual deviation inside the bound. A manufactured scalar example violates the earlier unweighted bound.
3. Distinguish discrete full-DDP curvature from iLQR: include the value-gradient-weighted dynamics Hessians. Do not identify a local quadratic solution with exact nonlinear rollout, optimizer convergence or global reachability.
4. Use the actual closed-loop Jacobian, metric material derivative, rate convention and regional/path conditions for contraction. Physical-time convergence is not optimizer-iteration progress. Stable eigenvalues need not imply Euclidean contraction.
5. Define guards, resets, event timing and saltation separately. State-triggered common-time sensitivity includes timing; reset derivatives and saltation are not generally rotations. State transverse isolated-event/fixed-sequence scope and limits near grazing or Zeno accumulation.
6. Replace residual-as-intrinsic-curvature claims, footstrike-as-smooth-curvature claims and gimbal-lock-as-physical-singularity claims with model/coordinate distinctions.
7. Connect model state, input intervention, feedback, propagation, contact-time convention and task output to testable golf/humanoid questions. Motion alone does not identify a unique neural control mechanism. A model calculation is not human validation.
8. Replace bare filenames and nonexistent critical-review pointers. Keep the canonical seven-part hub primary, full manuscript a deeper reference, and retired golf drafts outside the public reading path. Four links initially suggested by source inventory pointed to excluded critique manuscripts; the existing publication-boundary regression exposed them, and the guide now uses published critiques and current main-article conditions.
9. Remove competence/time guarantees, implied external review grades, unsupported novelty declarations and stale planned-feature status. Distinguish existing examples, exercises, pseudocode and proposed applications.
10. Correct Khalil/Lee/Sastry chapter pointers from primary contents. Remove unverified peripheral reading claims. Explicitly define all formula-specific notation; retain continuous Hamiltonian versus discrete Q distinction.
11. Disable the unnecessary Code button on this prose-only page after mobile screenshot review exposed severe title word splitting. Rendered source remains available in the repository.

## Primary Source Scopes

- Khalil author third-edition contents: https://www.egr.msu.edu/~khalil/NonlinearSystems/contents.html. Section3.3 sensitivity, chapter4 Lyapunov, chapter13 feedback linearization. TOC scope only.
- Lee official second-edition front matter: https://sites.math.washington.edu/~lee/Books/ISM/front-matter.pdf. Chapter3 tangent vectors/differentials/bundle; chapter4 submersions/immersions/embeddings. Front matter/TOC, not whole book.
- Sastry publisher contents: https://link.springer.com/book/10.1007/978-1-4757-3108-8. Named topic locations; no full-text theorem verification claimed.
- Tassa, Mansard and Todorov: https://roboti.us/lab/papers/TassaICRA14.pdf. Introduction and SectionII through Q derivatives/control update (physical pages1–2). Full dynamics-Hessian term and iLQR distinction verified; no reproduction of the paper's robot performance claimed.
- Lohmiller and Slotine author preprint: https://web.mit.edu/nsl/www/preprints/contraction.pdf. Opening/Sections2–3.4 through Theorem2 (physical pages1–8), including metric derivative and contained-ball conditions. Later applications and converse claims are not used to certify this guide.
- Kong, Payne, Zhu and Johnson: https://arxiv.org/html/2306.06862v2. Introduction and SectionIII-A definition/equation9/assumptions; timing versus reset derivatives, transversality and no-Zeno scope. Full paper/application reproduction not claimed.

Local cross-checks: Unified Thesis1433–1526 (full-Q/iLQR); Residual-Aware Control40–132 (scaled propagated remainder); Contraction main44–106 (actual closed loop/metric/paths); Hybrid main1–160 (mode/guard/reset/cost/saltation). Companion opening/headings were checked for navigation descriptions; entire companions were not newly reviewed. Quarto render exclusions and existing tangent-series navigation contract are authoritative for public availability.

## Independent Checks

Numerical and analytic counterexamples are recorded in tangent-reading-counterexamples.json. The propagated scalar remainder agrees with the analytic solution to roundoff, while the omitted-propagator candidate falls below the true error. Existing foundation/control/residual/contraction/hybrid regressions cover the underlying distinctions. Adding the guide to the navigation test produced a genuine RED publication-boundary failure for four excluded targets; after correcting links,94 selected tests pass.

## Delegation and Adjudication

Two original inventory jobs and two revised-draft jobs used agy Gemini3.8 Flash High with supplied text only, no tools/network/edits. Lead independently read sources, derived counterexamples, edited content and evaluated results. Accepted requests for explicit nominal variables, component/time indices, scaled transition definition, closed-loop variation and event-side notation. Removed an editorial changelog sentence. Rejected claims that finite affine predictions are always inexact, that approximate finite superposition can never be useful over long horizons, that all glossary entries must appear elsewhere, or that a guide must link every archived/PDF/source file. Rejected sentence-heading objections (title-case checker passed). Source existence did not establish publication availability; lead's render-config/test inspection corrected that omission. Learning activities are not promises of turnkey code or human efficacy.

## Validation Status

Initial Quarto HTML render succeeded. Four width/theme checks initially failed because the bounded local preview had not applied the normal deployment polyfill stripping and had no served manifest; no content/layout or serious/critical axe failures occurred. Applied only the existing polyfill-cleanup helper to the generated article and served an official, one-page manifest; four cases then passed with zero serious/critical axe findings. This is bounded local evidence, not full-site deployment. Final HTML render and all four browser cases/axe pass after Code-button removal and equation line wrapping. Math inspection records86 containers, zero MathJax errors and zero page overflow at390/1440.94 focused and184 content tests pass (four skips),653-source title check, Ruff and Black pass. Shared mobile math remains smaller than body text; no global CSS change is part of this source review. Repository full suite and final source-commit inventory binding remain pending.
