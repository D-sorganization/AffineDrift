# Editorial Review of Three AffineDrift Textbooks

**Date:** 2026-04-11
**Scope:** *The Drifter Manifesto*, *The Geometry of Motion* (Vols 0–I), *The Physics of Golf*
**Stance:** Adversarial editorial review from a scientific publishing house. The goal of this
document is not to celebrate the manuscripts but to identify every way in which they currently
fall short of publishable standards, prioritized by severity, and to recommend concrete fixes.

The three books together currently total roughly 44 000 lines of LaTeX / Quarto source. The
review that follows is a structured sample-based audit, not a line-by-line read, and it is
written to be useful to an author working on a second pass.

---

## 1. Executive Summary

Taken as a whole, the three volumes show a genuine and unusually ambitious effort to unify
geometric mechanics, optimal control, neuromotor science, and the practical biomechanics of the
golf swing. The structural skeleton is defensible: each book has a clear scope, internally
consistent notation, and a top-down narrative that the others reinforce. The material in the
*Geometry of Motion* Volume 0 chapters on linear algebra, configuration spaces, exponential
coordinates, and the articulated-body algorithm is solid undergraduate-to-graduate teaching
copy.

But as it stands, the manuscripts are **not yet ready for publication** by any serious academic
press. In my judgment the dominant weaknesses, in order of severity, are:

1. **Inconsistent and in places absent citation practice.** The *Drifter Manifesto* contains
   zero `\cite{}` / `[@key]` calls across its ~2 600 lines, despite invoking foundational
   results from geometric control theory, Lagrangian mechanics, and multibody dynamics.
   *Physics of Golf* is equally uneven: core chapters on affine structure, the zero-torque
   counterfactual, the triple pendulum, and parallel mechanisms carry zero citations, while
   motor-control and motor-learning chapters cite twenty each. The bibliography files exist and
   are reasonably populated; they are simply not being used where it matters most.

2. **Unsupported quantitative claims ("magic numbers") presented as fact.** Specific examples
   include "elite golfers produce clubhead speeds within 2 % of their average", "30–50 ms
   neural delays", "5–15 cm extra clubhead displacement due to shaft flex", "DCR ≈ 40 : 1 at
   impact", and the torque budgets of "60–80 N·m generated over the whole swing". Some of these
   numbers are defensible from the literature, but they are stated without attribution and
   without explicit computation from cited primary sources.

3. **Tone drifts toward the promotional.** The words *profound*, *remarkable*, *revolutionary*,
   and *astonish* appear dozens of times across the corpus. Individually each instance is
   minor; collectively they corrode credibility. A reader looking for mathematical rigour is
   distracted by a voice that keeps telling them they are witnessing something great. The book
   should describe the physics and let the reader decide.

4. **Editorial inconsistency across and within books.** The *Physics of Golf* uses imperial
   units in chapter 1 (`32 ft/s²`, `1 lb`) and SI units elsewhere; some chapters are ~250 lines
   and others ~1 300; some chapters use `driftcontrol` boxes and others do not; *Geometry of
   Motion* Vol I has chapters ranging from 1 000 to 1 700 lines with highly variable depth of
   citation; the *Drifter Manifesto* mixes appendices labelled A–D with Parts I–V without a
   clean cross-reference.

5. **Several technical claims need tightening.** A handful of passages make statements that an
   adversarial reviewer would challenge: e.g. the LQR gain-margin proof sketch in *Geometry of
   Motion* Vol I Ch. 6 manipulates the algebraic Riccati equation in a way that is not an
   identity as written, and the *Drifter Manifesto*'s claim that "the approximation is tight
   because the ZTCF remains close to the actual trajectory" deserves a bound rather than an
   assertion. Section 6 below enumerates the most visible instances.

6. **Scope vs. audience mismatch.** The stated goal is "graduate or PhD level". Several sections
   currently address a motivated lay reader — `laymansbox` panels, river-and-boat analogies,
   "your wrists are creating that acceleration, right? Wrong." — and a graduate reader would
   find the juxtaposition uneven. These panels should either be demoted to sidebars with clear
   visual separation or pruned for a PhD-level edition.

None of these problems are structural: the mathematics is largely correct and the exposition
is already above average. But the manuscripts currently read as a late first draft, not as a
camera-ready text. The rest of this document itemizes what I would require before
recommending acceptance.

---

## 2. Bibliography and Citation Audit

### 2.1 Citation counts per chapter

Measured by `\cite{}` occurrences (LaTeX) or `[@key]` occurrences (Quarto):

