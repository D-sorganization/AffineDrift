# Comprehensive Technical Review: AffineDrift Website

**Date:** March 12, 2026
**Scope:** Full-stack review covering technical claims, UI/UX, implementation quality, and maintainability
**Reviewer:** Automated comprehensive audit

---

## Executive Summary

AffineDrift is an ambitious Quarto-based website presenting novel applications of control theory, differential geometry, and nonlinear dynamics to golf swing biomechanics. The site contains ~146 QMD content files, 4 book volumes, multiple article series, and extensive supplementary resources. This review identifies **104 issues** across four domains:

- **Technical Claims & Content Accuracy**: 48 issues (8 critical, 17 major, 23 moderate)
- **UI/UX & Website Implementation**: 22 issues (3 critical, 8 major, 11 moderate)
- **Maintainability & Architecture**: 22 issues (4 critical, 9 major, 9 moderate)
- **Content Completeness & Quality**: 12 issues (2 critical, 6 major, 4 moderate)

---

## Part I: Technical Claims & Content Accuracy

### CRITICAL Issues

#### ISSUE-TC01: Control-Affine Assumption Scope Overreach
**Files:** `articles/theory-part1.qmd`, `articles/affine-nature-golf-swing.qmd`, `articles/superposition.qmd`
**Severity:** CRITICAL

The core framework claims that the golf swing is a control-affine system: `ẋ = f(x) + G(x)u`. While this is a standard and useful modeling framework, the articles frequently make **categorical claims** that exceed the scope of this assumption:

1. **Muscle force-velocity coupling**: Hill's muscle model introduces multiplicative (not additive) coupling between activation and velocity, violating affine structure. The articles mention this limitation in `sources-of-nonlinearity.qmd` but the core theory articles (Part 1-3) do not adequately caveat this.
2. **Co-contraction and impedance modulation**: When antagonist muscles co-contract, they produce zero net torque but modulate joint stiffness. This stiffness modulation occurs in the null space of the torque map and is not captured by the affine input structure.
3. **History-dependent effects**: Fatigue, calcium buffering, and metabolite accumulation mean the effective input matrix G depends on movement history, not just instantaneous state.

**Recommendation:** Add explicit scope-limitation sections to theory-part1 and theory-part2 clarifying that the control-affine structure applies at the **joint-torque level** as a modeling choice, not as a physical truth. The existing `sources-of-nonlinearity.qmd` already addresses many of these concerns but is not cross-referenced from the core theory.

---

#### ISSUE-TC02: Superposition Claims Require Stronger Temporal Caveats
**Files:** `articles/superposition.qmd`, `index.qmd`, `overview.qmd`
**Severity:** CRITICAL

The superposition article (1,200+ lines) establishes that force superposition holds **instantaneously** at fixed state. This is mathematically correct. However:

1. The homepage states "generalized forces DO superpose" without the instantaneous caveat, implying trajectory-level superposition.
2. Several articles reference "force superposition" without clarifying it is an instantaneous property that requires re-evaluation as state evolves.
3. The phrase "Instantaneous Force-Acceleration Superposition" (used in the Tangent Hyperplane series) is more precise but is not consistently used across the site.

**Recommendation:** Standardize on the term "Instantaneous Force-Acceleration Superposition" across all articles. Add the instantaneous caveat to the homepage framework section.

---

#### ISSUE-TC03: Novel Claims Not Clearly Distinguished from Established Results
**Files:** Multiple tangent hyperplane articles, textbook chapters
**Severity:** CRITICAL

The site mixes well-established results from control theory/differential geometry with novel interpretations and applications. Readers cannot easily distinguish:

1. **Established**: Control-affine systems, tangent space linearization, contraction analysis, Lie bracket accessibility
2. **Novel interpretation**: Application to golf biomechanics, "drift/input" decomposition naming, ZTCF/ZVCF counterfactual framework
3. **Potentially novel**: Integral superposition framework, residual-aware control design, specific contraction-tangent unification claims

**Recommendation:** Add a "Novelty Status" callout to each major article indicating whether the content is: (a) established textbook material, (b) novel application of existing theory, or (c) potentially novel theoretical contribution.

---

### MAJOR Issues

#### ISSUE-TC04: ZTCF (Zero-Torque Counterfactual) Identifiability Gap
**Files:** `articles/theory-part2.qmd`, `articles/inverse-dynamics-inference.qmd`
**Severity:** MAJOR

The ZTCF framework (setting u=0 to observe pure drift) is conceptually valuable but faces a **practical identifiability problem**: you cannot directly measure or observe the ZTCF trajectory from real golf swing data because:
1. The golfer is always applying some control input
2. Muscle tone maintains joint stiffness even during "passive" phases
3. Separating gravitational, Coriolis, and centrifugal contributions from measured motion requires knowing the full system model

The existing critique in `critiques/ztcf_identifiability.md` identifies this issue but the main articles do not adequately address it.

**Recommendation:** Add a "Practical Considerations" section to theory-part2 addressing identifiability and referencing the critique.

---

#### ISSUE-TC05: Dimensional Inconsistency in Drift-Control Ratio (DCR)
**Files:** `articles/controllability-drift-ratio.qmd`
**Severity:** MAJOR

The DCR is defined as a ratio of norms, but the choice of norm affects the numerical value and physical interpretation:
1. The article uses the kinetic energy norm (`M(q)`-weighted) for accelerations, which is physically motivated
2. However, the DCR is also compared across different joints/DOFs without normalizing for the different physical dimensions (some are rotational, some translational)
3. The existing critique `critiques/dimensional_inconsistency_dcr.md` identifies this but the article has not been updated

**Recommendation:** Add a section on dimensional consistency, norm choice sensitivity, and cross-joint comparison caveats.

---

#### ISSUE-TC06: Lie Bracket Formalism Overreach
**Files:** `articles/theory-part3.qmd`, tangent hyperplane series
**Severity:** MAJOR

Several articles invoke Lie brackets for accessibility analysis, but:
1. The Lie bracket condition (LARC) provides **local** accessibility, not global controllability
2. The articles sometimes conflate accessibility with controllability
3. For underactuated systems (like the golf swing), the distinction is crucial

**Recommendation:** Clarify the distinction between accessibility and controllability wherever Lie brackets are discussed.

---

#### ISSUE-TC07: Contraction-Tangent Unification Claims Need Proof Completion
**Files:** `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_Unification.qmd`
**Severity:** MAJOR

The contraction-tangent unification article makes ambitious claims about bridging contraction analysis with tangent space methods, but several key results are stated without complete proofs. The connection to Lohmiller & Slotine's contraction analysis framework needs more rigorous mathematical development.

**Recommendation:** Either complete the proofs or explicitly mark incomplete results as conjectures.

---

#### ISSUE-TC08: "Control Is Motion" Paradigm Lacks Formal Definition
**Files:** `books/control-is-motion.qmd`, various articles
**Severity:** MAJOR

The phrase "Control Is Motion" is used as a paradigm label throughout the site but lacks a formal mathematical definition. It appears to mean "control inputs are best understood through their geometric effects on the configuration manifold" but this is never precisely stated. This makes it difficult for readers to evaluate or critique the claim.

**Recommendation:** Provide a formal definition of what "Control Is Motion" means mathematically, distinct from the standard control-affine formulation.

---

### MODERATE Issues

#### ISSUE-TC09: Intermediate Axis Theorem Misapplication
**Files:** `articles/secondary-axis-stability.qmd`
**Severity:** MODERATE

