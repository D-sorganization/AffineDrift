# Terminology Decision Record — ZTCF, ZVCF, DCR, Drift, Control

Status: **OPEN — no decisions ratified yet.** Tracked by the terminology epic.

This document is the working record for resolving definitional conflicts in
AffineDrift's core vocabulary. It is written to be read cold, without prior
context, by a human or an agent reviewing the approach.

## How to use this document

Every claim below is a verbatim quote with a `file:line` citation. **No
definition here was authored by the person or agent who compiled it.** Where two
sources disagree, both are quoted and the disagreement is left open.

Each decision has: the conflict, the options, what each option costs, what
depends on it, and a `DECISION:` line that currently reads `UNRESOLVED`. Fill in
the `DECISION:` lines, then the remediation work becomes mechanical.

Do not "harmonize" a conflict by picking whichever wording reads better. Several
of these are questions about what the physics is supposed to mean, and the wrong
answer silently changes a published scientific claim.

---

## 0. Root cause

**`NOTATION.md` contains no entry for `ZTCF`, `ZVCF`, `f(x)`, `G(x)`, `u`, or
"drift".**

Its symbol glossary (lines 309–357) covers lowercase and uppercase Greek only.
There is no Latin-symbol table, so `f`, `G`, `u`, `x` are never entered.
`f_acc` and `G_acc` appear exactly once, inside the DCR formula at line 142,
where they are *used but never defined*.

Three separate places nonetheless name it the authority:

- `NOTATION.md:5` — "the authoritative reference for all mathematical symbols,
  notation conventions, and sign conventions used across Physics of Golf,
  Geometry of Motion, and all articles."
- `scripts/check_terminology.py:9` — "`NOTATION.md` is the single source of truth."
- `SPEC.md` F59 — names it as the acronym gate's source of truth.

The project's signature acronym is therefore enforced only *negatively*, by a
hardcoded blocklist of wrong expansions inside a linter. Its correct expansion
lives in that script's `fix` field and in article prose — nowhere authoritative.

**This is why a sixth wrong ZTCF expansion ("zero transfer of control and
force") survived from the textbook's first commit in March 2026 until August
2026, in both trees, through a dedicated acronym-unification pass (#3526).** An
enumerated blocklist can only catch errors someone already noticed.

---

## 1. Measured scale

Counts over `articles/`, `books/`, `pages/`, `resources/`, `models/`,
`repositories/`, `index.qmd`, both `.qmd` and `.tex`, fenced code excluded.
Regenerate with the case-inventory script referenced by the epic.

| Item | Count | Files |
| --- | ---: | ---: |
| `ZTCF`, **bare** (no qualifier) | **1,156** | 79 |
| `ZTCF`, qualified | 44 | 16 |
| `ZVCF` | 385 | 22 |
| "Drift–Control Ratio" (canonical) | 76 | — |
| "Drift-to-Control Ratio" | 38 | — |
| "Drift coefficient ratio" | 2 | 2 |
| `G(x)`/`G(q)` | 254 | 36 |
| `g(x)`/`g(q)` | 247 | 35 |
| Files using **both** `G` and `g` forms | — | 19 |
| No-muscle / purely-passive claims near ZTCF | 27 | — |
| Trajectory-superposition identity | **0** | — |

**96% of ZTCF uses are bare**, against a canonical rule requiring a qualifier on
first use.

---

## 2. Decision 1 — ZTCF's four-object rule 🔑 ROOT DECISION

**Four of the six remaining conflicts dissolve once this is settled.**

### What is already decided and enforced

This is not an open question about meaning. The project chose a scheme and
pinned it in CI:

- `tests/test_proximal_distal_article_contract.py:35` —
  `test_glossary_requires_qualified_ztcf_and_rejects_muscle_inference`
- It asserts all four object names, plus `"qualifier is required on first use"`,
  plus `"This is not a no-muscle simulation"`.

The canonical glossary:

> `articles/zero-torque-counterfactual.qmd:77` — "This article is the
> **canonical reference** for \"ZTCF\" across the AffineDrift site. … Four
> related objects are in circulation; the qualifier is required on first use:"
>
> `:79` — "**Pointwise ZTCF sample** — $f(x(t))$, the zero-applied-control
> evaluation at one achieved state. It is an instantaneous vector, not a
> forecast. \"Pointwise drift vector\" is the preferred generic name"
>
> `:81` — "**Stitched pointwise ZTCF trace** — the time-indexed collection
> $\{f(x(t_k))\}$ … Its samples do not form a dynamically integrated trajectory"
>
> `:83` — "**Forward ZTCF trajectory** — $x^{\mathrm{ZTCF}}(t; x_0, t_0)$"
>
> `:87` — "**Branched ZTCF trajectory** — the forward ZTCF trajectory (3)
> initialized from the **achieved** swing state"
>
> `:89` — "The **drift vector field** $f:\mathcal{X}\rightarrow T\mathcal{X}$ …
> is not a trajectory or a dataset."

### The conflict

**(a) The rule is 96% unenforced** — 1,156 bare uses against 44 qualified.

**(b) Two prominent articles describe a different, three-object scheme that
inverts the central point:**

> `articles/theory-part2.qmd:137` — "The full glossary (Trajectory ZTCF, drift
> vector $f(x)$ which is **not** ZTCF, and Branched ZTCF)"
>
> `articles/affine-nature-golf-swing.qmd:766` — "The **three** distinct objects
> informally called \"ZTCF\" on this site (Trajectory ZTCF, drift vector $f(x)$
> — **not** ZTCF, and Branched ZTCF)"