| File | `\cite` count |
|---|---:|
| `articles/drifter-manifesto.qmd` | **0** |
| **Geometry of Motion – Volume 0** | |
| ch01 linear algebra | 9 |
| ch02 state space | 8 |
| ch03 configuration | 7 |
| ch04 rotations SE(3) | 9 |
| ch05 screw axes | 6 |
| ch06 exponential coordinates | 9 |
| ch07 recursive algorithms | 11 |
| ch08 spatial algebra | 9 |
| ch09 product of exponentials | 10 |
| ch10 ABA | 12 |
| ch11 Lagrangian mechanics | 12 |
| ch12 machine learning | 12 |
| **Geometry of Motion – Volume I** | |
| ch01 foundations | **3** |
| ch02 variational | 5 |
| ch03 superposition | 4 |
| ch04 contraction | 5 |
| ch05 optimal control | 4 |
| ch06 duality | **2** |
| ch07 counterfactuals | **3** |
| ch08 applications | 5 |
| **Physics of Golf** | |
| ch01 why physics | **0** |
| ch02 language of motion | 5 |
| ch03 double pendulum | 1 |
| ch04 forces and torques | 1 |
| ch05 affine structure | **0** |
| ch06 zero-torque counterfactual | **0** |
| ch07 constraint forces | 6 |
| ch08 triple pendulum | **0** |
| ch09 parallel mechanisms | **0** |
| ch10 energy transfer | **0** |
| ch11 flexible shaft | **0** |
| ch12 fascia | 7 |
| ch13 interdisciplinary | 4 |
| ch14 complete swing | 6 |
| ch15 GRF | 8 |
| ch16 muscle→joint torques | 1 |
| ch17 muscle force generation | 1 |
| ch18 inverse dynamics parallel | **0** |
| ch19 aerodynamic drag | 5 |
| ch20 soft tissue | 1 |
| ch21 spine modeling | 6 |
| ch22 anatomy/joint modeling | **0** |
| ch23 DOF/URDF models | 14 |
| ch24 motor control brain | 10 |
| ch25 motor learning | 20 |
| ch26 remarkable brain | 20 |
| ch27 passive distributed control | 3 |
| ch28 impact/collision | 7 |
| ch29 joint damping/friction | 3 |
| ch30 kinetic chain | 6 |
| ch31 swing plane/launch | 9 |
| ch32 putting | 4 |

### 2.2 Interpretation

- **The Drifter Manifesto has no citations at all.** Part 1 §3 of the manuscript references
  "Isidori 1995; Nijmeijer & van der Schaft 1990" in the running prose, but the document never
  uses a BibTeX key, and no reference list is rendered. For a paper whose thesis depends on
  the classical control-affine form
  $\dot{x} = f(x) + g(x)u$
  this is not a small problem. At minimum the following should be cited on first use and
  briefly discussed in text: Isidori (1995) *Nonlinear Control Systems*; Nijmeijer and van der
  Schaft (1990) *Nonlinear Dynamical Control Systems*; Sastry (1999) *Nonlinear Systems*;
  Khalil (2002) *Nonlinear Systems*; Bullo and Lewis (2005) *Geometric Control of Mechanical
  Systems*; Murray, Li, and Sastry (1994) *A Mathematical Introduction to Robotic Manipulation*.
  Featherstone (2008) *Rigid Body Dynamics Algorithms* is necessary for the modal-shaft /
  recursive-dynamics passages. Lynch and Park (2017) *Modern Robotics* for the Jacobian and
  kinematic-interface material.

- **Physics of Golf chapters 5 and 6 are the single most important chapters of the book and
  currently cite nothing.** These are the chapters that introduce the control-affine form and
  the ZTCF; they need to carry the bulk of the theoretical provenance. At present a reader is
  asked to accept the decomposition without any external anchor, and an adversarial reviewer
  would call this "authorial stipulation".

- **Chapters 8, 9, 10, 11, 18, 22 likewise cite nothing**, despite making quantitative claims
  about torques, clubhead speeds, shaft deflection, and hip joint range of motion — all topics
  where peer-reviewed sources (Nesbit 2005, MacKenzie & Sprigings 2006, Penner 2001/2003,
  Betzler et al. 2012, Sprigings & Mackenzie 2002, Miao et al. 2023, McTeigue 1994) are
  available *in the existing bib file* `golf_physics.bib`. The authors have done the
  bibliography work and then left it on the floor.

- **Geometry of Motion Volume I is thinly cited relative to Volume 0.** Vol 0 is introductory
  and averages ~9 citations per chapter; Vol I is the research-level volume and averages ~4.
  This is backwards — the more sophisticated the material, the more important it is to tell
  the reader where the result came from. Ch. 6 (Duality) is particularly exposed: it invokes
  Willems' dissipation framework, Anderson and Moore's robustness results, and the
  Kalman–Yakubovich–Popov lemma, but only carries two `\cite` calls.

