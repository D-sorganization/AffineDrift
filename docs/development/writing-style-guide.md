# AffineDrift Writing Style Guide

The canonical standard for prose in every rendered `.qmd` on affinedrift.com:
articles, textbook chapters, book landings, model and repository pages,
resources, and site pages.

AffineDrift publishes claims about a physical system that readers are invited to
challenge. Prose that is vague, padded, or overstated does not merely read badly
here — it hides the boundary between what a model computed, what an experiment
measured, and what an author supposes. Every rule below exists to keep that
boundary visible.

The guide follows established technical and scientific communication practice
(Gopen and Swan's reader-expectation approach, the *Chicago Manual of Style* for
mechanics, and the IMRaD conventions of the biomechanics literature this site
engages with), adapted to a Quarto site whose pages mix narrative, mathematics,
and executable evidence.

---

## 1. Sentence-Level Standards

### 1.1 Length and rhythm

| Metric | Target | Hard ceiling |
| --- | --- | --- |
| Mean sentence length | 20–24 words | 26 words |
| Sentences over 30 words | under 15% | 20% |
| Sentences over 45 words | 0 | — |

A 45-word sentence in technical prose almost always carries two or three
independent claims that a reader must hold simultaneously while also parsing
notation. Split it. Vary length deliberately: a short sentence after a long one
lands the point.

### 1.2 Put the actor in the subject slot

Prefer the agent — a force, a model, a measurement, a researcher — as the
grammatical subject, and a real verb as the action.

- Weak: *An examination of the interaction force was performed by means of the
  ledger, and a determination was made that transfer had occurred.*
- Strong: *The ledger shows that the interaction force transferred energy.*

Passive voice is correct when the actor is unknown, irrelevant, or genuinely
less important than the object — *the shaft was modeled as an
Euler–Bernoulli beam* is fine. Keep passive constructions under roughly 18% of
sentences; above that, the prose stops naming who or what is doing the work.

### 1.3 Unpack nominalizations

Verbs buried inside nouns lengthen sentences and drain them of motion.

| Nominalized | Direct |
| --- | --- |
| performs a calculation of | calculates |
| provides an explanation for | explains |
| makes the assumption that | assumes |
| gives an indication that | indicates |
| leads to a reduction in | reduces |

### 1.4 Cut filler

Delete on sight: *very*, *really*, *quite*, *basically*, *essentially*,
*actually*, *simply*, *obviously*, *clearly*, *of course*, *needless to say*,
*it is important to note that*, *it should be noted that*.

Replace: *in order to* → *to*; *due to the fact that* → *because*; *the fact
that* → recast the sentence; *in terms of* → name the relation; *a number of* →
give the number or say *several*.

*Clearly* and *obviously* are worse than padding. If a step is obvious the
reader does not need to be told; if it is not, the word blames the reader.

### 1.5 Hedge once, precisely

One hedge per claim. *The results may possibly suggest that transfer could
perhaps occur* commits to nothing. Choose the hedge that names the actual
uncertainty:

- **Model-bounded**: *under the declared assumptions, the model predicts…*
- **Sample-bounded**: *in the eight measured golfers…*
- **Mechanism-uncertain**: *one explanation consistent with this is…*

---

## 2. Paragraph and Section Structure

### 2.1 Topic sentence first

Open every paragraph with the claim it defends. A reader scanning only first
sentences should get the argument. Never open with throat-clearing
(*It is also worth considering that…*).

### 2.2 Old information before new

Begin a sentence with material the previous sentence established, and end it
with what is new. The stress position — the end of the sentence — is where
emphasis lands, so put the point you want remembered there, not in a trailing
qualifier.

- Choppy: *Power is the dot product of force and velocity. The ledger sums
  boundary powers. Coordinates affect decomposition.*
- Linked: *Power is the dot product of force and velocity. Summing those
  products across a boundary gives the ledger. What the ledger cannot fix is
  that the decomposition itself depends on the chosen coordinates.*

### 2.3 One paragraph, one idea

Three to seven sentences. A paragraph that runs past ten sentences is usually
two paragraphs with a missing break, or an unstructured list that should be
a real list.

### 2.4 Signposting

Transitions must state a logical relation, not merely mark a boundary.
*Additionally* and *Furthermore* rarely earn their place; *Because of that
cancellation*, *The same argument fails when*, and *This leaves one route open*
tell the reader what changed.