Both name a "**Trajectory ZTCF**" that is defined nowhere in the repo. Both say
`f(x)` is not a ZTCF; the canonical glossary calls it "Pointwise ZTCF sample".

**(c) The canonical article contradicts itself on scope:**

> `:79` — the pointwise object *is* a ZTCF
>
> `:100` — "**That integrated trajectory, not the instantaneous decomposition,
> is the Zero-Torque Counterfactual.**"

**(d) A third article defines bare ZTCF as strictly instantaneous, no qualifier:**

> `articles/calculation-framework-comparison/multibody-drift-control-v3.qmd:59`
> — "We call this the **Zero Torque Counterfactual**, or **ZTCF**: what the
> system would do, at this instant, with zero input. It is a snapshot — a
> photograph of the physics at one moment — not a prediction of the future."
>
> `:323` — "**It is time-local, not a trajectory prediction.**"

### Options

| Option | Meaning | Cost | Test impact |
| --- | --- | --- | --- |
| **1A** | Keep four objects. Reconcile the two stragglers; define or delete "Trajectory ZTCF" | 2 files | none |
| **1B** | 1A, plus actually enforce the qualifier at first use per page | 1A + ~79 first-use sites | none |
| **1C** | Narrow: ZTCF = trajectory only; `f(x)` is only ever "pointwise drift vector" | glossary rewrite + reconcile | **changes a pinned test** |

**Dependency note:** do not do 1B before settling whether 1C is wanted.
Qualifying ~1,150 sites and then narrowing the scheme wastes the work.

**Argument for 1A:** cheapest, touches no test, preserves a deliberate decision.

**Argument for 1C:** makes `theory-part2.qmd:303`'s contrast exactly true —
"the ZTCF is a *trajectory*-level counterfactual … the **ZVCF is an
*instantaneous* snapshot**" — and matches `:100` and both stragglers. Under 1A
that contrast is false, because a "Pointwise ZTCF sample" is also instantaneous.

`DECISION: UNRESOLVED`

---

## 3. Decision 2 — What is inside the drift? ⚠️ HAS A MATHEMATICAL CONSEQUENCE

### The conflict

**Inventory A — includes passive joint impedance and shaft stiffness/damping:**

> `articles/theory-part1.qmd:376` — "$\tau_{\text{pas}}(q, \dot{q})$ to model the
> **passive joint impedance** (ligament stiffness, joint friction, and intrinsic
> muscle viscoelasticity)"
>
> `:382` — "**Frozen Strategy** assumption: we define the \"Drift\" $f(x)$ as the
> dynamics of the system with the golfer's impedance *fixed* at its operational
> level, but with the *net driving torque* removed ($u=0$). This distinguishes
> the **Effective Plant** … from a \"flaccid\" ragdoll"
>
> `articles/theory-part2.qmd:82-88` — "Physically, this includes:" followed by a
> five-item list: "inertia of all rigid segments," / "Coriolis and centrifugal
> forces," / "gravitational torques," / "passive joint contributions
> **(if modeled)**," / "elastic and damping forces from shaft deformation."