### 2.3 Inline "author-year" mentions that are not citations

Several passages use inline prose of the form "Willems (1972)", "Anderson and Moore (1971)",
"Tobin et al. (2017)", "OpenAI's Dactyl project", "Ball's *Treatise on the Theory of Screws*".
Some of these are backed by a later `\cite`, but many are not. A scientific text should never
rely on a reader's goodwill to supply the reference; every author-year phrase should either
be a formal `\cite` or be removed.

### 2.4 Bibliography files themselves

| File | Entries | Types |
|---|---:|---|
| `references/affine-drift.bib` | 135 | 74 article, 51 book, 10 misc |
| `articles/The_Geometry_of_Motion/geometry_of_motion.bib` | 81 | — |
| `articles/The_Physics_of_Golf/golf_physics.bib` | 161 | 114 article, 42 book, 3 misc |

The raw counts are healthy. The golf bibliography is very well populated with Penner, Nesbit,
MacKenzie, Sprigings, Slocum and company. The problem is distribution, not availability.

**The `references/affine-drift.bib` file has a second, more subtle problem:** its first ten
entries are `@misc` self-references to other AffineDrift articles with 2026 dates and fragile
relative URLs ("articles/Tangent%20Hyperplane%20Articles/..."). Self-citation is legitimate, but
a peer reviewer will notice immediately that the very first entries of the bibliography all
point back at the authors. Move these to the end of the file and intersperse them with the
external literature when cited.

### 2.5 Recommendation

- Set a floor of 4–6 citations per chapter in the *Physics of Golf*, with chapters 5, 6, 8, 9,
  10, 11, 18 and 22 brought up first. Every quantitative claim that survives editing should be
  anchored to either a primary source or an explicit computation from stated parameters.
- Add ~15 first-call citations to *The Drifter Manifesto* and insert a BibTeX header so that
  the Quarto build renders a reference list. The manifesto should cite Isidori, Nijmeijer &
  van der Schaft, Sastry, Khalil, Bullo & Lewis, Murray/Li/Sastry, Featherstone, Lynch & Park
  on first use of the relevant material; it should cite Siciliano et al. (2009) for the
  manipulator equation; and it should cite Book (1984) or Dwivedy & Eberhard (2006) for
  the flexible-shaft modal reduction.
- For the *Geometry of Motion* Volume I, bring Ch. 6 (Duality) and Ch. 7 (Counterfactuals) up
  to 6–8 citations each. Willems (1972), Anderson & Moore (1971), Doyle & Stein (1981),
  Safonov (1980), Zames (1981), Agrachev & Sachkov (2004), Sontag (1998), Bressan & Piccoli
  (2007), Bloch (2003).

---

## 3. The Drifter Manifesto

### 3.1 What works

- The scope and exclusions callout at the top of §1 is well executed: the reader knows
  exactly what is and is not being claimed.
- The "Frozen Strategy" / Effective Plant callout is a good piece of self-policing — the
  authors have anticipated the critique that biological impedance is state-dependent and
  answered it directly.
- The Schur-complement block inversion of the rigid–flexible mass matrix is cleanly derived.
- The "Approximation Note on the Subtraction Identity" callout near the end of Appendix D is
  the right kind of epistemic humility: the authors admit the identity
  $\tau_\text{total} - \tau_\text{ZTCF} = \tau_\text{ZVCF}$
  is exact only at $t=t_0$ and explain why the numerical near-equality is tight. This is
  exactly the register the whole manuscript should adopt.

### 3.2 What needs fixing

1. **No bibliography.** See §2.1. This is the single largest problem with the document.

2. **"Critics' Comments" is structurally a good idea, but it reads as a straw-man
   exchange.** Each critique is answered by the authors themselves inside the same box.
   Consider either (a) naming the actual sources of each critique and citing them, or (b)
   rewriting the responses as "the framework remains applicable when …" rather than "Our
   Response:" rebuttals. As written, the reader cannot tell whether the critique is being
   taken seriously or set up to be knocked down.

3. **Several words do work they cannot support.** The manifesto uses "rigorous" and
   "rigorously" a dozen times in the first 200 lines. A text that has to assert its own rigour
   is typically not demonstrating it. Trim to at most 2–3 instances where the word is earning
   its keep (e.g. the Schur-complement block inversion).

4. **The "rowboat on a river" analogy in §1 is fine**, but it repeats a similar passage in
   *Physics of Golf* Ch. 5 ("standing in a river, the current is the drift field") almost
   verbatim. Pick one and cross-reference.