Sections open with what the section establishes and close by handing off to the
next. Do not restate the heading as the first sentence.

---

## 3. Precision and Claim Discipline

### 3.1 Label the evidence class

AffineDrift distinguishes four classes; use the site's existing bold labels
where a page already uses them, and keep the distinction in wording everywhere
else.

- **Model Result** — an executable system produced this under stated assumptions.
- **Human Evidence** — people were measured; give n and the measurement.
- **Hypothesis** — a proposed explanation awaiting a decisive test.
- **Practical Interpretation** — plain-language reading, not instruction.

### 3.2 Never let a model become a fact

- Wrong: *The kinetic chain transfers energy distally.*
- Right: *In the double-pendulum model, interaction power at the wrist is
  positive through the late downswing.*

Reserve *proves*, *demonstrates*, *guarantees*, and *always* for statements that
are mathematically established. A simulation *predicts*; a measurement *shows*
within its uncertainty.

### 3.3 Quantities carry units and provenance

Every number states its units and where it came from — measured, cited,
assumed, or illustrative. Numbers presented without provenance read as
measurements even when they are not, and CI blocks newly added quantitative
claims that carry neither a citation nor a caveat word.

### 3.4 Name the boundary

Energy, power, and work statements are meaningless without a system boundary and
reference frame. Say which one before reporting the quantity.

---

## 4. Mechanics and House Conventions

### 4.1 Spelling: US English

The corpus is overwhelmingly US-spelled; that is the standard.
*center*, *meter*, *behavior*, *modeling*, *labeled*, *normalized*,
*optimization*, *characterized*, *analyzed*, *organize*, *color*.

Exception: never alter spelling inside a quotation, a proper noun, a
bibliography entry, a cited work's title, a URL, a file path, or a code
identifier.

### 4.2 Terminology is fixed

`NOTATION.md` is the single source of truth for acronyms and symbols, and
`scripts/check_terminology.py` enforces the acronym slice of it across
`articles/`, `pages/`, and `resources/`:

| Acronym | The only permitted expansion |
| --- | --- |
| ZTCF | Zero Torque Counterfactual |
| DCR | Drift-Control Ratio (the controllability quantity) |
| DgCR | the aerodynamic drag-curve ratio — never written `DCR` |

Banned outright: *Zero-Torque Control Fraction*, *Zero-Torque Controlled
Flight*, *Zero-Torque-Contribution-to-Force*, *Drift-Correction Response*,
*Disturbance Rejection vs. Control*, and the placeholder markers `\citeneeded`
and `[citation needed`.

Introduce an acronym once, at first use, then use it consistently. Do not invent
synonyms for a defined term — a reader who meets *interaction force*, *coupling
force*, and *joint reaction* on one page cannot tell whether three things or one
thing is meant.

### 4.3 Headings

APA title case, enforced by `scripts/check_title_case.py` across headings, YAML
`title`/`subtitle`/`fig-cap`/`fig-subcap`, `_quarto.yml` nav labels, figure
captions, and chart titles. Capitalize every word except these minor words, and
capitalize even those when they are first, last, or follow a colon, question
mark, dash, or opening bracket:

> a, an, and, as, at, but, by, for, in, nor, of, on, or, per, so, the, to, via,
> vs, yet

Unit abbreviations (`cm`, `kg`, `km`, `m`, `mm`, `mph`, `ms`, `nm`, `rad`, `s`)
and name particles (`da`, `de`, `der`, `di`, `la`, `le`, `van`, `von`) stay
lowercase. Prose sentences are deliberately out of scope — the check never looks
at body text.

Headings are noun phrases or questions, not sentences, and never end in a
period. Do not skip levels. One `#`-level title per page, and an `articles/`
page must not carry both a YAML `title:` and a body `# H1` with the same text.

### 4.4 Voice and person

Second person (*you*) for instructions to the reader. First person plural
(*we*) for shared reasoning with the reader — *we draw the boundary around the
club alone* — used sparingly. Present tense for what a model or equation does;
past tense for what was measured or run.

### 4.5 Punctuation

- Em dash — unspaced or spaced consistently within a page; do not mix with
  hyphens for the same purpose.
- Serial comma always.
- Quotation marks: straight or curly consistently within a file; LaTeX-bound
  sources follow `scripts/check_latex_quotes.py`.
