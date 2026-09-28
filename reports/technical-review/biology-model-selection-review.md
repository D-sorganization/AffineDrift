# Biological Model Selection: Complete Chapter Review — #4463

## Scope and Argument

Read and corrected the complete Volume III opening chapter, its contradictory
introduction, and the public book map. Preserved the chapter, four equation,
three principle, comparison, remark, and public chapter destinations. There is
no paired chapter QMD; the linked notebook is a title scaffold, not executable
verification. The full 66-page PDF is regenerated, but this does not certify
other chapters or complete the corpus review under #4021/#4009.

The chapter connects the swing's inference chain: observed motion and external
loads; mass properties and contacts; candidate muscle forces and states;
activation/excitation; deformation and delivery. Each modeling choice defines
both a calculable quantity and a corresponding evidence requirement. Matching
clubhead motion alone cannot identify a muscle history or tissue stress field.

## Corrected Findings

1. **P1 — Compliance and Coordinates.** Replaced the dimensionally incomplete
   flexible equation with augmented rigid/modal coordinates, coupled inertia,
   projected elastic/damping loads, actuation, and constraint reactions. A free
   rigid club does not have one universal degree of freedom. Frequency response
   separates quasi-static compliance, resonance, and inertial response; controller
   bandwidth or cycles per downswing alone cannot establish negligible deformation.
2. **P1 — Muscle Force and Power.** Normalized passive force receives the same
   force scale as active force. Fibre force, tendon force, pennation, and path
   shortening differ. The declared moment-arm sign preserves virtual work and
   yields 0.8 W by independent joint and musculotendon calculations. Joint motion
   alone cannot classify fibre contraction, especially with compliant tendons.
3. **P1 — Redundancy and Identifiability.** Task-Jacobian and muscle-force maps
   have different domains, ranks, and constraints. The bounded allocation example
   has a feasible interval, not arbitrary muscle patterns. Dynamic realizability
   remains an additional requirement; fully specified internal states can fix
   tendon forces. Variability evidence does not directly reveal a neural projector.
4. **P1 — Anthropometry and Inertia.** The original code gives 0.826 of body mass
   with one row per type and 1.074 with both sides. Removed its unsupported de Leva
   attribution and regression-like routine. Retain those numbers only as an
   explicit accounting error and supply a separate synthetic unit-sum inventory.
   COM requires pose/frames; spatial inertia requires a tensor and origin, not
   an unspecified scalar moment. Derive its cross-block signs from kinetic energy.
5. **P1 — Input Affinity and State Closure.** Nonlinear state dependence does not
   disprove input affinity. A constant-time-constant activation model is affine
   in excitation; the declared branch-dependent law fails the affine midpoint
   identity across branches. State count, smoothness, constraints and contact
   modes determine applicability of geometric tools. Zero excitation retains
   activation history and is not equivalent to zero physiological force or power.
6. **P2 — Model Choice and Evidence.** Replaced universal engineering/biology
   binaries, unsupported anatomy/delay ranges and the unverified epigraph.
   Complexity is not validation, a muscle model does not uniquely identify neural
   drive, and ordinary musculoskeletal software is not automatically tissue FEM.
   Replace underdetermined exercises and arbitrary computational thresholds with
   explicit manufactured fixtures, target outputs, and measurement requirements.

## Numerical Verification

`tests/test_biology_model_selection_rigor.py` checks eight independent fixtures:

- Original and synthetic mass inventories, including bilateral duplication.
- COM value and translation covariance.
- Angular-first spatial inertia: symmetry, positive eigenvalues, principal-moment
  triangle inequalities, and agreement with the independently expanded kinetic
  energy for nonzero angular and translational velocity.
- Harmonic compliance below, at, and above the natural frequency, including phase.
- Joint/musculotendon power pairing with signed moment arms.
- Bounded force allocation and distinct nullspace projectors for two toy maps.
- Piecewise activation rates, failure of the cross-branch affine identity, and
  its validity within one activation branch.
- The constant-time-constant activation model's affine identity.

Six additional source regressions reject the specific false generalizations.
RED verification recorded six failures and eight numerical passes against the
original chapter. All 14 pass after correction. These are mathematical/software
checks, not participant data, physiological validation, or coaching evidence.

## Primary Sources and Access Limits

- [Millard et al. (2013)](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf):
  read the force normalization, pennation equilibrium, singularity and rigid-tendon
  sections. These support the chosen Hill-model conventions and the need to state
  model variants; they do not identify a golfer's parameters.
- [OpenSim activation API](https://opensim-org.github.io/opensim-moco-site/docs/1.3.0/html_user/classOpenSim_1_1MuscleFirstOrderActivationDynamicModel.html):
  checked the displayed branch equations and activation-floor discussion. The
  arithmetic example deliberately omits a floor and is not a claim of parity
  with every muscle class/version or with the normalized variant in Millard.
- [Scholz and Schöner (1999)](https://www.ini.rub.de/upload/file/1531404969_54ebac4c9aedb006e95d/ScholzSchoner99.pdf):
  read the hypothesis, task/variance formulation and general discussion. Distinguish
  the sit-to-stand findings from a universal neural mechanism or golf result.
- [de Leva (1996)](https://pubmed.ncbi.nlm.nih.gov/8872282/): the primary abstract
  establishes the landmark-adjustment scope. Full-table access was unavailable;
  no replacement empirical coefficients or claim of table-level verification is
  made. The mass counterexample is arithmetic on the old chapter's own numbers.
- [Delp et al. (2007)](https://graphics.stanford.edu/~erang/papers/opensim/Delp.OpenSim.2007.pdf):
  read the platform description and modeling context. Model-based internal-load
  inference is distinct from direct measurement or a local tissue continuum model.

## Delegation and Lead Review

Six agy `gemini-3.8-flash-high` plan-mode calls handled supplied-text inventory
grouping, claim extraction, proposed numerical tests/exercises, and two parallel
consistency passes. No agent was authorized to use tools, edit, browse, or publish;
the fleet dispatcher currently refuses unattended agy tool permissions (#1800).
No permission bypass or alternative provider was used.

The lead independently checked every adopted result. In particular, corrected a
proposed null-vector magnitude comparison, rejected the claim that nonlinear
state dependence alone prevents input affinity, and omitted overbroad continuum
claims from the proposed exercises. Adopted useful notation clarifications;
rejected dangling-reference flags caused by the supplied-text split. Agent output
is advisory local QA, not scientific evidence or an executed test receipt.

## Rendering and Publication Boundary

Print source/PDF checkpoint: `3875b82d18d27078d6d0aa22fcfa4ca4acf65a58`.
The book map pins the corrected chapter, main source and PDF there, retaining
the explicitly separate older notebook snapshots. The introduction and physical
pages 9–17 were visually read; final title/box-caption refinements and exercise
math fit without chapter overfull boxes or undefined references. Existing
book-wide warnings outside this scope remain for whole-book reconciliation.

The book page rendered locally and passed all four desktop/mobile × light/dark
production-verifier cases, with zero serious/critical axe violations. The chapter
summary and source/notebook separation were inspected in the browser.
Exact hashes and render evidence are in `biology-model-selection-render-verification.json`.
Protected merge and deployed-publication verification require a separate receipt;
local checks alone do not establish that the changes are live.
