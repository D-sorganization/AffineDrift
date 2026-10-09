# Editorial Style Guide

This guide establishes the editorial voice, structural conventions, readability standards, and pedagogical rules for all reader-facing publications across AffineDrift. It complements the sentence-level standards in `docs/development/writing-style-guide.md` and enforces the policies mandated by **[WEB-12.1] (#4587)**.

---

## 1. Voice and Tone

AffineDrift writes for researchers, engineers, and analytical coaches who value intellectual honesty and mechanical precision over marketing persuasion.

### Confident About Mathematics

When stating mathematical identities, proved theorems, or established equations of motion, write with authority and clarity:

- **State theorems directly**: Do not hedge proven relationships with phrases like *"it appears that"* or *"one might say"*. If an affine decomposition $\dot{x} = f(x) + G(x)u$ partitions state derivative space into drift and control input vectors, state that partition as a mathematical fact.
- **Separate derivation from interpretation**: Clearly separate what the mathematical model yields from what physical inference can be drawn from it.

### Scope and Mathematical Confidence

Prose must be uncompromisingly explicit about model scope and underlying assumptions:

- **State assumptions upfront**: Explicitly declare planar versus three-dimensional approximations, rigid-body assumptions, lumped-parameter constraints, and boundary conditions before presenting conclusions.
- **Bound every claim**: Never claim a 2D result generalizes to 3D without dedicated comparative evidence. Never claim a single-subject kinematic trace proves universal human swing mechanics.

---

## 2. Where Caveats Go

A major failure mode in scientific writing is burying the reader under a cascade of apologetic caveats embedded in every paragraph. In AffineDrift, caveats are strictly quarantined into standardized structural components.

### The Standardized Caveat Block (WEB-03.4)

Every long-form article, textbook chapter, and technical monograph must include the standardized **"What This Shows / What It Does Not Show"** block immediately following the introduction or key findings:

```markdown
::: {.callout-note appearance="simple"}
### What This Shows / What It Does Not Show

**What This Shows:**
- The mathematical partition of instantaneous acceleration into passive drift $f(x)$ and active muscular control $G(x)u$.
- The exact sensitivity of clubhead speed to wrist uncocking torque under declared parameter assumptions.

**What It Does Not Show:**
- Individual muscle activation histories or motor unit recruitment patterns.
- An optimal swing technique applicable to all physical body types.
:::
```

### Clean Body Prose

With caveats properly quarantined in the designated block:
- Keep body prose focused on the primary mechanism.
- Avoid repetitive disclaimers in subsequent sections.
- When an assumption is violated in a specific section, state the violation plainly as a model boundary.

---

## 3. Glossary Linking

Technical terms must be linked to the site-wide glossary using the Quarto shortcode / Lua filter (`{{< term key >}}`) introduced in **[WEB-01.5] (#4490)**.

### Linking Rules

1. **First occurrence only**: Link a term on its first substantial occurrence within an article section. Do not link every repeated mention.
2. **Standard shortcode**: Use `{{< term key >}}` when the displayed text matches the glossary term name (e.g., `{{< term drift >}}`).
3. **Custom label syntax**: Use `{{< term key "custom label" >}}` when inflecting grammar, pluralizing, or using descriptive phrasing (e.g., `{{< term control "active control torque" >}}`).
4. **Accessible hover tooltip**: The filter automatically injects WAI-ARIA accessible tooltip markup (`role="tooltip"`, `aria-describedby`) linking to `/pages/glossary.html#key`.

---

## 4. Readability Targets

AffineDrift serves diverse audiences through a layered architecture. Readability is managed per layer rather than uniformly across the entire text.

| Content Layer | Target Readability (Flesch-Kincaid) | Vocabulary Level | Purpose |
| --- | --- | --- | --- |
| **Lay Summary Block** (`.laymans-terms`) | **$\le$ Grade 10** | Everyday English | Immediate conceptual grasp for general readers and analytical golfers |
| **Executive / Abstract Block** (`.abstract-section`) | Grade 11–14 | Technical English | Concise summary for researchers and engineers |
| **Body Exposition** | **Unconstrained** | Specialized Domain Vocabulary | Uncompromising mathematical and biomechanical rigor |
| **Appendix / Proofs** | **Unconstrained** | Formal Mathematical Notation | Complete formal derivations and proofs |

### Lay Block Editing Guidelines

To maintain $\le$ Grade 10 in `.laymans-terms`:
- Replace multi-syllable jargon with direct physical verbs (e.g., *"pushes"* instead of *"imparts a normal compressive force"*).
- Limit sentence length to 15–18 words in this block.
- Keep concepts grounded in physical sensations or observable visual movement.

---

## 5. Analogy and Metaphor Rules

Analogies are powerful pedagogical bridges, but flawed analogies create persistent mechanical misconceptions in sports biomechanics (e.g., treating the human kinetic chain as a simple whip or cracking towel).

### The Golden Rule: Say Where the Analogy Breaks

Whenever an analogy or metaphor is introduced to explain a complex concept, the author **must explicitly state where the analogy breaks down**:

```markdown
<!-- Compliant analogy usage -->
The golfer's arms and club behave superficially like a double pendulum,
transferring angular velocity outward as the proximal link decelerates.

However, this analogy breaks down in three crucial respects:
1. The human wrist joint is not a passive frictionless pin; it possesses
   active multi-axis musculotendinous impedance and neuromuscular stiffness.
2. The torso does not provide a fixed pivot; its base of support moves
   dynamically through ground reaction forces.
3. The motion is non-planar; 3D out-of-plane coupling alters effective inertia.
```

Never introduce a metaphor without immediately defining its physical and mathematical boundaries.

---

## 6. Banned Internal Vocabulary

Reader-facing articles (`articles/**/*.qmd`, `pages/*.qmd`, `books/**/*.qmd`) must communicate timeless scientific concepts. Internal fleet governance, project management labels, and engineering audit mechanics must never leak into reader prose.

### Prohibited Terms in Reader Prose (WEB-12.2)

The following terms belong strictly in internal developer documentation (`docs/development/`, `SPEC.md`, pull requests) and are **strictly banned in reader-facing prose**:

| Banned Internal Term | Permitted Reader-Facing Alternative |
| --- | --- |
| `readiness-program` | *editorial review*, *publication standard*, or omit |
| `claim-audit` | *evidence review*, *verification ledger*, *claim assessment* |
| `ztcf-gate` | *zero-torque counterfactual analysis*, *passive drift baseline* |
| `phantom-merge` | *divergent branch history* (internal developer context only) |
| `weak-assertion` | *statistical sensitivity*, *uncertainty bound* |
| `tier:strong` / `tier:cli` | *peer-reviewed tier*, *editorial level*, or omit |

---

## 7. Capitalization and Headings

Headings establish document hierarchy and are subject to automated repository title-case verification.

### Heading Capitalization

- **H1 (Document Title)**: Title Case (e.g., `# Induced Acceleration in the Golf Swing`).
- **H2 (Major Section)**: Title Case (e.g., `## Force and Mobility Ellipsoids`).
- **H3 (Subsection)**: Title Case (e.g., `### Derivation of the Kinetic Energy Metric`).
- **H4 and below**: Sentence case or Title Case, applied consistently within the document.

### Technical Naming Conventions

- Acronyms: Define on first use (e.g., *Iterative Linear Quadratic Regulator (iLQR)*, *Drift-Control Ratio (DCR)*).
- Mathematical entities: Italicize scalar variables ($q, u, t$); bold vectors and matrices ($\mathbf{M}(q), \mathbf{x}$).

---

## 8. Mathematical Notation and Figure Consistency

Mathematical typesetting must maintain consistent conventions across all articles:

- **Equation Numbers**: Use Quarto cross-reference syntax `{#eq-label}` for equations that are referenced in text. Unreferenced display math should omit equation numbers.
- **Vectors and Tensors**: Use bold Roman for vectors ($\mathbf{v}$) and bold capital letters for matrices ($\mathbf{M}$). Avoid ambiguous scalar notation for spatial quantities.
- **Coordinate Frames**: Explicitly state the reference frame for all angular velocities and accelerations (e.g., ground-fixed frame versus body-attached frame).

---

## 9. Author Pre-Submission Editorial Checklist

Before opening a pull request for a new or revised article, verify compliance with this checklist:

1. [ ] **Mathematical Confidence**: Theorems and dynamical derivations are stated directly without unnecessary hedging.
2. [ ] **Scope Boundaries**: Underlying assumptions (planar vs. 3D, rigid-body vs. flexible) are explicitly declared upfront.
3. [ ] **Caveat Block (WEB-03.4)**: Standardized "What This Shows / What It Does Not Show" callout block is present immediately following the introduction.
4. [ ] **Glossary Tooltips (WEB-01.5)**: Key domain concepts use `{{< term key >}}` on their first occurrence.
5. [ ] **Readability**: The `.laymans-terms` summary block passes Flesch-Kincaid $\le$ Grade 10.
6. [ ] **Analogy Transparency**: Every metaphor or mechanical analogy states explicitly where the physical analogy breaks down.
7. [ ] **Vocabulary Hygiene (WEB-12.2)**: No internal fleet workflow terms (e.g., `readiness-program`, `claim-audit`, `ztcf-gate`, `tier:strong`) appear in reader-facing prose.
8. [ ] **Headings**: Document headings strictly follow Title Case capitalization rules.