- Semicolons join two independent clauses that belong together. If either side
  cannot stand alone, use a comma or a period.

### 4.6 Lists

Parallel grammar across items. Introduce with a full sentence and a colon.
Do not use a list where two sentences of connected prose would show the
relationship between the items better.

### 4.7 Figures, equations, and cross-references

- Every figure needs a caption and `fig-alt` text that states what the figure
  shows, not that it is a figure.
- Reference figures, sections, and equations by their Quarto cross-reference
  (`@fig-`, `@sec-`, `@eq-`), never as *the figure above*.
- Display equations are grammatical parts of the sentence that introduces them
  and carry the punctuation that sentence requires.
- Define every symbol at first use, in words.

---

## 5. Hard Constraints for Editors

Prose edits must not break these. All are enforced in CI.

1. **Do not change any equation, symbol, numeral, or unit** unless the change is
   the explicit purpose of the edit.
2. **Preserve every citation key** exactly: `[@putnam1993]`, `\cite{...}`.
3. **Preserve every cross-reference and anchor**: `{#sec-...}`, `{#fig-...}`,
   `@sec-`, `@fig-`, `@eq-`. Renaming an anchor breaks
   `scripts/check_quarto_xrefs.py`.
4. **Preserve math delimiters** `$…$` and `$$…$$` and everything between them
   (`scripts/check_display_math.py`, `scripts/scan_quarto_syntax.py`).
5. **Do not edit YAML front matter** except to fix a genuine title-case or
   typographic error (`scripts/validate_frontmatter.py`).
6. **Keep headings in title case** and keep one page title
   (`scripts/check_title_case.py`, `scripts/check_single_title.py`).
7. **Do not rename or reorder** `{{< include … >}}` shortcodes, div fences
   (`::: {…}`), or code cells.
8. **Do not add new quantitative claims.** Rewriting a sentence makes it a new
   line to `scripts/check_textbook_claims.py`; a rewritten sentence carrying a
   number must keep whatever citation or caveat wording already licensed it.
9. **Do not weaken an existing hedge.** Removing *may*, *under the model*, or
   *illustrative* converts a hypothesis into a claim.
10. **Use straight quotes, not LaTeX paired quotes.** ` ``…'' ` fails
    `scripts/check_latex_quotes.py`; write `"…"` and let Quarto curl it.
11. **Only math environments survive Pandoc.** In `articles/**`, `\begin{…}` is
    limited to the math allow-list in `scripts/check_latex_environments.py`
    (`align`, `aligned`, `array`, `bmatrix`, `cases`, `displaymath`, `eqnarray`,
    `equation`, `gather`, `gathered`, `matrix`, `multline`, `pmatrix`,
    `smallmatrix`, `split`, `subarray`, `vmatrix`, `Bmatrix`, `Vmatrix`).
    Anything else is silently dropped from the page.
12. **Never run a generic Markdown formatter over a `.qmd`.** Prettier and
    similar tools read `$$…$$` as emphasis and have previously corrupted
    `_{subscript}` into `*{subscript}`. Edit by hand.
13. **Some exact strings are pinned by `content_lint` tests** and must survive
    verbatim (see `tests/test_public_site_content_hygiene.py`,
    `tests/test_physics_of_golf_glossary.py`,
    `tests/test_geometry_of_motion_convention_regression.py`). Grep `tests/`
    for `content_lint` before editing a file that has one.
14. **Never edit rendered output in `docs/`.**

---

## 6. Revision Checklist

Before opening a PR that touches prose:

- [ ] No sentence exceeds 45 words; few exceed 30.
- [ ] Every paragraph opens with its claim.
- [ ] Filler and double hedges removed.
- [ ] Every number has units and provenance.
- [ ] Model results are not written as facts about golfers.
- [ ] US spelling throughout, outside quotations and proper nouns.
- [ ] Terminology matches `NOTATION.md`; acronyms expanded once.
- [ ] All citations, cross-references, math, and anchors unchanged.
- [ ] `python3 scripts/scan_quarto_syntax.py`
- [ ] `python3 scripts/check_quarto_xrefs.py`
- [ ] `python3 scripts/check_title_case.py`
- [ ] `python3 scripts/check_display_math.py`
- [ ] `python3 scripts/check_terminology.py --baseline config/terminology-baseline.json`