5. **The claim that the framework is "falsifiable"** (closing remarks of Appendix D) needs a
   concrete falsification test. A theory is falsifiable only if the authors can state the
   observation that would cause them to withdraw it. The current phrasing is rhetorical, not
   Popperian.

6. **The Part numbering is inconsistent with section numbering.** The document uses "Part I",
   "Part II", …, "Part V" in the narrative prose, but the top-level sections are numbered
   `{#sec-part1}` and the rendered HTML will use automatic numbering. A reader following the
   cross-references is going to drift between "Part 2" and "§2". Settle on one nomenclature.

7. **Several equations are introduced without the quantifier domains.** e.g. "where
   $\phi_i(s) \in \mathbb{R}^3$" appears without stating whether $s \in [0, L]$ and without
   declaring the regularity of $\phi_i$ (typically $C^2$ with clamped boundary conditions).
   A graduate reader will want these.

8. **The "Final Remarks" section promises "a rigorous, falsifiable mechanical theory of the
   golf swing".** This overclaims. The manuscript presents a *decomposition* of a mechanical
   model, not a theory of the golf swing itself. "Mechanical decomposition framework" is
   accurate; "theory of the golf swing" invites counter-examples the framework does not
   address (impact, aerodynamics, GRF).

### 3.3 Suggested expansions

A PhD-level reader would appreciate (in order of value):

- A short section proving that drift invariance
  $\partial f(x) / \partial u = 0$
  is a *definition* of control-affine systems, not a consequence of one. State clearly that
  the control-affine class is closed under the decomposition but other nonlinear systems
  (notably bilinear and polynomial-in-control systems) are not.
- An explicit discussion of when the ZVCF is independent of the parameterization of time.
  The manifesto implicitly assumes a smooth autonomous drift; if the drift is time-varying
  (e.g. gravity in a rotating frame), the ZVCF becomes a family rather than a single torque.
- A derivation of the DCR's units. As currently written, the Drift-Control Ratio is a ratio
  of two generalized forces of different physical interpretation and in a multi-joint system
  it is not a well-defined scalar. Either define it as a matrix norm
  $\|M^{-1}[C\dot q + g]\| / \|M^{-1} \tau\|$
  with a specified norm, or define it componentwise and carry a subscript.
- A section on the Lie bracket $[f, g_i]$ and what it buys the framework, since the Critics'
  Comments already invoke Lie brackets to defend the need for geometric control theory.

---

## 4. The Geometry of Motion — Volume 0

### 4.1 What works

- Volume 0 is in the best shape of the three books. The linear-algebra chapter is a solid
  companion to Strang; the SE(3) / screw-axis / exponential-coordinates chain through
  chapters 4–9 tracks Lynch & Park and Murray/Li/Sastry cleanly; chapter 10 on the
  articulated-body algorithm is unusually lucid and has 12 citations to back it up.
- The `laymansbox` environment works well at this level of the text — it lets the reader
  decompress between proofs without breaking the narrative.
- The historical framing in chapter 1 and chapter 4 is appropriate for a graduate textbook.

### 4.2 What needs tightening

1. **"Profound"-class adjectives.** Thirteen instances across Volume 0, distributed across
   nine chapters. Examples:
   - Ch. 1: "This has profound physical consequences." → "This has direct physical
     consequences." (The physics is the same; the adjective adds nothing.)
   - Ch. 4: "Rotation is profoundly mathematically problematic" → "Rotation is mathematically
     awkward"
   - Ch. 11: "The development of Lagrangian mechanics represents one of the most profound
     intellectual shifts in the history of mechanics." This is a value judgment. If retained,
     attribute it to Lanczos (1970) or Arnold (1989); otherwise drop.
   - Ch. 2: "Kalman's insight was revolutionary". Use "foundational" — the word does the
     same work without inviting dispute.

2. **Ch. 1 §1 claims "linear algebra — the mathematics of vectors, matrices, and linear
   transformations — is arguably the single most consequential mathematical framework
   underpinning all of modern engineering".** "Arguably" is doing a lot of hedging here.
   Reword: "Linear algebra is the mathematical language of modern engineering."

3. **Ch. 10 p. 829** asserts "This two-stage architecture — ABA followed by contact resolution
   — is the dominant paradigm in modern simulation." Cite MuJoCo (Todorov et al. 2012), Drake
   (Tedrake et al.), Bullet (Coumans), and Featherstone (2008) §11.

4. **Ch. 11 final paragraph** says Hamiltonian mechanics "underpins modern developments in
   geometric integration, optimal control, and quantum mechanics". This is true, but the
   citation `\cite{goldstein2002,arnold1989}` does not reach all three claims. Split out a
   citation for geometric integration (Hairer, Lubich, Wanner 2006; Marsden & West 2001) and
   for symplectic optimal control (Marsden & Ratiu 1999 Ch. 7).

