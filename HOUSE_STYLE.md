# AffineDrift House Style Spec v0.1

This document defines the layout and formatting rules for www.affinedrift.com. It is enforced to ensure a consistent, professional, and readable scientific voice.

## 1. Typography & Text

*   **Headings**: Use Sentence case for all headings (H1--H3).
    *   H1: Page Title only.
    *   H2: Major sections.
    *   H3: Subsections.
    *   H4: Avoid unless strictly necessary for complex nested structures.
*   **Paragraphs**: Avoid walls of text. Maximum paragraph length is ~5-6 sentences. Split longer thoughts.
*   **Lists**: Use standard Markdown lists (`-` or `1.`). Ensure one blank line before and after lists.
*   **Emphasis**: Use *italics* for emphasis and new terms. Use **bold** sparingly for strong emphasis or key terms in definitions.

## 2. Terminology & Abbreviations

*   **Drift--Input**: Use an en-dash (`--`) when referring to the decomposition or relationship.
*   **ZTCF**: Zero Torque Counterfactual. Capitalize as a proper noun phrase when written out: "Zero Torque Counterfactual".
*   **ZVCF**: Zero Velocity Counterfactual. Capitalize as a proper noun phrase when written out: "Zero Velocity Counterfactual".
*   **Control-affine**: Hyphenated.
*   **Inverse Dynamics (ID)**: Abbreviated as $\mathrm{ID}$ in math mode.

## 3. Math & Equations

*   **Format**: Use standard LaTeX syntax.
*   **Display Math**: Use `$$ ... $$` for centered equations.
    *   **Punctuation**: Punctuation belonging to the sentence must be placed **inside** the math block (e.g., `$$ x = y. $$`).
*   **Inline Math**: Use `$ ... $`. Punctuation goes outside.
*   **Variables**: Standard italics for scalars. Bold or vector notation as per specific paper conventions (consistent within page).
*   **Text in Math**:
    *   Full words: `\text{word}` (e.g., `\text{drift}`, `\text{input}`).
    *   Operators/Acronyms: `\mathrm{OP}` (e.g., `\mathrm{ID}`, `\mathrm{ZTCF}`).
*   **Spacing**: Use `\,` to separate differentials or distinct terms if needed for clarity.

## 4. Callouts & Highlights

Use Quarto callouts for structured content:

*   **Definitions**: `::: {.callout-note}` or `::: {.callout-tip}`.
*   **Key Properties**: `::: {.callout-note title="Key Properties"}`.
*   **Warnings/Limitations**: `::: {.callout-warning}` or `::: {.callout-important}`.
*   **Theorems**: `::: {.callout-note title="Theorem"}`.

## 5. Figures & Captions

*   **Format**: `![Caption text.](path/to/image.png){#fig-label}`
*   **Captions**: Sentence case. End with a period.
*   **Referencing**: Use `@fig-label` in text.

## 6. Embeds (YouTube)

*   Use the standard Quarto shortcode or a consistent HTML block if needed.
*   `{{< video https://www.youtube.com/embed/... >}}` is preferred.