**Note the qualifier.** `theory-part2` writes "passive joint contributions **(if
modeled)**" — it is conditional on the model, not a commitment that passive
impedance is always in the drift. It therefore sits closer to the middle of this
conflict than to Inventory A, and any ratified wording should say whether the
inclusion is unconditional or model-dependent. Shaft elasticity and damping in
that same list carry no such qualifier.

**Inventory B — Coriolis and gravity only:**

> `articles/The_Physics_of_Golf/quarto/ch05_affine_structure.qmd:83` —
> "$\bm{f}(\bm{x}) = [\dot{\bm{q}};\ \bm{M}(\bm{q})^{-1}[-\bm{C}\dot{\bm{q}} -
> \bm{g}(\bm{q})]]$"
>
> `articles/controllability-drift-ratio.qmd:208`, `GoM ch07_counterfactuals.qmd:97`
> — same form.

**The PoG glossary states both, four entries apart, in both trees:**

> `glossary.qmd:73` (= `glossary.tex:74`) — "**Drift**: Passive dynamics driven
> by **gravity, inertia, and constraint forces**, independent of active muscle
> control."
>
> `glossary.qmd:77` (= `glossary.tex:78`) — "**Drift field**: … encodes
> **gravity, Coriolis forces, elastic restoring forces, and damping**."

Line 73 names constraint forces, which no `f(x)` formula in the corpus contains,
and omits Coriolis.

### Why this is not cosmetic

> `articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd:704` —
> "$E_{\text{ZTCF}}(t)$ is constant: $\frac{\mathrm{d}E_{\text{ZTCF}}}{\mathrm{d}t} = 0$."