5. **Ch. 12 machine learning.** The chapter mentions "Tobin et al. (2017)" and "OpenAI's
   Dactyl project" in prose without `\cite` calls. Both papers are in the bib file or should
   be — add them.

### 4.3 Suggested additions

- **Ch. 4 §SE(3):** add a short discussion of the non-flatness of the exponential map away
  from the identity and the difference between $\log_\text{SE(3)}$ and the matrix log. This is
  the sort of detail that graduate students trip over and that the chapter currently glosses.
- **Ch. 7 recursive algorithms:** add a subsection on Featherstone's spatial inertia and
  articulated-body inertia definitions in explicit form, so that Vol 0 Ch. 10 does not have to
  reconstruct them.
- **Ch. 11:** a short subsection on when the Lagrangian formulation fails (non-holonomic
  constraints, Chetaev vs. d'Alembert, vakonomic vs. mechanical solutions). This is a known
  PhD-level pitfall that the current chapter skips.

---

## 5. The Geometry of Motion — Volume I

### 5.1 What works

- The chapter-level theme — "foundations → variational → superposition → contraction →
  optimal control → duality → counterfactuals → applications" — is a defensible ordering for
  a research-level monograph. The superposition chapter in particular reads as original
  synthesis.
- Ch. 7 (Counterfactuals) opens with a clean invocation of Agrachev and Sachkov and uses the
  Picard–Lindelöf theorem to ground the ZTCF's well-posedness. This is exactly the right
  move.
- The link to the *Physics of Golf* via the ZTCF / ZVCF language is consistent: Vol I gives
  the geometry, *Physics of Golf* Ch. 5–6 gives the application.

### 5.2 What needs fixing

1. **Citation density is too low for a research volume.** Chapters 6 and 7 average ~2 and ~3
   citations respectively; see §2.1.

2. **Ch. 6 Duality §2.3 "Robustness Margins from LQR".** The "Proof Sketch" of the gain-margin
   proposition manipulates the ARE
   $A^T S + S A - S B R^{-1} B^T S + Q = 0$
   into a form "$A^T S + S A = -Q - S B R^{-1} B^T S + 2 S A$" which, as written, is not an
   algebraic identity — an extra "$+ 2 S A$" appears on the right-hand side. The subsequent
   manipulation produces the correct final result (the classical LQR $(\tfrac{1}{2}, \infty)$
   gain margin and 60° phase margin), so the issue is in the middle of the proof. Rewrite the
   proof in terms of
   $\dot V = -x^T(Q + S B R^{-1} B^T S) x$ at $\eta = 1$
   and then perturb the closed-loop $A - \eta B K$ using the fact that $S$ satisfies the ARE.
   The cleaner reference is Anderson & Moore (1990) §5.1 or Zhou, Doyle, Glover (1996) §14.

3. **Ch. 6 claims that the Riccati solution delivers "remarkable robustness properties *for
   free*".** The "for free" is misleading: these margins are *guaranteed* only for the
   state-feedback LQR at the input, and they can be destroyed by output feedback — this is
   the famous Doyle counterexample (Doyle 1978 "Guaranteed margins for LQG regulators"). That
   counterexample should be acknowledged in the same section, otherwise a reader will walk
   away with a false sense of safety.

4. **Ch. 7 §1 second paragraph** says "The control-affine structure has been extensively
   studied in modern control theory `\cite{Khalil2002, Sastry1999, Murray1994}`. It provides
   a natural framework for understanding the interplay between passive and active dynamics."
   This is a drop-in sentence — it does not pay for itself. Either delete or expand to a
   one-sentence account of *what* each of the three cited books contributes.

5. **Ch. 8 Applications (1 721 lines)** is by far the longest chapter in either volume and
   risks becoming a "catch-all" that should be several chapters. A clean split would be
   applications-to-mechanical-systems vs. applications-to-learning-based-control.

### 5.3 Suggested expansions

- **Ch. 4 Contraction.** Add a subsection linking contraction metrics to Riemannian geometry
  (Lohmiller & Slotine 1998; Forni & Sepulchre 2014), and explicitly discuss when contraction
  implies exponential stability vs. asymptotic stability.
- **Ch. 5 Optimal Control.** Add a side-by-side comparison of Pontryagin's Minimum Principle
  and HJB, with a worked example where the two give different structures (bang-bang vs.
  singular arcs).
- **Ch. 7 Counterfactuals.** The ZTCF deserves a section on sensitivity — how does the
  counterfactual trajectory depend on perturbations to the initial state? This is the
  Gronwall-type bound that would let the reader quantify the approximation error of the
  subtraction identity flagged in the *Drifter Manifesto*.

---

## 6. The Physics of Golf

### 6.1 What works

- The book's narrative arc — "physics matters → language of motion → double pendulum →
  forces → affine structure → counterfactuals → constraints → energy → flexible shaft →
  biological detail → motor control → learning → impact → kinetic chain → putting" — is
  probably the right order and the right level of ambition.
- The later chapters on motor control, motor learning, and the "remarkable brain" are the
  most heavily cited in the book and show that the authors can do the work when they choose
  to.
- Ch. 15 (ground reaction forces), Ch. 21 (spine modeling), and Ch. 25 (motor learning) are
  currently the strongest chapters and can serve as the template for the rest.

### 6.2 The central citation problem

Chapters 5, 6, 8, 9, 10, 11, 18, 22 carry zero `\cite` calls between them. These include the
chapter that introduces the control-affine form, the chapter that introduces the ZTCF, the
chapters that extend to the triple pendulum and parallel mechanisms, and the chapters on
flexible shafts and joint modeling. These are not minor background chapters — they are the
theoretical spine of the book. Every one of them should be rewritten to:

- Open with an explicit statement of where the result being taught originates (e.g.
  control-affine form: Isidori 1995 §3; zero-torque counterfactual: AffineDrift *Drifter
  Manifesto* §2 + Bloch 2003 §2; flexible shaft: Book 1984 + Rao 2019 Ch. 8).
- Cite every quantitative claim (see §6.3 below).
- Close with a "Further Reading" paragraph pointing at 2–3 primary sources the reader can go
  to for depth.

### 6.3 Magic numbers with no source

Below is a non-exhaustive list, in the order I encountered them. All of these need either a
citation or an explicit computation from a cited parameter set, or they need to be removed.

- **Ch. 1 exercise 1:** "Use $g = 32\ \text{ft/s}^2$". The rest of the book uses SI units.
  Normalize.
- **Ch. 1 `driftcontrol` box:** "You're exerting an upward force equal to the weight's weight
  (call it $W = 1\ \text{lb}$)". Imperial in an SI book; "weight's weight" is a typo.
- **Ch. 5 §DCR example:** "$M_{11} \approx 2.22\ \text{kg m}^2$", "50 N·m torque produces
  $50 \times 0.45 = 22.5\ \text{rad/s}^2$", "60–80 N·m generated over the whole swing". None
  of these numbers are derived from the Ch. 3 double-pendulum parameter table, and none are
  cited. They should either trace back to the Ch. 3 table in one explicit step or be dropped.
- **Ch. 5:** "DCR > 50 means the last 50 milliseconds before impact" — an operational
  threshold masquerading as a physical fact. Either calibrate against the double-pendulum
  simulation of Ch. 3 (in which case state the simulation parameters used) or retract.
- **Ch. 6 §ZTCF at impact:** "assume the club head reaches 100 mph (44.7 m/s)", "DCR at this
  moment is approximately 40:1", "angular velocity of 50 rad/s about the shoulder". Three
  unsupported numerical claims in two sentences. The 100 mph figure is defensible (PGA Tour
  averages, e.g. Trackman 2023, which is already in `golf_physics.bib` as `trackman_launch`),
  but the 50 rad/s and 40 : 1 numbers are AffineDrift-specific and need to be presented as
  "in our double-pendulum simulation with the Ch. 3 parameters we obtain …".
- **Ch. 6:** "contact lasts only 0.5 ms" — the classical impact-duration figure. Cite
  Cochran & Stobbs (1968) or Gobush (1996).
- **Ch. 11:** "extra clubhead displacement due to shaft flex is 5–15 cm (2–6 inches)", "extra
  velocity at impact is 5–15% of the clubhead speed". Cite Butler & Winfield (1994),
  MacKenzie & Boucher (2017), or Newman et al. (1998). If the source does not exist, soften
  to "order-of-magnitude estimates suggest".
- **Ch. 22:** "A golfer with FAI cannot internally rotate the lead hip as much … Reduce
  internal rotation ROM to ~20–30° instead of 40°". Cite Kim et al. (2011) or Gulgin et al.
  (2009) for the FAI ROM reduction; cite Murray et al. (2009) or Tavares et al. (2022) for
  the normative 40°.
- **Ch. 24 §Constraints on the Brain's Control Problem:** "30–50 ms neural delays",
  "50–100 ms muscle force rise time constant", "80–150 ms visual feedback", "10–20 ms
  vestibular feedback", "5–10% muscle force variability". All of these are textbook values
  (Kandel et al. 2013, Purves et al. 2018, Shadmehr & Wise 2005, Faisal et al. 2008), and
  `Kandel2013` is already cited elsewhere in the chapter — extend the citation to the
  numerical ranges.
- **Ch. 24 §laymansbox:** "An elite golfer produces clubhead speeds within 2 % of their
  average, swing after swing". This is the one I would retract hardest: the figure varies
  from 1 % to 4 % across the literature (MacKenzie 2012; Hume et al. 2005; Lamb & Glazier
  2018) and the right framing is "coefficient of variation in the 1–4 % range" with a
  citation, not "2 %".
- **Ch. 9:** "For a 200-pound golfer (mass 90 kg)". 200 lb is 90.7 kg; no need to mix units.

### 6.4 Tone

The book sometimes reaches for rhetorical temperature it cannot sustain:

- Ch. 13: "When they do, remarkable insights emerge" — the reader decides what is remarkable.
- Ch. 13: "The brain's computational capacity is remarkable — managing 200+ muscles in real
  time — yet fragile". The 200+ figure is fine but the "remarkable" editorializes on top of
  it.
- Ch. 24 laymansbox: "The answer will astonish you" — remove; this is a marketing register.
- Ch. 26: chapter title "The Remarkable Brain". Retitle "Biological Constraints and Human
  Motor Performance" or similar. The current title telegraphs the conclusion.
- Ch. 26: "No robot can currently do this. No engineered control system has come close."
  This is a strong empirical claim. Either cite a benchmark (DARPA Robotics Challenge,
  OpenAI Five, Boston Dynamics Atlas) and defend it, or soften to "No currently deployed
  robotic platform reproduces this combination of speed, precision, and adaptability".
- The `mythreality` environment in Ch. 24 ("Fantasy: … Reality: …") is unnecessarily
  combative. Rename to `mechanism` or `clarification`.

### 6.5 Layout and editorial consistency

- Ch. 32 (putting) is **58 lines** while Ch. 23 (DOF/URDF models) is **1 265 lines**. A
  textbook should not have an order-of-magnitude spread between adjacent chapters. Either
  expand Ch. 32 into a full chapter on the putting stroke (with its own ZTCF analysis, its
  own DCR regime, distance control vs. direction control, and the two-link vs. one-link
  decision) or demote it to a final section of Ch. 31.
- Chapters 1–11 are pitched at an undergraduate reader; chapters 18–31 are pitched at a
  researcher. This is jarring to read in a single sitting. Consider splitting the book into
  Part I: *Foundations* (Chs 1–14) and Part II: *Advanced Biomechanics and Control* (Chs
  15–32) with an explicit difficulty break.
- The existing `laymansbox`, `driftcontrol`, `mythreality`, `constraintbox`, `exercises`,
  `principle`, `definition`, `example`, `intuitionbox` environments are too many. A reader
  has to learn nine box types; most textbooks get by with three (theorem/definition, example,
  remark). Consolidate.
- The epigraph for Ch. 3 ("The goal of physics is not to describe how nature is but to
  figure out how to simplify what nature does.") is unattributed. If you cannot attribute
  it, remove it. This applies to several chapter epigraphs.
- Glossary is 868 lines, longer than the shortest chapter. Worth auditing for duplication
  with the Vol 0 glossary.

### 6.6 Suggested expansions (PhD-level)

- **Ch. 11 flexible shaft.** Add the full derivation of the Euler–Bernoulli / Timoshenko
  beam with clamped boundary conditions at the hand and free boundary at the tip, plus the
  first three mode shapes with explicit eigenvalues. Cite Rao (2019) *Mechanical Vibrations*
  or Meirovitch (2001) *Fundamentals of Vibrations*.
- **Ch. 18 inverse dynamics parallel.** This is a 903-line chapter with no citations. At
  minimum cite Featherstone (2008), Khatib (1987) operational space, and the parallel
  mechanism literature (Tsai 1999; Merlet 2006).
- **Ch. 28 impact/collision.** The hybrid-dynamics treatment is necessary for a complete
  model of the swing. Cite Brogliato (2016) *Nonsmooth Mechanics* and Stronge (2004) *Impact
  Mechanics*; add a sub-section on the coefficient of restitution and the USGA "spring
  effect" limit on driver COR.
- **Ch. 31 swing plane & launch.** Add the D-plane construction (Jorgensen 1999) explicitly,
  since the book already cites Trackman.
- **Ch. 32 putting.** Must be expanded. The putting stroke is a radically different control
  regime — nearly pure drift, sub-DCR, velocity-sensitive contact dynamics — and it is the
  natural capstone of the drift/control framework. One paragraph is not enough.

---

## 7. Cross-Cutting Issues

### 7.1 The "profound / remarkable / revolutionary" register

Count across the four sources: **~28 occurrences of profound, remarkable, revolutionary,
astonish, breathtaking**. Over an entire four-book corpus this is not catastrophic, but it is
distributed unevenly — some chapters use the register three or four times. A rule of thumb:
if the word could be removed without changing the claim, remove it. The reader will decide
what is remarkable.

### 7.2 Self-promotion and pre-announcement of conclusions

Several passages tell the reader in advance how impressed they should be by the upcoming
result. Examples:

- Ch. 1 Physics of Golf: "Everything in this book flows from …"
- Ch. 1: "Elite golfers, we'll find, have high DCR in the critical phases." This is
  presented as an empirical discovery of the book. In fact, *Physics of Golf* never presents
  the data that would establish this — the AffineDrift project is still in Phase I
  (theoretical), per the *Drifter Manifesto*. Either present the claim as a prediction of the
  framework ("the framework predicts …") or cite the simulation that supports it.
- Ch. 5 *Physics of Golf*: "This decomposition is the key to understanding the golf swing."
  Hyperbolic; soften.
- Ch. 26: "This is the chapter that asks: how?" The reader already knows they are in the
  chapter.

### 7.3 Units

The *Physics of Golf* should be converted to SI throughout. The only exception is where the
literature being cited (e.g. Trackman) uses mph and yards — in those cases present both, as
is done in Ch. 6.

### 7.4 Cross-references between books

The three books reference each other implicitly (the *Drifter Manifesto* assumes the
multibody background of *Geometry of Motion*; *Physics of Golf* reuses the ZTCF/ZVCF
definitions from the *Drifter Manifesto*) but the cross-references are not explicit. A
reader who picks up *Physics of Golf* Ch. 5 is not told that the same material is
rigorously derived in the *Drifter Manifesto* Part 2, or that the geometric setting is in
*Geometry of Motion* Vol I Ch. 7. Add a "See also" footnote at the top of each chapter that
relies on the other two books.

### 7.5 Terminology consistency

- *Drift* in the *Drifter Manifesto* is $f(x)$, a vector field; in the *Physics of Golf* it
  sometimes means the *scalar* drift force; in the *Geometry of Motion* Vol I Ch. 7 it means
  the integral curve of $f$. All three usages are standard in the literature, but a reader
  moving between books will be briefly confused. Pick one primary usage and footnote the
  others.
- *DCR* is sometimes "Drift-Control Ratio" and sometimes "Drift-to-Control Ratio". Pick one.
- *Counterfactual* is sometimes used in the causal-inference sense (what would have
  happened under a different input) and sometimes as a synonym for "thought experiment".
  Restrict the word to the first meaning; use "hypothetical" for the second.

### 7.6 Summary of magnitude of the work

- New citations to add across the three books: **~150–200**.
- Chapters currently with zero or near-zero citations that need to be brought to the target
  floor: **~15** (manifesto counts as one; Physics of Golf 5, 6, 8, 9, 10, 11, 18, 22; *
  Geometry of Motion Vol I* 6 and 7).
- Instances of `profound` / `remarkable` / `revolutionary` to remove or replace: **~28**.
- Magic numbers to either cite or retract: **~30**.
- Editorial standardization (units, box types, epigraphs, glossary merge): **~2 days' work**.

This is a serious pass but not a rewrite. The bones of the manuscripts are in the right
places; the fixes are mostly surgical.

---

## 8. Prioritized Action List

In order of highest expected value per unit of author time:

1. **Add `bibliography: ../references/affine-drift.bib` to the *Drifter Manifesto*
   frontmatter and insert 15–20 `[@key]` calls at the obvious anchor points.** Highest ROI
   single action in the entire review. Without this the manifesto fails a basic sniff test.
2. **Bring *Physics of Golf* Chs. 5 and 6 up to 4–6 citations each.** Chapter 5 is the
   chapter that introduces the affine decomposition, and it currently cites nothing.
3. **Audit the Ch. 6 duality proof sketch in *Geometry of Motion* Vol I and replace with a
   clean Lyapunov-based robustness argument.** Technical correctness.
4. **Remove or replace the 28 `profound / remarkable / revolutionary / astonish` instances.**
5. **Normalize *Physics of Golf* to SI units throughout.**
6. **Retract or cite every magic number identified in §6.3.**
7. **Expand Ch. 32 putting from 58 lines to a full chapter.**
8. **Split long chapters (*Geometry of Motion* Vol I Ch. 8 applications;
   *Physics of Golf* Ch. 23 URDF).**
9. **Reduce the number of callout-box environments from nine to three.**
10. **Add explicit cross-references between the three books.**

---

*End of review.*