The article discusses stability about the intermediate axis of inertia (Dzhanibekov effect) but the application to the golf club is questionable since:
1. The golf club is not a free rigid body (it's attached at the grip)
2. The relevant instability is about the constraint reaction, not free-body rotation
3. The existing critique `critiques/intermediate_axis_fallacy.md` identifies this

**Recommendation:** Revise to clearly distinguish constrained vs. free-body rotation dynamics.

---

#### ISSUE-TC10: Strokes Gained Critique Makes Strong Non-Ergodicity Claim
**Files:** `articles/strokes-gained-limitations.qmd`
**Severity:** MODERATE

The article claims strokes gained is fundamentally flawed due to non-ergodicity. While the statistical critique has merit, the claim that strokes gained "fails" is overstated. Strokes gained is a descriptive statistic, not a causal model.

**Recommendation:** Reframe as "limitations of strokes gained as a causal analysis tool" rather than a fundamental failure.

---

#### ISSUE-TC11: Wrist-as-Universal-Joint Model Simplification
**Files:** `articles/wrist-universal-joint.qmd`
**Severity:** MODERATE

The wrist is modeled as a universal joint (2-DOF), but the actual wrist has 3 DOF (flexion/extension, radial/ulnar deviation, pronation/supination). The simplification is reasonable but the limitations are not discussed in the main article.

---

#### ISSUE-TC12: Double Pendulum Model Energy Considerations
**Files:** `articles/drift-components-wrench-double-pendulum.qmd`
**Severity:** MODERATE

The double pendulum wrench analysis focuses on force decomposition but does not discuss energy balance. Energy is a fundamental constraint that should be addressed, especially for the ZTCF where energy is conserved (no input work).

---

#### ISSUE-TC13: Intentional Constraint Collapse Needs Formal Treatment
**Files:** `articles/intentional-constraint-collapse.qmd`
**Severity:** MODERATE

"Intentional Constraint Collapse" (ICC) is presented as a deliberate strategy but the mathematical formalization is incomplete. When/why is ICC optimal vs. maintaining constraints? The answer likely involves the DCR approaching specific threshold values but this connection is not made explicit.

---

#### ISSUE-TC14: Textbook Chapters Reference Theorems Without Full Proofs
**Files:** `articles/tangent-hyperplane-contraction/chapters/*.qmd`
**Severity:** MODERATE

Several textbook chapters reference theorems (e.g., "Theorem 3.1", "Proposition 4.2") but the proofs are either sketched or deferred. For a textbook, this needs to be resolved before publication.

---

#### ISSUE-TC15: Bibliography Cross-Reference Gaps
**Files:** Multiple articles, `data/bibliography.json`
**Severity:** MODERATE

Some articles reference works that do not appear in the centralized bibliography (120 entries). The bibliography system appears well-maintained but cross-referencing is inconsistent:
- Some articles use inline citations
- Some use the Quarto citation system
- Some use neither and just mention authors by name

**Recommendation:** Standardize on Quarto's built-in citation system across all articles.

---

#### ISSUE-TC16: ZVCF Definition Error in inverse-dynamics-inference.qmd
**File:** `articles/inverse-dynamics-inference.qmd:97-103`
**Severity:** CRITICAL

The article states "The Zero Velocity Counterfactual (ZVCF) holds the state fixed and disables drift contributions. Gravity, shaft elasticity, and other passive contributions are set to zero. Only the input vector fields G(x)u remain active." This is **factually incorrect** based on the definition in all other articles. The ZVCF sets velocities to zero but evaluates the *drift* at zero velocity, yielding configuration-dependent forces (gravity + elasticity). It does NOT isolate input forces. The claim `F_ZVCF = F_input` contradicts every other article in the series, which consistently defines ZVCF as the configuration-dependent *slice of drift*.

**Recommendation:** Correct the ZVCF definition to match the rest of the series. This is a fundamental definitional error that undermines the article's credibility.

---

#### ISSUE-TC17: State Vector Ordering Inconsistency Across Articles
**Files:** `articles/theory-part1.qmd`, `articles/affine-nature-golf-swing.qmd`
**Severity:** CRITICAL

The state vector ordering is inconsistent:
- Notation tables define `x = [q, η, q̇, η̇]` (positions grouped, then velocities)
- The f(x) and g(x) definitions use `x = [q, q̇, η, η̇]` (rigid DOFs grouped, then flexible)

This inconsistency appears in both theory-part1 and the full affine-nature-golf-swing.qmd article. The f(x) matrix structure assumes one ordering while the notation table defines another.

**Recommendation:** Standardize on one ordering throughout and verify all matrix expressions match.

---

#### ISSUE-TC18: Markdown `*` Rendering as `+` in Superposition Equations
**File:** `articles/superposition.qmd:373-376, 559, 635-636, 645, 773-774, 1333-1335, 1399-1401`
**Severity:** CRITICAL (produces incorrect mathematical output)

Multiple equation blocks contain bare `*` characters that are being interpreted as markdown bold/italic markers instead of mathematical operators. For example, line 374: `* M(q)^{-1}τ` should be `+ M(q)^{-1}τ`. This is a systematic issue that produces **incorrect equations in the rendered output**.

**Recommendation:** Escape all `*` characters in equations or use `\ast` or `\cdot` in LaTeX math mode.

---

#### ISSUE-TC19: Numerical Identity `F_total - F_ZTCF = F_ZVCF` Lacks Rigorous Justification
**File:** `articles/theory-part5.qmd:123-128, 269-275`
**Severity:** MAJOR

The claimed identity `F_total(t) - F_ZTCF(t) = F_ZVCF(t)` is presented as a validated numerical result, but it is mathematically suspect. The ZTCF forces are evaluated along the *ZTCF trajectory* (which diverges from the actual trajectory), while F_total is evaluated along the actual trajectory. This subtraction is only clean at t=t_0 where both trajectories share the same state. The theoretical justification is not provided.

**Recommendation:** Either provide a rigorous proof of this identity or explicitly note it is an approximation that is exact only at t_0.

---

#### ISSUE-TC20: "Mechanical Orthogonality" Term Misused
**File:** `articles/theory-part2.qmd:68`
**Severity:** MAJOR

The term "Mechanical Orthogonality" is used to describe the additive separability of drift and input terms. However, "orthogonality" has a precise mathematical meaning (inner product = 0) that is not what is meant here. The terms are additively separable (linearly independent contributions), not orthogonal in any inner-product sense.

**Recommendation:** Replace "Mechanical Orthogonality" with "Mechanical Separability" or "Additive Decomposition" and add a note explaining the terminology.

---

#### ISSUE-TC21: Incomplete/Missing 3D Pendulum Examples
**File:** `articles/theory-part4.qmd:399-403`
**Severity:** MAJOR

The article introduction promises "a spatial (3D) pendulum with and without a flexible shaft" but only presents planar (2D) pendulum examples. The 3D examples are referenced in the summary but never derived.

**Recommendation:** Either add the 3D examples or remove the promise from the introduction.

---

#### ISSUE-TC22: DCR "Monotonic Growth Invariance" Proof Is Informal
**File:** `articles/controllability-drift-ratio.qmd:311-313`
**Severity:** MAJOR

The claimed "theorem" about norm-independent monotonic growth is stated formally but proved by a qualitative "squeeze theorem" argument. The claim that "every component of drift increases and every component of control decreases" is not necessarily true component-wise -- it is the norms that grow/shrink, not necessarily every component.

**Recommendation:** Either provide a rigorous proof or downgrade from "theorem" to "conjecture" or "empirical observation."

---

#### ISSUE-TC23: Unsupported Quantitative Claims in DCR Article
**File:** `articles/controllability-drift-ratio.qmd:287, 386`
**Severity:** MODERATE

Claims like "DCR increases by 100x-300x" and "Collapse begins 70-120 ms before impact" are stated without citation or simulation data. These appear to be estimates from a planar model but are presented as facts.

**Recommendation:** Add citations, simulation references, or mark as estimates.

---

#### ISSUE-TC24: Inconsistent Block Matrix Naming Across Articles
**Files:** `articles/theory-part4.qmd`, `articles/affine-nature-golf-swing.qmd`
**Severity:** MODERATE

Inertia matrix blocks are called `M_rr, M_rf, M_fr, M_ff` in theory-part4 but `M_qq, M_qη, M_ηq, M_ηη` in affine-nature-golf-swing.qmd. Both conventions appear without cross-referencing.

**Recommendation:** Standardize block matrix naming and add a notation reference table.

---

#### ISSUE-TC25: Terminology Inconsistency: "Causal Orthogonality" vs "Mechanical Orthogonality"
**Files:** `articles/affine-nature-golf-swing.qmd`, `articles/theory-part2.qmd`
**Severity:** MODERATE

The full article uses "Causal Orthogonality" while theory-part2 uses "Mechanical Orthogonality" for the same concept.

---

#### ISSUE-TC26: Broken Quarto Cross-Reference Syntax
**File:** `articles/affine-nature-golf-swing.qmd` (throughout)
**Severity:** MODERATE

Multiple uses of LaTeX-style cross-references (`Section~@sec-affine`, `Equation~@eq-affine_repeat`) that may not render correctly in Quarto. Some references use colon-based labels (`@subsec:assumptions`) while others use hyphen-based (`@sec-affine`). These likely produce broken links in the rendered output.

---

#### ISSUE-TC27: Inverse Dynamics Article Has Placeholder Figures and Tables
**File:** `articles/inverse-dynamics.qmd:201, 229, 253, 277, 384, 438, 535, 674, 602`
**Severity:** MODERATE

8 figure placeholders (`[Figure: ...]`) and 1 table placeholder (`[Table]`) indicate incomplete content. This article also has truncated text at lines 552 and 564, and mixed unit systems (lbs vs N).

---

#### ISSUE-TC28: Air Resistance Calculation Self-Contradicts
**File:** `articles/inverse-dynamics.qmd:496-531`
**Severity:** MODERATE

The step-by-step air drag calculation computes a result, then says "But wait -- this is incorrect" and restarts with a different approach. The final comparison claims a 40% reduction but the arithmetic path is muddled and self-contradicting.

**Recommendation:** Clean up into a single coherent derivation.

---

#### ISSUE-TC29: Controllability Gramian Used Without Linearization Caveat
**File:** `articles/controllability-drift-ratio.qmd:546-550`
**Severity:** MODERATE

The Gramian-based reachable ellipsoid formula is stated without noting it is valid only for linearized systems. For the nonlinear system being discussed, this is an approximation.

---

#### ISSUE-TC30: Equation Numbering Conflicts in Superposition Article
**File:** `articles/superposition.qmd:1251`
**Severity:** MODERATE

Equation tag `(7.1)` is used in a section labeled "8.1", indicating numbering carried over from a draft reorganization.

---

#### ISSUE-TC31: Unrevised AI Draft Text in Hybrid Tangent Spaces Article
**File:** `articles/Tangent Hyperplane Articles/Advanced/Hybrid_Tangent_Spaces.qmd:581, 913, 969`
**Severity:** CRITICAL

Three instances of unedited AI draft self-correction text visible in the published article:
- Line 581: "Wait, let me recalculate"
- Line 913: "Wait, let me correct this"
- Line 969: "Wait, this doesn't look right"

These are clear evidence of AI-generated content that was not reviewed before publication. While the corrected results that follow are mathematically correct, the draft process text is unprofessional and damages credibility.

**Recommendation:** Remove all "Wait, let me..." text and present only the corrected derivations.

---

#### ISSUE-TC32: Fabricated or Unsourced Empirical Claims in Tangent Hyperplane Articles
**Files:** `Contraction_Tangent_Unification.qmd:817, 931-963`, `Residual-Aware_Control.qmd:25, 805-853`
**Severity:** CRITICAL

Multiple articles present specific numerical results as empirical data without any citation or data source:
1. **Contraction article line 817**: "Professional golfers exhibit γ(t) > 0.5 throughout swing, while amateurs have γ(t) < 0.2" -- no citation or data source. Appears fabricated.
2. **Contraction article lines 931-963**: Specific results for a "KUKA LWR 7-DOF arm" experiment with no citation. If simulated, labeled misleadingly.
3. **Residual-Aware Control line 25**: Claims "experimental validation on quadrotor aerobatics, humanoid walking, and golf swing optimization" but all results appear to be simulations.
4. **Residual-Aware Control lines 805-853**: References "ATRIAS bipedal robot" with specific numbers but no citation.

**Recommendation:** Either cite real experimental sources or clearly label results as simulated. Remove unsourced quantitative claims about golfer performance.

---

#### ISSUE-TC33: Residual Bound Dimensional Error and Factor-of-10 Calculation Mistake
**File:** `articles/Tangent Hyperplane Articles/Advanced/Residual-Aware_Control.qmd:159, 165-168`
**Severity:** MAJOR

Two errors in the pendulum residual calculation:
1. Line 159: Hessian bound units stated as s⁻¹, should be s⁻² (dimensions are rad/s² per rad)
2. Lines 165-168: The calculation yields ‖r‖ ≤ 0.0049 rad ≈ 0.28°, but the text claims "0.05 rad (2.8 degrees)" -- a factor of 10 error

**Recommendation:** Fix both the dimensional units and the numerical result.

---

#### ISSUE-TC34: Riemann Curvature Tensor Conflated with Hessian Remainder
**File:** `articles/Tangent Hyperplane Articles/Tangent_Hyperplanes_Unified_Thesis.qmd:749`
**Severity:** MAJOR

The equation uses R for both "residual" and "Riemann curvature tensor," and claims the second-order Taylor remainder involves the Riemann curvature. In ℝⁿ (flat space), the Riemann curvature tensor is identically zero. The relevant object is the Hessian of f, not the Riemann curvature of the state-space manifold. This is a significant conceptual conflation.

---

#### ISSUE-TC35: Residual Bound in Unified Thesis Uses Wrong Quantity
**File:** `articles/Tangent Hyperplane Articles/Tangent_Hyperplanes_Unified_Thesis.qmd:728`
**Severity:** MAJOR

The residual bound ‖r‖ ≤ C ε² ∫‖A(t)‖dt uses the Jacobian norm ‖A(t)‖ instead of the Hessian norm ‖H_f‖. The Jacobian governs perturbation growth, not residual magnitude. The correct bound should involve the Hessian (as done in the Residual-Aware Control article).

---

#### ISSUE-TC36: Double Integrator ARE Solution Appears Numerically Incorrect
**File:** `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_Unification.qmd:547-558`
**Severity:** MAJOR

The double integrator example claims Q = diag(16, 1), R = 1 gives specific S∞ and eigenvalue values. For these weights, the standard ARE solution yields different gains than stated. The claimed gain K = [2, 2] does not correspond to the stated Q, R values.

**Recommendation:** Verify the ARE solution numerically and correct the example.

---

#### ISSUE-TC37: "Exact" Language Inconsistency Across Tangent Hyperplane Series
**Files:** Multiple tangent hyperplane articles
**Severity:** MODERATE

The parallel article series (parts 1-4 in `tangent-hyperplanes-series/`) hedges on "exactness" calling linearization an "excellent approximation" (part-1-geometry.qmd:48), while the Unified Thesis insists on "exact, not approximate." This internal contradiction undermines the core messaging. The Critics Corner acknowledges this issue but the proposed terminology fix has not been implemented.

---

#### ISSUE-TC38: Integral Accumulation Principle Stated Too Broadly
**File:** `articles/Tangent Hyperplane Articles/Tangent_Hyperplanes_Unified_Thesis.qmd:1140-1155`
**Severity:** MODERATE

The callout claims Ψ(u₁ + u₂) = Ψ(u₁) + Ψ(u₂) when g is linear in u. But if the state trajectory x(t) depends nonlinearly on u, then the superposition breaks. The principle only holds for variations at fixed x(t), which the warning box partially addresses but the formal statement does not qualify.

---

#### ISSUE-TC39: Stochastic Contraction Metric Equation Non-Standard
**File:** `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_Unification.qmd:771`
**Severity:** MODERATE

The noise term ½ S G Σ Gᵀ S does not match standard stochastic Riccati equations, which have additive noise terms. If this is a nonstandard formulation, justification is needed.

---

#### ISSUE-TC40: Frechet Derivative Definition Error in Critics Corner
**File:** `articles/Tangent Hyperplane Articles/CRITICS_CORNER.qmd:64`
**Severity:** MODERATE

The Frechet derivative is written as A = lim(δx→0) [f(x+δx) - f(x)] / ‖δx‖, which divides a vector by a scalar giving a vector, not a matrix. The correct definition is: A is the linear map satisfying ‖f(x+δx) - f(x) - Aδx‖ / ‖δx‖ → 0.

---

#### ISSUE-TC41: Unified Thesis Part III Explicitly Incomplete
**File:** `articles/Tangent Hyperplane Articles/Tangent_Hyperplanes_Unified_Thesis.qmd:1281`
**Severity:** MODERATE

Line 1281 states: "This part is intentionally brief in the current version... Part III requires substantial expansion." This is a published document with an acknowledged incomplete section.

---

#### ISSUE-TC42: File Extension Mismatches in Cross-References
**Files:** `TABLE_OF_CONTENTS.qmd:75-82`, `LAYMANS_TERMS_SUMMARY.qmd:209`
**Severity:** MODERATE

Multiple cross-references use `.md` extension when actual files are `.qmd`. References to `LAYMANS_TERMS_SUMMARY.md`, `TECHNICAL_ASSESSMENT.md`, `CRITICAL_REVIEW.md` will produce broken links.

---

#### ISSUE-TC43: Books Section Systematic Cross-Reference Mismatch
**Files:** `books/tangent-space-methods.qmd`, `articles/tangent-hyperplane-contraction/chapters/`, `articles/The_Geometry_of_Motion/`
**Severity:** CRITICAL

The Books landing page (`books/tangent-space-methods.qmd`) describes chapter titles that match *The Geometry of Motion* (GoM) Volume I naming conventions, but the HTML links point to the Tangent Hyperplane Contraction (THC) chapter files, which have **different titles, scopes, and much thinner content**. For example:
- Chapter description says "Foundations of Nonlinear Dynamics" (GoM naming)
- Link points to `articles/tangent-hyperplane-contraction/chapters/01-foundations.html` (THC file)
- The THC chapter covers different material at much less depth

This means the Books section's chapter descriptions systematically misrepresent the content they link to. Readers clicking through get unexpectedly different material.

**Recommendation:** Either update the Books page descriptions to match the THC chapter content, or re-point the links to the GoM chapters. Alternatively, consolidate the two textbook projects into one canonical version.

---

#### ISSUE-TC44: Schur Complement Numerical Error Contradicts Positive-Definiteness Claim
**File:** `articles/tangent-hyperplane-contraction/chapters/ch08_applications.qmd:~211`
**Severity:** MAJOR

The chapter presents a Schur complement matrix claimed to be positive definite, but the (3,3) entry is **negative**. A positive-definite matrix must have all positive diagonal entries. This either indicates a sign error in the derivation or the positive-definiteness claim is incorrect.

**Recommendation:** Verify the Schur complement calculation and correct the sign error or the claim.

---

#### ISSUE-TC45: Contraction Rate Off by Factor of 2
**File:** `articles/tangent-hyperplane-contraction/chapters/ch04_contraction.qmd:~412-418`
**Severity:** MAJOR

The contraction rate derivation contains a factor-of-2 error. The symmetric part of the Jacobian gives the contraction rate as `λ_max(sym(J))`, but the text appears to drop or double a factor of 2 in the relationship between the matrix measure and the contraction rate. This propagates to subsequent stability conclusions.

**Recommendation:** Re-derive the contraction rate carefully, tracking factors of 2 from the symmetric part of the Jacobian to the exponential convergence bound.

---

#### ISSUE-TC46: Pendulum Gravity Sign Ambiguity
**File:** `articles/tangent-hyperplane-contraction/chapters/ch05_optimal_control.qmd:~572`
**Severity:** MAJOR

The pendulum example has an ambiguous gravity sign convention. The equation uses `+g sin(θ)` which corresponds to measuring θ from the **upright** equilibrium. However, the context discusses swinging from the **downward** equilibrium, where the correct sign is `-g sin(θ)`. This sign convention mismatch affects the linearization, the LQR design, and the claimed stability properties.

**Recommendation:** State the angle convention explicitly and verify all signs are consistent with the chosen convention.

---

#### ISSUE-TC47: LQR Robustness Proof Is Tautological
**File:** `articles/tangent-hyperplane-contraction/chapters/ch06_duality.qmd:~128-142`
**Severity:** MAJOR

The "proof" of LQR robustness margins (infinite gain margin, 60° phase margin) simply states the well-known result without derivation. It claims to prove it from the return-difference inequality but then just asserts the conclusion. The return-difference inequality `(I + L)^H R^{-1} (I + L) ≥ R^{-1}` is stated but the steps connecting it to specific gain/phase margins are omitted.

**Recommendation:** Either provide the complete derivation from the return-difference inequality to the gain/phase margin bounds, or cite a textbook reference (e.g., Anderson & Moore, Optimal Control) and label the result as "well-known."

---

#### ISSUE-TC48: LTI Controllability Rank Test Applied to Time-Varying System
**File:** `articles/The_Geometry_of_Motion/quarto/03-local-optimal-control.qmd:55`
**Severity:** MODERATE

The chapter applies the LTI controllability rank condition `rank[B, AB, A²B, ..., Aⁿ⁻¹B] = n` to a linearized system that is explicitly time-varying (the linearization point changes along a trajectory). The correct test for time-varying systems is the controllability Gramian, not the constant-matrix rank test. This is a common pedagogical error but incorrect in this context.

**Recommendation:** Either note that the rank test applies at a frozen operating point (frozen-time approximation) or use the controllability Gramian for the time-varying case.

---

## Part II: UI/UX & Website Implementation

### CRITICAL Issues

#### ISSUE-UX01: AI Agent Internal Monologue Leaked into Production HTML
**File:** `resources-videos.qmd:439-445`
**Severity:** CRITICAL

An AI editing agent's internal thought process is visible as an HTML comment in the production source:
```html
<!-- Using a generic section or appending to others? The user wanted specific updates.
     I will update the A. Sala and Biomechanics channels in place or here if I removed them.
     Wait, I am replacing lines 342-395 (Physics Demos + Fluid Dynamics).
     I need to go upwards to fix the Channels which were earlier in the file (lines 195 and 322).
     ...
-->
```
This is shipped to users in the HTML source and is unprofessional. While it's in a comment and not visible on screen, it's visible via "View Source" and indicates a quality control gap.

**Recommendation:** Remove all AI agent internal comments. Audit all QMD/HTML files for similar leaked content.

---

#### ISSUE-UX02: Font Variable Mismatch in custom.scss
**File:** `custom.scss:24`
**Severity:** CRITICAL (affects entire site typography)

```scss
$font-family-sans-serif: "Playfair Display", serif;
```

"Playfair Display" is a **serif** font being assigned to the `$font-family-sans-serif` Bootstrap variable. This means:
1. The variable name is semantically incorrect (sans-serif variable holds a serif font)
2. If the font fails to load, the fallback is `serif` which is correct for the font but wrong for the variable name
3. This makes the CSS architecture misleading for future contributors

**Recommendation:** Either rename the variable usage to accurately reflect the font choice, or switch to an actual sans-serif font for this variable.

---

### MAJOR Issues

#### ISSUE-UX03: Massive CSS Codebase with Significant Duplication
**Files:** `styles.css` (2,655 lines), `css/` (19 files, ~4,700 lines), `custom.scss`
**Severity:** MAJOR

Total CSS is ~7,400 lines across multiple files. Key concerns:
1. `styles.css` (2,655 lines) is a single monolithic file that imports 3 more CSS files
2. The `css/` directory has 19 additional CSS files
3. Not all CSS files in `css/` are referenced from `_quarto.yml` or `styles.css`
4. Only `css/startup-launcher.css`, `css/search-metrics.css`, and `styles.css` are explicitly included in `_quarto.yml`
5. Dead CSS rules likely exist given the size

**Recommendation:** Audit CSS for dead rules using coverage tools. Consolidate into a clear architecture with a single entry point.

---

#### ISSUE-UX04: Inconsistent Page Layouts
**Severity:** MAJOR

Some pages use Quarto's native layouts while others use raw HTML blocks with custom CSS. This creates visual inconsistency:
1. The homepage (`index.qmd`) is entirely raw HTML in a `{=html}` block
2. Theory articles use Quarto's native markdown rendering
3. Resource pages use raw HTML with accordion components
4. The visual styles (spacing, typography, card designs) differ between these approaches

**Recommendation:** Standardize on one approach per page type. Define 3-4 page templates (landing, article, resource list, tool) and apply consistently.

---

#### ISSUE-UX05: Missing Dark Mode Support
**Severity:** MAJOR

The `custom.scss` defines a colorblind-safe palette (Okabe-Ito), which is excellent. However:
1. No dark mode is implemented despite the site being content-heavy (reading fatigue)
2. CSS custom properties in `styles.css` define light theme values but no `prefers-color-scheme: dark` media query
3. For a technical audience that reads long articles, dark mode is expected

**Recommendation:** Implement dark mode using CSS custom properties and `prefers-color-scheme` media query, with a manual toggle.

---

#### ISSUE-UX06: Navigation Becomes Overwhelming at Scale
**Severity:** MAJOR

The navbar has 7 top-level items, several with dropdowns. The left sidebar on the homepage adds more links. As the site grows:
1. The Books dropdown will grow with each new volume
2. The Resources dropdown already has 8 items
3. The Articles dropdown mixes different content types (manifesto, series, reviews)
4. The Repositories dropdown only has a single external GitHub link, wasting nav space

**Recommendation:** Restructure navigation around user tasks: "Learn" (theory + articles), "Explore" (resources + bibliography), "Build" (models + tools + repositories), "Connect" (about + contact).

---

### MODERATE Issues

#### ISSUE-UX07: Homepage Emoji Icons Instead of Proper Icons
**File:** `index.qmd:152-166`
**Severity:** MODERATE

Quick-start cards use HTML entity emojis (&#128214;, &#128187;, etc.) as icons. These render inconsistently across platforms and look unprofessional.

**Recommendation:** Use SVG icons or an icon library (e.g., Bootstrap Icons which is already loaded via Quarto).

---

#### ISSUE-UX08: No Breadcrumb Navigation
**Severity:** MODERATE

Articles nested in subdirectories (e.g., `articles/Tangent Hyperplane Articles/Advanced/...`) have no breadcrumb navigation. Users can get lost in the content hierarchy.

**Recommendation:** Add breadcrumb navigation to all article pages.

---

#### ISSUE-UX09: Table of Contents Disabled Globally
**File:** `_quarto.yml:157`
**Severity:** MODERATE

`toc: false` is set globally in `_quarto.yml`. Individual articles override this, but long resource pages and some articles lack a table of contents. For 1000+ line articles, this is a usability problem.

**Recommendation:** Set `toc: true` globally and disable on specific pages that don't need it (homepage, contact).

---

#### ISSUE-UX10: Service Worker Caches Stale Content
**File:** `service-worker.js`
**Severity:** MODERATE

The service worker uses `CACHE_NAME = 'affinedrift-v2'` but there's no automated cache-busting. When content is updated, users may see stale content until the service worker is manually updated.

**Recommendation:** Implement content-hash-based cache keys or at minimum increment the version number as part of the build process.

---

#### ISSUE-UX11: Book Placeholder Images Throughout Resources
**Files:** `resources-books.qmd` (25+ instances)
**Severity:** MODERATE

Most book entries use `book_placeholder.svg` instead of actual cover images. This makes the page look incomplete.

**Recommendation:** Add actual book cover images or remove the image element for books without covers.

---

#### ISSUE-UX12: Mobile Menu Has Custom Implementation Over Quarto's
**Files:** `index.qmd:10-21`, `css/mobile.css`
**Severity:** MODERATE

The homepage implements a custom mobile menu toggle button with custom CSS, but Quarto already provides responsive navigation. This creates potential conflicts between the two systems.

**Recommendation:** Use Quarto's built-in responsive navigation consistently.

---

#### ISSUE-UX13: Custom Global Search Is Completely Non-Functional
**Files:** `src/js/global-search.js`, `css/search-metrics.css`
**Severity:** CRITICAL

The custom global search feature (Cmd+K shortcut, fuzzy matching, category filtering) is entirely dead code:
1. `src/js/global-search.js` is **never loaded** — not referenced in `_quarto.yml`, `site-head.html`, or `site-after-body.html`
2. The required data file `/data/search_index.json` **does not exist**
3. The CSS for the search modal (`css/search-metrics.css`) IS loaded by `_quarto.yml`, adding dead styles

The Quarto built-in search works, but the custom search with its advanced features is completely disconnected.

**Recommendation:** Either wire up the global search (load the JS, generate the search index) or remove all dead search code and CSS.

---

#### ISSUE-UX14: Undefined CSS Custom Properties Break Homepage Rendering
**Files:** `css/home.css`, `styles.css`
**Severity:** MAJOR

Six CSS custom properties are **used but never defined** in any `:root` declaration:
- `--border-light`, `--text-dark`, `--text-light`, `--legal-pad-yellow-border`, `--legal-pad-yellow-accent`, `--bg-dark`

Since CSS variables fail silently, this causes:
- Invisible sidebar borders (transparent fallback)
- Text rendering in inherited/default colors instead of intended palette
- Welcome header bottom border is invisible
- Tooltip backgrounds have no color

**Recommendation:** Add all missing CSS variable definitions to `:root` in `styles.css` or `css/base.css`.

---

#### ISSUE-UX15: script.js Preloaded on Every Page but Only Serves Legacy Browsers
**Files:** `_includes/site-head.html:48`, `_includes/site-after-body.html:11-22`
**Severity:** MAJOR

The module/nomodule pattern in `site-after-body.html` loads `js/main.js` for modern browsers and `script.js` as legacy fallback. However, `site-head.html` **preloads** `script.js` on every page (`<link rel="preload" href="/script.js" as="script">`), wasting ~60KB of bandwidth for a file that will never execute in any browser from the last 8 years. The service worker also precaches `script.js`.

**Recommendation:** Remove the preload hint. Only serve `script.js` to browsers that actually need it.

---

#### ISSUE-UX16: Splash Screen Has No noscript Fallback
**Files:** `js/startup-launcher.js`, `css/startup-launcher.css`
**Severity:** MAJOR

The startup launcher creates a full-screen overlay with `z-index: 10000` and sets `overflow: hidden` on both `<html>` and `<body>`. If JavaScript fails or is disabled, the splash **never hides** — permanently blocking all site content. There is no `<noscript>` fallback.

**Recommendation:** Add a `<noscript><style>.startup-overlay { display: none !important; }</style></noscript>` tag.

---

#### ISSUE-UX17: manifest.json Has Invalid Icon Size and 1.4MB Logo
**File:** `manifest.json:19`
**Severity:** MAJOR

The PWA manifest specifies `"sizes": "192x192 512x512"` but the actual image is 1563x1563px at **1.4MB** — far too large for a PWA icon (should be under 50KB). The sizes specification is also invalid; separate icon entries should be used for each size.

**Recommendation:** Generate properly sized (192x192, 512x512) optimized icons. Create separate manifest entries for each size.

---

#### ISSUE-UX18: Competing Color Systems in CSS
**Files:** `custom.scss:5-12`, `css/base.css`, `styles.css`
**Severity:** MODERATE

Two incompatible color palettes are defined:
- `custom.scss`: Okabe-Ito colorblind-safe palette (e.g., `$color-blue: #0072B2`)
- `css/base.css` / `styles.css`: "Modern Scientific Palette" (e.g., `--primary-blue: #0f4c75`)

The SCSS palette sets headings to `var(--color-blue)` (#0072B2) while `base.css` sets them to `var(--primary-blue)` (#0f4c75). The actual heading color depends on CSS load order.

**Recommendation:** Consolidate to a single palette. The Okabe-Ito system is the better choice for accessibility.

---

#### ISSUE-UX19: MathJax Triple-Typeset Causes Unnecessary Reflow
**File:** `_includes/mathjax-loader.html`
**Severity:** MODERATE

`MathJax.typeset()` is called three times: inside `startup.ready()`, inside `startup.promise.then()`, and on `DOMContentLoaded` with a 100ms delay. This causes unnecessary re-rendering and visible reflow on math-heavy pages.

**Recommendation:** Call `MathJax.typeset()` only once, after both MathJax and DOM content are ready.

---

#### ISSUE-UX20: Conflicting Responsive Breakpoints Across CSS Files
**Files:** `css/responsive.css`, `css/overrides.css`, `css/mobile.css`
**Severity:** MODERATE

The right sidebar is hidden at different breakpoints depending on which CSS rule wins:
- `css/responsive.css`: hidden at `< 992px`
- `css/overrides.css`: hidden at `< 1200px`
- `css/mobile.css`: `.home-toc` hidden at `<= 1200px`

Since only `styles.css` (the monolith) is actually loaded, the modular files' intent is unclear and behavior depends on which rules the monolith chose to include.

---

#### ISSUE-UX21: Search Box min-width Causes Horizontal Overflow on Mobile
**File:** `css/navigation.css:131-143`
**Severity:** MODERATE

`#quarto-header #quarto-search` has `min-width: 300px` and `flex-basis: 400px`. On screens narrower than ~500px, this causes the navbar to overflow horizontally.

**Recommendation:** Use `max-width: 100%` or clamp the search box width on small screens.

---

#### ISSUE-UX22: polyfill.io Script Loaded Unnecessarily
**File:** `_includes/mathjax-loader.html:64`
**Severity:** MODERATE

The page loads `polyfill.min.js` from cdnjs.cloudflare.com. The polyfill.io service had security concerns in 2024 (domain sale). Additionally, MathJax v3 handles its own polyfills internally, making this load unnecessary.

**Recommendation:** Remove the polyfill.io script tag.

---

## Part III: Maintainability & Architecture

### CRITICAL Issues

#### ISSUE-MA01: Triplicated Asset Directories (CSS and JS)
**Files:** `css/`, `src/css/`, `docs/css/` and `js/`, `src/js/`, `docs/js/`
**Severity:** CRITICAL

Three copies of CSS and JS files exist:
- **`css/`** (19 files): Appears to be the primary source
- **`src/css/`** (6 files): Identical copies of some files from `css/`
- **`docs/css/`** (6 files): Identical copies (output directory, copied by Quarto build)
- **`js/`** (13 files): Primary source
- **`src/js/`** (9 files): Some overlap with different content (has `modules/` subdirectory)
- **`docs/js/`** (13 files): Identical copies from `js/`

This means:
1. Changes to CSS/JS must be made in the correct directory or they'll be overwritten
2. `src/js/` has module versions that don't match `js/` (different architecture)
3. No build pipeline reconciles these directories

**Recommendation:** Designate `src/` as the single source of truth. Set up a build pipeline that copies from `src/` to the locations Quarto expects. Remove duplicate files from `css/` and `js/`.

---

#### ISSUE-MA02: 40 QMD Files at Repository Root
**Severity:** CRITICAL

The repository root contains 40 QMD files alongside config files, README, etc. This creates:
1. A cluttered root directory that's hard to navigate
2. Difficulty distinguishing content from configuration
3. No clear content hierarchy

Root-level QMD files include: `index.qmd`, `overview.qmd`, `about.qmd`, `contact.qmd`, `collaborate.qmd`, `bibliography.qmd`, `articles.qmd`, `drifter-manifesto.qmd`, `tangent-hyperplanes.qmd`, `research-reviews.qmd`, `book-reviews.qmd`, `daydreams-doodles.qmd`, `tools.qmd`, `models.qmd`, `repositories.qmd`, `resources-*.qmd` (8 files), `models-*.qmd` (7 files), `repositories-*.qmd` (5 files), `offline.html`

**Recommendation:** Move content pages into subdirectories: `pages/`, `resources/`, `models/`, `repositories/`. Update `_quarto.yml` render paths accordingly.

---

#### ISSUE-MA03: Multiple Overlapping Content Hierarchies
**Severity:** CRITICAL

Content is spread across at least 5 directories with unclear relationships:
1. **Root-level QMDs**: Main site pages
2. **`articles/`**: Core theory articles (primary content)
3. **`content/`**: Additional content with its own `README.md`
4. **`books/`**: Book-format versions of similar content
5. **`articles/tangent-hyperplane-contraction/`**: Textbook-format content
6. **`articles/The_Geometry_of_Motion/`**: Another textbook-format content
7. **`articles/Tangent Hyperplane Articles/`**: Yet another organization of tangent hyperplane content

The same theoretical material appears in multiple forms:
- Tangent hyperplanes: standalone articles, book chapters, textbook chapters, series articles, unified thesis
- Core theory: theory-part1-5, book volume content, Geometry of Motion chapters

**Recommendation:** Create a clear content architecture document. Designate one canonical version of each article and make others clearly derivative. Consider using Quarto's multi-format output instead of maintaining multiple versions.

---

### MAJOR Issues

#### ISSUE-MA04: No Build Pipeline or Asset Management
**Severity:** MAJOR

There is no build tool (webpack, esbuild, Vite) for:
1. CSS concatenation/minification
2. JS bundling/minification
3. Image optimization
4. Cache-busting hash generation
5. Dead code elimination

The site relies on Quarto's built-in rendering plus manual file management.

**Recommendation:** Add a minimal build pipeline. Even a simple npm script that concatenates and minifies CSS/JS would help. Consider Vite for its simplicity.

---

#### ISSUE-MA05: Spaces in Directory Names
**Files:** `articles/Tangent Hyperplane Articles/`, `articles/The_Geometry_of_Motion/`, `content/Drift Ratio Visualizations/`, etc.
**Severity:** MAJOR

Multiple directories use spaces in their names. This causes:
1. Quoting issues in scripts and CI/CD
2. URL encoding problems (%20 in URLs)
3. Difficulty with command-line tools
4. Git operations become error-prone

**Recommendation:** Rename all directories to use hyphens or underscores. Update all references.

---

#### ISSUE-MA06: `docs/` as Output Directory is Committed to Git
**Severity:** MAJOR

The entire `docs/` directory (Quarto's output) is committed to the repository. This includes:
- 159 HTML files
- Multiple copies of CSS/JS
- Bootstrap and Quarto library files
- Generated search index

This means every content change produces massive diffs. The `docs/` directory should either:
1. Be in `.gitignore` and built via CI/CD, or
2. Be deployed from a separate branch (e.g., `gh-pages`)

**Recommendation:** Move to CI/CD-based builds. Add `docs/` to `.gitignore`. Use GitHub Pages with GitHub Actions to build and deploy.

---

#### ISSUE-MA07: 18+ Configuration Files at Root
**Severity:** MAJOR

Root directory has: `_quarto.yml`, `package.json`, `package-lock.json`, `pyproject.toml`, `ruff.toml`, `.pre-commit-config.yaml`, `playwright.config.js`, `jest.config.js`, `.htmlvalidate.json`, `manifest.json`, `custom.scss`, `styles.css`, plus files in `config/` directory (8 JSON config files).

**Recommendation:** Consolidate where possible. Move tool configs to a `config/` directory. Use `pyproject.toml` for Python tool configs instead of separate files.

---

#### ISSUE-MA08: Stale Assessment/Report Files
**Files:** `docs/assessments/` (60+ files), `critiques/` (40+ files)
**Severity:** MAJOR

There are 60+ assessment files and 40+ critique files. Many are dated and may be stale:
- Assessment archive has reports from Jan-Feb 2026
- Multiple "Completist Reports" at different dates
- Status JSON files at root (`1007_status.json`, `1008_status.json`)

**Recommendation:** Archive old assessments. Remove stale status files. Create a clear retention policy for assessment documents.

---

#### ISSUE-MA09: No Content Validation Pipeline
**Severity:** MAJOR

Despite having Jest and Playwright tests, there is no:
1. Link checker for internal/external links
2. Math equation validator
3. Bibliography consistency checker
4. Spell checker
5. Content linting (consistent headings, frontmatter validation)

**Recommendation:** Add a pre-commit or CI check that validates links, frontmatter, and bibliography consistency.

---

### MODERATE Issues

#### ISSUE-MA10: Test Coverage Gaps
**Files:** `tests/` directory
**Severity:** MODERATE

Unit tests cover: bibliography, global search, metrics, notes workspace, script, utils
E2E tests cover: accessibility, articles, bibliography, homepage, navigation, offline, search, user journey

Missing test coverage:
- No tests for the service worker
- No tests for mobile menu behavior
- No visual regression tests
- No tests for print CSS
- E2E smoke test has only 20 lines

---

#### ISSUE-MA11: Python Code Not Integrated
**Files:** `src/affine_control/`, `src/tangent_models/`, `src/tools/`
**Severity:** MODERATE

Python source code exists in `src/` but:
1. `pyproject.toml` is minimal
2. No Python tests are defined in the test directories
3. The MATLAB tools referenced in articles are not available in the repository
4. The relationship between Python code and the website is unclear

---

#### ISSUE-MA12: Archive Directories Lack Cleanup Policy
**Files:** `archive/`, `content/archive/`, `articles/archive/`, `articles/calculation-framework-comparison/archive/`
**Severity:** MODERATE

Multiple archive directories contain old versions of articles and code. There's no cleanup policy or retention schedule.

---

#### ISSUE-MA13: Duplicate Data Files
**Files:** `data/`, `docs/data/`
**Severity:** MODERATE

`data/bibliography.json`, `data/bibliography.yaml`, `data/reading_paths.yaml` exist in both `data/` and `docs/data/`. The `docs/data/` copies are generated by the Quarto build but committed to git.

---

#### ISSUE-MA14: 56 CI/CD Workflow Files (10,400+ Lines of YAML)
**Files:** `.github/workflows/` (56 files)
**Severity:** CRITICAL

The repository has 56 GitHub Actions workflow files totaling over 10,400 lines of YAML. The "Jules" agent system defines 10+ specialized bot workflows with overlapping mandates:
- `Jules-Code-Quality-Reviewer.yml`, `Jules-Code-Quality-Fixer.yml`, `Jules-Assessment-AutoFix.yml`, and `Jules-Auto-Repair.yml` have overlapping responsibilities
- Each workflow needs updating when project structure changes
- Complex interactions between bots create maintenance burden and bot-loop risk

**Recommendation:** Audit and consolidate to ~15-20 workflows. Merge overlapping Jules agents. Core CI (`ci-standard.yml` + `deploy-website.yml`) is solid; the agent workflows need rationalization.

---

#### ISSUE-MA15: Root-Level Artifact Files Should Be Cleaned Up
**Files:** `1007_status.json`, `1008_status.json`, `pr_615_comments.json`, `pr_615_comments_api.json`, `pr_615_feedback.json`, `checks.json`, `split_vol2.py`, `AffineDrift_Adversarial_Review_2026-03-07.md`
**Severity:** MAJOR

Multiple debugging/status artifacts committed to the repository root:
- Issue status JSON snapshots (2 files)
- PR feedback JSON files (3 files, 154KB combined)
- Build output files
- One-off scripts
- Assessment files that belong in `docs/assessments/`

**Recommendation:** Delete or .gitignore artifact files. Move assessment docs to proper location.

---

#### ISSUE-MA16: script.js (1,740 lines) and styles.css (2,655 lines) Violate File Size Limits
**Files:** `script.js`, `styles.css`
**Severity:** MAJOR

Both files exceed the project's own 400-line file limit documented in AGENTS.md. `script.js` at 1,740 lines and `styles.css` at 2,655 lines are monolithic files that should be decomposed into the modular structures already present in `js/` and `css/`.

**Recommendation:** Decompose both files or establish them as generated output from the modular source files.

---

#### ISSUE-MA17: docs/ Serves Dual Purpose (Build Output + Manual Docs)
**Severity:** MAJOR

The `docs/` directory is both Quarto's HTML output AND contains manually maintained documentation:
- `docs/adr/` - Architecture Decision Records
- `docs/development/` - Development guides
- `docs/assessments/` - Quality assessments (60+ files)
- `docs/reference/` - Notation references

Running `quarto render` could conflict with these manually maintained files.

**Recommendation:** Move manually maintained documentation to a `documentation/` directory outside the Quarto output path.

---

#### ISSUE-MA18: LaTeX Build Artifacts Committed to Git
**Files:** `articles/The_Geometry_of_Motion/Volume_I/chapters/*.aux`, `articles/textbook/chapters/*.aux`
**Severity:** MODERATE

LaTeX compilation artifacts (`.aux`, `.out`, `.toc`, `.log` files) are committed to the repository.

**Recommendation:** Add LaTeX artifacts to `.gitignore`.

---

#### ISSUE-MA19: Deprecated articles/textbook/ Directory Still Present
**File:** `articles/textbook/README.md`
**Severity:** MODERATE

The `articles/textbook/` directory is self-described as deprecated in its README, superseded by `articles/The_Geometry_of_Motion/`. It should be deleted.

---

#### ISSUE-MA20: Pre-commit Config Python Version Mismatch
**File:** `.pre-commit-config.yaml`
**Severity:** MODERATE

Pre-commit config specifies Python 3.11 as default while the project targets Python 3.12 in `pyproject.toml`. This can cause tool version mismatches.

---

#### ISSUE-MA21: Duplicate Python Tool Configuration
**Files:** `mypy.ini`, `ruff.toml`, `pyproject.toml`
**Severity:** MODERATE

Both `mypy.ini` and `pyproject.toml` configure mypy. Both `ruff.toml` and `pyproject.toml` configure ruff. Additionally, both ruff-format and black are configured despite serving overlapping purposes.

**Recommendation:** Consolidate all Python tool config into `pyproject.toml`. Choose either ruff-format or black.

---

#### ISSUE-MA22: src/js/ Contains Divergent Files from js/ (Not Simple Duplicates)
**Files:** `src/js/bibliography.js`, `src/js/main.js`, `js/bibliography.js`, `js/main.js`
**Severity:** MAJOR

Unlike `src/css/` (which is byte-identical to `css/`), the `src/js/` directory has files that **differ** from `js/`:
- `src/js/bibliography.js`: 13,299 lines vs `js/bibliography.js`: 8,803 lines
- `src/js/main.js`: 1,204 lines vs `js/main.js`: 3,259 lines
- `src/js/global-search.js` and `src/js/seo-enhancements.js` have no counterpart in `js/`

It's unclear which directory is canonical. Changes to one are not reflected in the other, creating a maintenance trap.

**Recommendation:** Determine canonical source, merge differences, and eliminate the duplicate directory. Add a build step if transformation is needed.

---

## Part IV: Content Completeness & Quality

### CRITICAL Issue

#### ISSUE-CQ01: "Coming Soon" and Placeholder Content on Live Site
**Files:** `resources-papers.qmd:65`, multiple resource pages
**Severity:** CRITICAL

Active pages contain placeholder content:
- `resources-papers.qmd:65`: "Note: Detailed review of Carol Putnam's work on interaction forces and proximal-to-distal sequencing coming soon."
- `resources-books.qmd`: 25+ book entries using `book_placeholder.svg`
- `resources-researchers.qmd`: Multiple researcher entries with fallback placeholder images

**Recommendation:** Either complete the content or remove placeholder entries. "Coming soon" content reduces site credibility.

---

### MAJOR Issues

#### ISSUE-CQ02: Textbook Content Is Draft Quality
**Files:** `articles/tangent-hyperplane-contraction/textbook-main.qmd`
**Severity:** MAJOR

The textbook-main.qmd explicitly identifies itself as a draft:
- Line 3: `subtitle: "A Geometry-First Textbook Draft for High-Dimensional Nonlinear Control"`
- Line 25: References "This draft" multiple times
- Line 252: "This draft establishes the core architecture for a full textbook"

This draft content is published on the live site alongside polished articles, creating quality inconsistency.

**Recommendation:** Either clearly mark draft content with visual indicators (e.g., a banner) or move to a separate staging area.

---

#### ISSUE-CQ03: Inconsistent Article Metadata
**Severity:** MAJOR

Articles have inconsistent YAML frontmatter:
- Some have `author:`, `date:`, `abstract:`
- Some have none of these
- Citation format varies (some use Quarto's citation system, others use inline references)
- Date formats vary

**Recommendation:** Define a standard frontmatter template and apply to all articles.

---

#### ISSUE-CQ04: Cross-Referencing Between Articles Is Weak
**Severity:** MAJOR

Despite the content being deeply interconnected, articles rarely link to each other:
1. Theory-part2 introduces ZTCF but doesn't link to the existing critique
2. The sources-of-nonlinearity article addresses many criticisms in the critiques/ directory but doesn't reference them
3. Book chapters don't link to the corresponding standalone articles
4. No "See Also" or "Related Articles" sections

**Recommendation:** Add systematic cross-references using Quarto's cross-reference system. Add "Related Articles" sections to each article.

---

### MODERATE Issues

#### ISSUE-CQ05: Critiques Directory Not Surfaced on Website
**Files:** `critiques/` (40+ files)
**Severity:** MODERATE

The `critiques/` directory contains 40+ detailed critique files but these are:
1. Not rendered as QMD pages
2. Not linked from the articles they critique
3. Not accessible from the website navigation

**Recommendation:** Convert key critiques to QMD pages and link them from the relevant articles. The "Critic's Corner" page for the Tangent Hyperplane series shows this is already being done selectively.

---

#### ISSUE-CQ06: Multiple Versions of Same Article Without Version Control
**Files:** Various archive/ directories
**Severity:** MODERATE

Articles like `controllability-drift-ratio` and `secondary-axis-stability` have v1 versions in archive directories, but:
1. No changelog documenting what changed between versions
2. No indication on the current version that it's been revised
3. Readers finding old versions via search may get outdated information

---

#### ISSUE-CQ08: inverse-dynamics.qmd Has 8 Placeholder Figures and Truncated Text
**File:** `articles/inverse-dynamics.qmd`
**Severity:** CRITICAL

The article has:
- 8 figure placeholders (`[Figure: ...]`) where actual visualizations should be
- 1 table placeholder (`[Table]`)
- Truncated text at lines 552 and 564 (sentences cut off mid-word)
- Mixed unit systems (lbs and N used without conversion)

This article is published on the live site in an incomplete state.

**Recommendation:** Complete the figures, fix truncated text, and standardize units.

---

#### ISSUE-CQ09: Confusing "Parts" Numbering Across Series and Project
**Files:** `articles/theory-part3.qmd:397`, `articles/theory-part5.qmd:142, 156`
**Severity:** MAJOR

The theory series uses "Parts 1-5" for the article sequence. But the broader project also uses "Parts II and III" to refer to simulation and experimental phases. These two numbering systems overlap, creating confusion when theory-part3 references "Parts II and III of this project."

**Recommendation:** Use "Phase" for project stages and "Part" for article series.

---

#### ISSUE-CQ10: THC Textbook Chapters Are Skeletal (6 of 8 Under 35 Lines)
**Files:** `articles/tangent-hyperplane-contraction/chapters/ch01-ch08*.qmd`
**Severity:** MAJOR

The Tangent Hyperplane Contraction textbook has 8 chapter files, but 6 of them are under 35 lines of content. These chapters contain section headings and brief introductory paragraphs but no substantive mathematical development, no complete proofs, and no worked examples. This makes the "textbook" effectively an outline masquerading as a finished product.

Combined with ISSUE-TC43 (the Books page linking to these thin chapters with descriptions promising rich content), this creates a poor reader experience.

**Recommendation:** Either develop the chapters into full textbook content or clearly label them as outlines/drafts with a progress indicator showing completion percentage.

---

#### ISSUE-CQ11: Volume 0 (Geometry of Motion) Has Duplicate Chapter Files
**Files:** `articles/The_Geometry_of_Motion/Volume_I/chapters/`, `articles/The_Geometry_of_Motion/quarto/`
**Severity:** MODERATE

The Geometry of Motion project has two sets of chapter files:
1. `Volume_I/chapters/` — LaTeX-format chapters (`.tex` files with `.aux` artifacts)
2. `quarto/` — Quarto-format chapters (`.qmd` files)

These appear to be parallel versions of the same content in different formats, with inconsistent naming conventions (`ch01_foundations.tex` vs `01-foundations-of-nonlinear-dynamics.qmd`). It's unclear which is canonical.

**Recommendation:** Designate one format as canonical, derive the other automatically, or archive the deprecated version. Document which version is authoritative.

---

#### ISSUE-CQ12: Books Volume I Content Links Do Not Match Descriptions
**Files:** `books/tangent-space-methods.qmd`
**Severity:** MAJOR

Volume I "Tangent-Space Methods for Nonlinear Control" describes 8 chapters with detailed descriptions, but the `_quarto.yml` sidebar links all point to `books/tangent-space-methods.qmd#book1-chN` anchors. The actual chapter content at these anchors may not match the detailed descriptions, especially given that the THC textbook chapters they derive from are skeletal (ISSUE-CQ10).

**Recommendation:** Audit all 8 chapter anchor targets to ensure the content matches the descriptions. Consider linking to the richer GoM chapters instead if available.

---

#### ISSUE-CQ07: The Geometry of Motion and Tangent Hyperplane Contraction Textbooks Overlap
**Files:** `articles/The_Geometry_of_Motion/`, `articles/tangent-hyperplane-contraction/`
**Severity:** MODERATE

Two separate textbook-format content areas cover overlapping material:
- Both cover foundations of nonlinear dynamics
- Both discuss tangent space methods
- Both include optimal control chapters

It's unclear whether these are intended as separate books or if one supersedes the other.

**Recommendation:** Clarify the relationship between these two textbook projects. If they're separate books, add clear scope statements. If one is deprecated, archive it.

---

## Recommended GitHub Issues

The following issues should be created in the GitHub repository, organized by priority:

### Priority 1 (Critical - Address Immediately)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 1 | Remove leaked AI agent comments from resources-videos.qmd | `bug`, `content` | ISSUE-UX01 |
| 2 | Add scope-limitation caveats to core theory articles (Part 1-3) | `content`, `technical-accuracy` | ISSUE-TC01 |
| 3 | Standardize "Instantaneous Force-Acceleration Superposition" terminology | `content`, `technical-accuracy` | ISSUE-TC02 |
| 4 | Distinguish novel claims from established results across all articles | `content`, `documentation` | ISSUE-TC03 |
| 5 | Fix ZVCF definition error in inverse-dynamics-inference.qmd | `bug`, `technical-accuracy` | ISSUE-TC16 |
| 6 | Fix state vector ordering inconsistency across theory articles | `bug`, `technical-accuracy` | ISSUE-TC17 |
| 7 | Fix markdown `*` rendering as incorrect math operators in superposition.qmd | `bug`, `technical-accuracy` | ISSUE-TC18 |
| 8 | Fix serif font assigned to $font-family-sans-serif in custom.scss | `bug`, `ui` | ISSUE-UX02 |
| 9 | Consolidate triplicated CSS/JS directories (css/, src/css/, docs/css/) | `architecture`, `tech-debt` | ISSUE-MA01 |
| 10 | Move QMD content files out of repository root into subdirectories | `architecture`, `tech-debt` | ISSUE-MA02 |
| 11 | Define canonical content hierarchy to resolve overlapping directories | `architecture`, `documentation` | ISSUE-MA03 |
| 12 | Remove "coming soon" and placeholder content from live pages | `content`, `quality` | ISSUE-CQ01 |
| 13 | Add missing figures and fix truncated text in inverse-dynamics.qmd | `content`, `quality` | ISSUE-CQ08 |
| 14 | Remove unrevised AI draft text ("Wait, let me recalculate") from Hybrid Tangent Spaces | `bug`, `content` | ISSUE-TC31 |
| 15 | Remove or cite fabricated empirical claims in tangent hyperplane articles | `bug`, `technical-accuracy` | ISSUE-TC32 |
| 16 | Audit and consolidate 56 CI/CD workflow files | `architecture`, `ci-cd` | ISSUE-MA14 |
| 17 | Fix Books section cross-reference mismatch (descriptions don't match linked content) | `bug`, `content` | ISSUE-TC43 |
| 18 | Wire up or remove dead global search code (Cmd+K, search_index.json) | `bug`, `ui` | ISSUE-UX13 |

### Priority 2 (Major - Address Soon)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 16 | Add ZTCF identifiability discussion to theory-part2 | `content`, `technical-accuracy` | ISSUE-TC04 |
| 15 | Address dimensional inconsistency in DCR article | `content`, `technical-accuracy` | ISSUE-TC05 |
| 16 | Clarify accessibility vs. controllability in Lie bracket discussions | `content`, `technical-accuracy` | ISSUE-TC06 |
| 17 | Complete proofs in contraction-tangent unification article | `content`, `technical-accuracy` | ISSUE-TC07 |
| 18 | Formally define "Control Is Motion" paradigm | `content`, `documentation` | ISSUE-TC08 |
| 19 | Provide rigorous justification for F_total - F_ZTCF = F_ZVCF identity | `content`, `technical-accuracy` | ISSUE-TC19 |
| 20 | Replace "Mechanical Orthogonality" with correct terminology | `content`, `technical-accuracy` | ISSUE-TC20 |
| 21 | Add missing 3D pendulum examples to theory-part4 | `content` | ISSUE-TC21 |
| 22 | Provide rigorous proof for DCR monotonic growth invariance theorem | `content`, `technical-accuracy` | ISSUE-TC22 |
| 23 | Fix residual bound dimensional error and factor-of-10 mistake in Residual-Aware Control | `bug`, `technical-accuracy` | ISSUE-TC33 |
| 24 | Fix Riemann curvature tensor conflation with Hessian in Unified Thesis | `content`, `technical-accuracy` | ISSUE-TC34 |
| 25 | Fix residual bound using wrong quantity (Jacobian vs Hessian) in Unified Thesis | `content`, `technical-accuracy` | ISSUE-TC35 |
| 26 | Verify and correct double integrator ARE solution in Contraction article | `bug`, `technical-accuracy` | ISSUE-TC36 |
| 27 | Audit and reduce CSS codebase (~7,400 lines) | `tech-debt`, `ui` | ISSUE-UX03 |
| 24 | Standardize page layouts across site | `ui`, `ux` | ISSUE-UX04 |
| 25 | Implement dark mode | `enhancement`, `ui` | ISSUE-UX05 |
| 26 | Redesign navigation for scalability | `enhancement`, `ux` | ISSUE-UX06 |
| 27 | Add minimal build pipeline for assets | `architecture`, `enhancement` | ISSUE-MA04 |
| 28 | Rename directories with spaces to use hyphens | `tech-debt`, `architecture` | ISSUE-MA05 |
| 29 | Move docs/ to CI/CD build output (stop committing generated files) | `architecture`, `ci-cd` | ISSUE-MA06 |
| 30 | Consolidate root-level configuration files | `tech-debt` | ISSUE-MA07 |
| 31 | Archive stale assessment and status files | `tech-debt` | ISSUE-MA08 |
| 32 | Add content validation pipeline (link checker, frontmatter lint) | `ci-cd`, `quality` | ISSUE-MA09 |
| 33 | Mark draft textbook content with visual indicators | `content`, `ux` | ISSUE-CQ02 |
| 34 | Standardize article frontmatter (author, date, abstract, citations) | `content`, `quality` | ISSUE-CQ03 |
| 35 | Add systematic cross-references between related articles | `content`, `ux` | ISSUE-CQ04 |
| 36 | Clean up root-level artifact files (status JSONs, PR feedback, etc.) | `tech-debt` | ISSUE-MA15 |
| 37 | Decompose script.js (1740 lines) and styles.css (2655 lines) | `tech-debt`, `architecture` | ISSUE-MA16 |
| 38 | Separate docs/ into build output and manual documentation directories | `architecture` | ISSUE-MA17 |
| 39 | Fix Schur complement sign error contradicting positive-definiteness claim | `bug`, `technical-accuracy` | ISSUE-TC44 |
| 40 | Fix contraction rate factor-of-2 error in ch04 | `bug`, `technical-accuracy` | ISSUE-TC45 |
| 41 | Fix pendulum gravity sign ambiguity in ch05 | `bug`, `technical-accuracy` | ISSUE-TC46 |
| 42 | Complete LQR robustness proof or cite source in ch06 | `content`, `technical-accuracy` | ISSUE-TC47 |
| 43 | Develop skeletal THC textbook chapters into substantive content | `content`, `quality` | ISSUE-CQ10 |
| 44 | Audit Books Volume I chapter anchors to match descriptions | `content`, `quality` | ISSUE-CQ12 |
| 45 | Define missing CSS custom properties (--border-light, --text-dark, etc.) | `bug`, `ui` | ISSUE-UX14 |
| 46 | Remove legacy script.js preload hint from site-head.html | `performance`, `tech-debt` | ISSUE-UX15 |
| 47 | Add noscript fallback for splash screen overlay | `bug`, `accessibility` | ISSUE-UX16 |
| 48 | Fix manifest.json invalid icon sizes and 1.4MB logo | `bug`, `performance` | ISSUE-UX17 |
| 49 | Resolve divergent src/js/ vs js/ files (bibliography.js, main.js) | `tech-debt`, `architecture` | ISSUE-MA22 |

### Priority 3 (Moderate - Address When Convenient)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 36 | Revise intermediate axis theorem application in secondary-axis-stability | `content`, `technical-accuracy` | ISSUE-TC09 |
| 37 | Reframe strokes-gained critique as limitations analysis | `content` | ISSUE-TC10 |
| 38 | Add DOF limitation discussion to wrist-universal-joint article | `content` | ISSUE-TC11 |
| 39 | Add energy balance to double pendulum wrench analysis | `content` | ISSUE-TC12 |
| 40 | Formalize Intentional Constraint Collapse with DCR thresholds | `content`, `technical-accuracy` | ISSUE-TC13 |
| 41 | Complete proofs in textbook chapters | `content` | ISSUE-TC14 |
| 42 | Standardize bibliography cross-references across all articles | `content`, `quality` | ISSUE-TC15 |
| 43 | Add citations for unsupported quantitative claims in DCR article | `content` | ISSUE-TC23 |
| 44 | Standardize block matrix naming across articles | `content` | ISSUE-TC24 |
| 45 | Resolve "Causal Orthogonality" vs "Mechanical Orthogonality" inconsistency | `content` | ISSUE-TC25 |
| 46 | Fix broken Quarto cross-reference syntax in affine-nature-golf-swing | `bug` | ISSUE-TC26 |
| 47 | Replace placeholder figures/tables and fix truncated text in inverse-dynamics | `content` | ISSUE-TC27 |
| 48 | Clean up self-contradicting air resistance calculation | `content` | ISSUE-TC28 |
| 49 | Add linearization caveat to Gramian reachable ellipsoid in DCR | `content` | ISSUE-TC29 |
| 50 | Fix equation numbering conflicts in superposition article | `content` | ISSUE-TC30 |
| 51 | Resolve "exact" vs "excellent approximation" language across tangent hyperplane series | `content` | ISSUE-TC37 |
| 52 | Qualify Integral Accumulation Principle to require fixed trajectory | `content`, `technical-accuracy` | ISSUE-TC38 |
| 53 | Justify or correct stochastic contraction metric equation | `content`, `technical-accuracy` | ISSUE-TC39 |
| 54 | Fix Frechet derivative definition error in Critics Corner | `bug` | ISSUE-TC40 |
| 55 | Mark Unified Thesis Part III as draft/incomplete with visual indicator | `content` | ISSUE-TC41 |
| 56 | Fix .md to .qmd file extension mismatches in cross-references | `bug` | ISSUE-TC42 |
| 51 | Replace emoji icons with SVG/icon library on homepage | `ui` | ISSUE-UX07 |
| 52 | Add breadcrumb navigation to nested articles | `ux`, `enhancement` | ISSUE-UX08 |
| 53 | Enable table of contents globally, disable per-page as needed | `ux` | ISSUE-UX09 |
| 54 | Implement content-hash cache busting for service worker | `enhancement` | ISSUE-UX10 |
| 55 | Add actual book cover images to resources-books | `content` | ISSUE-UX11 |
| 56 | Remove custom mobile menu in favor of Quarto's responsive nav | `tech-debt`, `ui` | ISSUE-UX12 |
| 57 | Improve test coverage (service worker, mobile, visual regression) | `testing` | ISSUE-MA10 |
| 58 | Integrate Python tools with website or document relationship | `documentation` | ISSUE-MA11 |
| 59 | Define archive/retention policy for old assessments and versions | `documentation`, `tech-debt` | ISSUE-MA12 |
| 60 | Remove duplicate data files from docs/data/ | `tech-debt` | ISSUE-MA13 |
| 61 | Surface critiques directory on website with links from articles | `content`, `ux` | ISSUE-CQ05 |
| 62 | Add version history/changelog to revised articles | `documentation` | ISSUE-CQ06 |
| 63 | Clarify relationship between overlapping textbook projects | `documentation`, `content` | ISSUE-CQ07 |
| 64 | Add LaTeX build artifacts to .gitignore | `tech-debt` | ISSUE-MA18 |
| 65 | Delete deprecated articles/textbook/ directory | `tech-debt` | ISSUE-MA19 |
| 66 | Fix Python version mismatch in pre-commit config (3.11 vs 3.12) | `bug` | ISSUE-MA20 |
| 67 | Consolidate duplicate Python tool config (mypy.ini, ruff.toml into pyproject.toml) | `tech-debt` | ISSUE-MA21 |
| 68 | Fix LTI controllability rank test misapplied to time-varying system | `content`, `technical-accuracy` | ISSUE-TC48 |
| 69 | Resolve Volume 0 duplicate chapter files (LaTeX vs Quarto) | `tech-debt`, `content` | ISSUE-CQ11 |
| 70 | Consolidate competing color systems (Okabe-Ito vs Modern Scientific) | `ui`, `tech-debt` | ISSUE-UX18 |
| 71 | Fix MathJax triple-typeset causing unnecessary reflow | `performance`, `bug` | ISSUE-UX19 |
| 72 | Resolve conflicting responsive breakpoints across CSS files | `bug`, `ui` | ISSUE-UX20 |
| 73 | Fix search box min-width causing mobile horizontal overflow | `bug`, `ui` | ISSUE-UX21 |
| 74 | Remove unnecessary polyfill.io script (security concern) | `security`, `tech-debt` | ISSUE-UX22 |

---

## Summary Statistics

| Category | Critical | Major | Moderate | Total |
|----------|----------|-------|----------|-------|
| Technical Claims | 8 | 17 | 23 | 48 |
| UI/UX | 3 | 8 | 11 | 22 |
| Maintainability | 4 | 9 | 9 | 22 |
| Content Quality | 2 | 6 | 4 | 12 |
| **Total** | **17** | **40** | **47** | **104** |

---

## Positive Observations

While this review focuses on issues, the following strengths should be noted:

1. **Colorblind-safe palette**: The Okabe-Ito palette in `custom.scss` shows excellent accessibility awareness
2. **Self-critique culture**: The `critiques/` directory with 40+ critique files demonstrates intellectual honesty
3. **Mathematical depth**: Articles like `sources-of-nonlinearity.qmd` show rigorous, thorough treatment
4. **Comprehensive bibliography**: 120 entries in a structured JSON format with consistent fields
5. **Testing infrastructure**: Jest + Playwright setup with 2,257 lines of test code
6. **AI transparency**: The homepage openly discusses AI-assisted content creation
7. **Focus visibility**: CSS implements `:focus-visible` for keyboard accessibility
8. **Service worker**: Offline support is implemented (though needs cache-busting improvements)
9. **Pre-commit hooks**: `.pre-commit-config.yaml` exists for code quality enforcement
10. **Multiple reading paths**: The `reading_paths.yaml` system shows thoughtful UX consideration

---

*This assessment was generated on March 12, 2026. Issues should be re-evaluated after major changes to the codebase.*
