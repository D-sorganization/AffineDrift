# Rigor Guide

The standard AffineDrift content must meet. This is a contract, not a style preference.

Every rule below exists because the 2026-07-31 full-corpus review found it broken somewhere —
each one has a real example behind it.

## 1. Every number must be reproducible

**Rule:** No number appears in the text unless it can be regenerated from checked-in code, or is
cited to a source, or is explicitly labelled a modelling assumption.

**Why:** The review found at least eleven worked examples reporting results their own stated
models cannot produce. A "verified stable" closed loop with spectral radius 1.043. A mass matrix
with negative determinant. A damping ratio of 0.38 where the stated parameters give 1.41 —
inverting the narrative built on it.

**In practice:** Generate tables from scripts and `\input`/include the output. Never hand-type a
row. If you change a parameter, regenerate every dependent number rather than editing the ones
you notice.

## 2. Never display output that code did not produce

**Rule:** If the page shows solver output, a spectrum, or a printed result, an executed cell
produced it.

**Why:** The tangent corpus ships CVXPY output for a provably infeasible SDP, and prints
`Contracting: True` for code returning `+7.0`. This is the most damaging thing a technical site
can contain — every other error reads as a mistake; this reads as a result that was never run.

**In practice:** Quarto `{python}` cells, not pasted blocks. An honest negative result ("this SDP
is infeasible, and here is why that is interesting") is worth more than a fabricated positive one.

## 3. State theorem hypotheses

**Rule:** Every theorem carries the conditions under which it holds.

**Why:** `Ṁ − 2C` skew-symmetry was stated without the Christoffel hypothesis — and the same
chapter's own double pendulum violates it. A hierarchical-contraction theorem was stated with no
hypotheses and is refuted by a two-line counterexample. Classical LQR gain and phase margins were
asserted for a finite-horizon time-varying system.

**In practice:** Contraction claims state the metric and the region. Controllability claims
distinguish accessibility (Lie algebra rank condition) from controllability — for systems with
drift these are different, and conflating them is the most commonly botched point in geometric
control. Optimality conditions state whether the Hamiltonian is minimized or maximized under the
sign convention in use.

## 4. Distinguish instantaneous from trajectory-level claims

**Rule:** The affine decomposition is a statement about **accelerations at a frozen state**. It
is not a superposition principle for trajectories.

**Why:** This is the project's central claim and its most likely failure mode. `q̈ = M(q)⁻¹(τ −
C(q,q̇)q̇ − g(q))` is affine in `τ` at fixed state; it is **not** linear in state, and
trajectories do **not** superpose.

**In practice:** `superposition.qmd` does this correctly and is the model to follow. Never write
"Total motion = ZTCF + Control correction". Never instruct a reader to verify
`τ_total − τ_ZTCF = τ_ZVCF` — that identity is false, the difference is the **input** term, and
it has now been reintroduced twice after being fixed.

## 5. Cite what you actually read

**Rule:** A citation supports the specific claim it is attached to.

**Why:** Kawato 1987 — the _inverse_-model paper — was cited for the forward model. Kamin 1969 on
classical conditioning was cited for visuomotor adaptation. A Millard key pointed at a paper about
birds. Khalil's _Nonlinear Systems_ was given Isidori's title three times.

**In practice:** Never write a description of the source you wish existed inside `\cite{}` — the
review found eight of these, and they render as `[?]` while leaving the claim unsupported. Either
source the claim, derive it, or label it an assumption.

## 6. Use one convention and say which

**Rule:** Conventions are declared once, in `NOTATION.md`, and followed everywhere.

**Why:** Spatial-vector ordering forks between volumes — Volume 0 declares angular-first, Volume I
uses linear-first, and Volume I chapter 9 uses both, 560 lines apart. DCR means five different
things. ZTCF is expanded five ways.

**In practice:** Twists are angular-first `(ω, v)`, matching Featherstone, Lynch & Park, and
Pinocchio. Quaternions are Hamilton, scalar-first — the one convention the review found honoured
everywhere with zero violations. If you need a different quantity, **give it a different name**
rather than overloading an existing one.

## 7. Say when the model breaks

**Rule:** State the assumptions and their failure modes.

**Why:** Induced-acceleration results are decomposition-scheme and constraint-model dependent —
any causal attribution ("the hips contribute X%") is meaningless without the scheme. Closed-chain
inverse dynamics is **indeterminate**; it cannot be solved from kinematics alone. Inverse dynamics
yields net joint moments, never individual muscle forces.

**In practice:** Volume III chapter 6 does this well and repeatedly — follow it.

## 8. Match claims to evidence

**Rule:** Distinguish established results, contested results, and this project's own hypotheses.

**Why:** The HKB coordination result was stated backwards in text, figure, caption and exercise.
A `PLACEHOLDER … should not be trusted` number was promoted into another volume as a finding.
Fascia claims ran ahead of their evidence in a chapter whose purpose was separating science from
mysticism — with one citation in 526 lines.

**In practice:** The provenance callouts on `index.qmd` and `drifter-manifesto.qmd` are the model:
they name what is established literature and what is original AffineDrift synthesis. The affine
decomposition is this project's contribution, not textbook consensus, and should read that way.

## 9. Both trees, always

**Rule:** A content fix lands in the `.tex` and the `.qmd`, or states why it is tree-specific.

**Why:** See [`README.md`](README.md). This is the most common defect in the repository's history.

## 10. Leave nothing contradicting itself

**Rule:** After a correction, sweep the whole file and its siblings.

**Why:** The review repeatedly found a corrected statement sitting beside the wrong one it
replaced — in one case eighteen lines apart, in another within the Limitations and Critics
sections a sceptical reader trusts most. A reader who finds both cannot tell which is current,
and the correction's presence proves the project knows the other is wrong.

## Checklist before opening a content PR

- [ ] Every number is generated, cited, or labelled an assumption
- [ ] Every displayed output came from executed code
- [ ] Every theorem states its hypotheses
- [ ] Instantaneous and trajectory-level claims are distinguished
- [ ] Every citation resolves and supports its claim
- [ ] Conventions match `NOTATION.md`; parameters match `PARAMETERS.md`
- [ ] Assumptions and failure modes are stated
- [ ] Claim strength matches evidence strength
- [ ] Applied to both the LaTeX and Quarto trees
- [ ] No contradicting statement left elsewhere in the file
- [ ] The book still compiles