That theorem is **true under Inventory B and false under Inventory A** — A
contains `C_s η̇` and `τ_pas` damping, which dissipate. It carries no
no-dissipation hypothesis, against `RIGOR_GUIDE.md:36` ("Every theorem states
its hypotheses").

Whichever inventory is chosen, **`GoM ch07:704` needs an explicit hypothesis.**

### Sub-conflict: is drift "purely passive"?

> `articles/theory-part3.qmd:74` — "the \"Drift\" term $f(x)$ represents the
> dynamics of the **Effective Plant** conditioned on the task, **not purely
> passive mechanics**."

against

> `articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd:40` —
> "**No external forces besides gravity are applied; the system is purely passive.**"

`DECISION: UNRESOLVED`

### Cases to address (13 drift-inventory statements)

```
articles/The_Physics_of_Golf/chapters/ch10_energy_transfer.tex:604
articles/The_Physics_of_Golf/chapters/ch14_complete_swing.tex:378,443,449,708
articles/The_Physics_of_Golf/chapters/glossary.tex:74
articles/The_Physics_of_Golf/quarto/ch10_energy_transfer.qmd:501
articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd:296,298
articles/The_Physics_of_Golf/quarto/glossary.qmd:73
articles/affine-nature-golf-swing.qmd:862
articles/drifter-manifesto.qmd:799
articles/theory-part2.qmd:350
```

Plus the energy theorem: `GoM quarto/ch07_counterfactuals.qmd:704` and its
`Volume_I/chapters/ch07_counterfactuals.tex` twin.

---

## 4. Decision 3 — Is ZTCF a no-muscle simulation? (follows from Decision 2)

One side is already CI-pinned:

> `articles/zero-torque-counterfactual.qmd:34` — "Gravity, momentum, and every
> passive or structural force retained by the model remain active. **This is not
> a no-muscle simulation.**"
> *(pinned by `tests/test_proximal_distal_article_contract.py:49`)*

The other side, in **both** PoG trees:

> `quarto/ch06_zero_torque_counterfactual.qmd:22` — "**If all muscle torques are
> set to zero, what trajectory does the system follow…?**"
>
> `:40` — "**No external forces besides gravity are applied; the system is purely
> passive.**"
>
> `quarto/glossary.qmd:845` (= `glossary.tex:846`) — "**Zero-torque
> counterfactual (ZTCF)**: The trajectory the clubhead would follow if all
> muscle torques were set to zero."
>
> `quarto/ch30b_induced_acceleration.qmd:296` — "| ZTCF … | **What happens with
> no muscles** |"

This is the reader-facing surface of Decision 2. Under Inventory A it is simply
wrong and must be corrected in both trees.

`DECISION: UNRESOLVED` (follows Decision 2)

### Cases to address (27 sites)

```
articles/The_Physics_of_Golf/chapters/ch06_zero_torque_counterfactual.tex:33,220
articles/The_Physics_of_Golf/chapters/ch08_triple_pendulum.tex:518
articles/The_Physics_of_Golf/chapters/ch11_flexible_shaft.tex:420
articles/The_Physics_of_Golf/chapters/ch14_complete_swing.tex:516
articles/The_Physics_of_Golf/chapters/ch18_inverse_dynamics_parallel.tex:465
articles/The_Physics_of_Golf/chapters/ch30b_induced_acceleration.tex:358
articles/The_Physics_of_Golf/chapters/glossary.tex:846
articles/The_Physics_of_Golf/quarto/ch06_zero_torque_counterfactual.qmd:22,35,137
articles/The_Physics_of_Golf/quarto/ch08_triple_pendulum.qmd:429
articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd:356
articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd:350
articles/The_Physics_of_Golf/quarto/ch18_inverse_dynamics_parallel.qmd:501,1007
articles/The_Physics_of_Golf/quarto/ch30b_induced_acceleration.qmd:296
articles/The_Physics_of_Golf/quarto/glossary.qmd:845
articles/affine-nature-golf-swing.qmd:1303,1327,2360
articles/drifter-manifesto.qmd:868,1250,1986
articles/intentional-constraint-collapse.qmd:359
articles/theory-part3.qmd:31,428
```

---

## 5. Decision 4 — What type of object is ZVCF?

**No `NOTATION.md` entry. No article claims canonicity. Zero CI enforcement** —
`scripts/check_terminology.py` contains no ZVCF rule of any kind.

The nearest thing to an anchor is an attribution note:

> `articles/theory-part1.qmd:27` — "\"Zero Torque Counterfactual (ZTCF)\" and
> \"Zero Velocity Counterfactual (ZVCF)\" are the authors' naming for these
> constructions in the golf context."

### Four incompatible mathematical types

| Type | Source | Quote |
| --- | --- | --- |
| Generalized **torque**, retains shaft elasticity | `theory-part2.qmd:382` | "$\tau_{\mathrm{ZVCF}}(t) = \tau_{\mathrm{drift}}(q(t),0,\eta(t),0)$" |
| **Acceleration**, gravity only | `GoM ch07_counterfactuals.qmd:222` | "$a_{\text{ZVCF}} := \left.a_{\text{drift}}\right\|_{\dot{q}=0} = -M(q)^{-1}g(q)$" |
| **Acceleration including applied torque τ** | `GoM ch07_counterfactuals.qmd:232` | "$\ddot{q}_{\text{ZVCF}} = M(q)^{-1}(\tau - g(q))$" |
| **State** | `The_Physics_of_Golf/nomenclature.tex:54` | "$\state^{\mathrm{ZVCF}}(t)$ Zero-Velocity Counterfactual state" |

The third contains an input term that another source says is definitionally
excluded:

> `articles/lagrangian-reference.qmd:241` — "It is the configuration-only slice
> of the drift … and contains **no input contribution**"

That is a genuine contradiction, not a modelling variant.

### Sub-conflict: is ZVCF a releasable trajectory?

> `The_Physics_of_Golf/quarto/glossary.qmd:849` (= `glossary.tex:850`) —
> "**ZVCF**: … **the trajectory** if velocities were set to zero while
> maintaining position."
>
> `quarto/ch06_zero_torque_counterfactual.qmd:141` (= `.tex:219`) — "freeze all
> motion in the middle of the swing … **and then release**. The system would fall
> under gravity alone"

against

> `articles/theory-part2.qmd:398` — "The ZVCF is not intended to represent a
> physically realizable motion … The system would generally **not** remain in
> equilibrium"

### Sub-conflict: `ch06` contradicts itself six lines apart, both trees

> `quarto/ch06_zero_torque_counterfactual.qmd:126` — "the acceleration that would
> result from **gravity and Coriolis torques** if all velocities were set to zero"
>
> `:132` — "This equation contains only gravity … It **excludes
> Coriolis/centrifugal terms**"

`DECISION: UNRESOLVED`

---

## 6. Decision 5 — DCR expansion and formula ⚠️ A TEST CONTRADICTS NOTATION.md

### Expansion

> `NOTATION.md:149` — "The bare acronym **DCR** is reserved site-wide for the
> **Drift–Control Ratio** … The aerodynamic drag–curve ratio (formerly also
> abbreviated \"DCR\") is written **DgCR** to avoid the collision."

But:

> `tests/test_physics_of_golf_glossary.py:22` — `assert "drift-to-control ratio"
> in glossary_text`
> `:34` — the same assertion against `glossary.tex`

**A CI test requires a form the declared source of truth does not use.** One must
yield. `check_terminology.py` bans neither "Drift-to-Control Ratio" (38 sites)
nor "Drift coefficient ratio" (2 sites, matching nothing anywhere).

### Formula — five incompatible definitions

| # | Formula | Source |
| --- | --- | --- |
| 1 | `‖f_acc‖_M / ‖G_acc u_max 1‖_M` — inertia-weighted, acceleration block | `NOTATION.md:142`; `controllability-drift-ratio.qmd:278` |
| 2 | `‖f(x)‖ / ‖g(x)u(t)‖` — **full state**, unweighted, **policy-dependent** | `controllability-drift-ratio.qmd:25`; `nomenclature.tex:55` |
| 3 | `ρ(x) := ‖f(x)‖ / ‖G(x)u_max‖` — full state, symbol `ρ` | `GoM ch07:332` (+ `.tex:315`) |
| 4 | `‖Wf(x)‖ / (max_{‖u‖≤u_max}‖WG(x)u‖ + ε)` — operator norm, weighting `W` | `PoG ch05_affine_structure.qmd:313` |
| 5 | "the ratio of passive to active **torques**" | `PoG glossary.qmd:63` *(CI-pinned)* |

Formulas 2 and 3 use the full-state `‖f(x)‖` that the canonical article itself
calls invalid:

> `controllability-drift-ratio.qmd:231` — "A naïve application of the Euclidean
> norm to the full state vector drift $\|f(x)\|$ **mixes units of velocity
> (rad/s) and acceleration (rad/s²)**."

Formulas 1 and 4 differ numerically even at identical weighting: `‖G u_max 1‖`
is one corner of the torque box; `max_{‖u‖≤u_max}‖G u‖` is an induced operator
norm.

### Two dead citations

> `controllability-drift-ratio.qmd:284` — "Matches the definition in [Theory Part
> I] and the glossary in [Zero-Torque Counterfactual]."

`theory-part1.qmd` contains **no DCR definition** (one hit, line 568, a See-Also
link). The ZTCF glossary contains none either.

`DECISION: UNRESOLVED`

**Suggested sequence:** expansion first (mechanical, unblocks a
`check_terminology` rule), then formula (a modelling call), then repair the
citations.

---

## 7. Decision 6 — Symbols: `G` vs `g`, and the gravity collision

`G` currently denotes **both** the input matrix and the gravity vector, inside
single files:

> `theory-part1.qmd:428` — `G(q)` as gravity
> `theory-part1.qmd:493` — `f(x) + g(x)u`, `g` as the input map

`articles/zero-torque-counterfactual.qmd` uses both forms for the input map:
`G(x)` at `:108`, `g(x)` at `:140`.

`NOTATION.md`'s "Symbol Overloading Reference" (lines 224–278) covers F, R, m,
ω, v — **not G, f, g, or u** — despite:

> `content-development/RIGOR_GUIDE.md:86` — "If you need a different quantity,
> **give it a different name** rather than overloading an existing one."

Usage: 254 `G(x)`/`G(q)` across 36 files, 247 `g(x)`/`g(q)` across 35 files,
**19 files using both**.

`DECISION: UNRESOLVED`

### Cases to address — files using both forms

```
articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex   (G:10 g:2)
articles/The_Geometry_of_Motion/Volume_I/chapters/ch04_contraction.tex     (G:5  g:1)
articles/The_Geometry_of_Motion/Volume_I/chapters/ch07_counterfactuals.tex (G:29 g:2)
articles/The_Geometry_of_Motion/quarto/ch03_superposition.qmd              (G:10 g:2)
articles/The_Geometry_of_Motion/quarto/ch04_contraction.qmd                (G:5  g:1)
articles/The_Geometry_of_Motion/quarto/ch07_counterfactuals.qmd            (G:28 g:2)
articles/affine-nature-golf-swing.qmd                                      (G:11 g:45)
articles/calculation-framework-comparison/multibody-drift-control-v3.qmd   (G:3  g:11)
articles/controllability-drift-ratio.qmd                                   (G:1  g:9)
articles/drift-components-wrench-double-pendulum.qmd                       (G:4  g:15)
articles/drifter-manifesto.qmd                                             (G:10 g:48)
articles/inverse-dynamics-inference.qmd                                    (G:1  g:3)
articles/nonlinear-control-insights.qmd                                    (G:5  g:1)
articles/sources-of-nonlinearity.qmd                                       (G:24 g:11)
articles/superposition.qmd                                                 (G:35 g:22)
articles/theory-part1.qmd                                                  (G:3  g:13)
articles/theory-part2.qmd                                                  (G:2  g:12)
articles/theory-part4.qmd                                                  (G:5  g:10)
articles/zero-torque-counterfactual.qmd                                    (G:7  g:1)
```

---

## 8. Decision 7 — Where canonicity lives 🔑 DO THIS FIRST

Canonicity is currently asserted in three incompatible places:

1. **`NOTATION.md`** — claims authority over everything, silent on all core terms.
2. **Individual articles declaring themselves canonical** —
   `zero-torque-counterfactual.qmd:77`, `controllability-drift-ratio.qmd:276`.
3. **Hardcoded blocklists** in `scripts/check_terminology.py`.

`docs/development/content-architecture.md` ratifies none of it. Its canonical
table (lines 28–33) designates `articles/theory-part*.qmd` canonical for "Core
affine theory" only, and never mentions ZTCF, ZVCF, or DCR.

Every conflict in this document is downstream of this.

`DECISION: UNRESOLVED`

**Proposed shape:** `NOTATION.md` becomes the single home. Each of ZTCF, ZVCF,
`f`, `G`, `u`, "drift" gets one entry with:

- the expansion (with hyphenation fixed),
- the formal definition,
- an explicit **scope tag**: instantaneous / trajectory / either-with-qualifier,
- what is zeroed and what is held fixed,
- a pointer to the article that derives it.

---

## 9. Enforcement gap

| Term | Banned variants | Positive check | Gate |
| --- | ---: | --- | --- |
| ZTCF | 5 | none | ✅ blocklist |
| DCR | 2 (3 live expansions, 1 CI-*required* against NOTATION.md) | none | ⚠️ partial |
| ZVCF | 0 | none | ❌ none |
| DgCR | 0 | none | ❌ none |

**The structural problem:** `check_terminology.py` is an *enumerated blocklist*.
It catches only expansions someone already found and wrote down. That is exactly
how "zero transfer of control and force" survived the #3526 unification for four
months in a compiled textbook.

**Proposed additions once decisions land:**

- A **positive** check: every first use of `ZTCF` on a page carries a qualifier
  (if Decision 1B), or matches the ratified scope (if 1C).
- Any ZVCF rule at all.
- A DgCR rule, so a reintroduced bare "DCR" for the aerodynamic quantity fails.
- A check that `NOTATION.md` contains an entry for every acronym the gate
  enforces — closing the loop that made this possible.

---

## 10. Already fixed (context for reviewers)

These were resolved during the writing-quality programme and are **not** open
decisions. They are listed so a reviewer does not re-report them.

| Fix | Where | Commit |
| --- | --- | --- |
| ZTCF expanded as "zero transfer of control and force" | `ch31_swing_plane_launch` **both trees** | `5c2ce62` |
| Banned identity "Total motion = ZTCF + Control correction" | `ch06_zero_torque_counterfactual.tex:130` | `809a276` |
| 12 content corrections that reached `.qmd` but not `.tex` | both textbooks | `39b209d` |
| 8 overclaims in layman's blocks, 5 asserting trajectory superposition | site-wide | writing-quality pass |

The trajectory-superposition identity pattern now returns **0 matches**
corpus-wide.

---

## 11. Open structural findings

- **The content is triplicated, not duplicated.** `articles/motion-control/`
  holds `chapter1.tex`–`chapter11.tex`, a combined `Control_Is_Motion_Complete.tex`,
  and committed PDFs — a third divergent copy of Geometry of Motion Volume II.
  It is not in `_quarto.yml`, not in `compile-textbooks.yml`, and not referenced
  by any `.qmd` or `.yml`. It still carries text corrected in the other two
  trees. Decide: archive, delete, or wire into CI.
- **Pre-existing `.tex`-only errors** still in the PDFs:
  `Volume_0/chapters/ch02_state_space.tex:273` ("The **a** and B Matrices"),
  `ch30_kinetic_chain.tex:133` ("For **a** ideal coupled oscillator model").
  `ch30_kinetic_chain.tex:514` and its `.qmd` twin both read "for **a** 80 kg
  golfer" — consistent, uncorrected in both.
