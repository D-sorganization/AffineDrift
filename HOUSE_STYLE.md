# House Style Spec v0.1

This document is the authoritative guide for layout, formatting, and typographic consistency across `www.affinedrift.com`.

## 1. Typography & Layout

### Headings

- **H1**: Page Title only.
- **H2**: Major sections. Sentence case (e.g., "System definition and modeling assumptions").
- **H3**: Subsections. Sentence case.
- **Avoid H4+**: Use bold text or lists if further nesting is needed.
- **No Orphans**: Headings should never be the last element of a section.

### Paragraphs

- **Rhythm**: Avoid walls of text. Break paragraphs that exceed 5-6 sentences unless describing a dense mathematical derivation.
- **Flow**: Use "bridge" sentences sparingly to connect distinct ideas.
- **Whitespace**: Ensure adequate spacing between sections.

### Lists

- Use standard Markdown lists (`-` or `1.`).
- Consistent punctuation: If list items are sentences, end with periods. If fragments, do not.

## 2. Math & Equations

- **Syntax**: Use standard LaTeX.
- **Display Math**: Use `$$ ... $$` for block equations.
- **Inline Math**: Use `$ ... $`.
- **Punctuation**: Place punctuation _inside_ the display math block if the equation ends a sentence.
  - Example: `$$ x = y + z. $$`
- **Numbering**: Only number equations that are referenced elsewhere. Use `$$ ... $$ {#eq-name}`.
- **Notation**:
  - Vectors: Lowercase bold or italic as per context (be consistent within article). Preferred: $x, q, u$.
  - Matrices: Uppercase (e.g., $M, C$).
  - Sets: Blackboard bold (e.g., $\mathbb{R}^n$).
  - Acronyms in math: Use `\mathrm{}` (e.g., $T_{\mathrm{drift}}$).

## 3. Callouts

Use Quarto callouts for special blocks.

- **Note**: `:::{.callout-note}` for general asides.
- **Tip**: `:::{.callout-tip}` for helpful hints.
- **Warning**: `:::{.callout-warning}` for critical caveats or safety warnings.
- **Important**: `:::{.callout-important}` for key takeaways.
- **Theorem/Definition**: Use `:::{.callout-note appearance="simple" icon=false}` with a bold title like **Definition (ZTCF).**

## 4. Figures & Embeds

- **Figures**: Use standard Markdown image syntax with captions.
  - `![Caption text](path/to/image.png){#fig-id}`
- **YouTube**: Use a consistent preview block format.
  - Image preview with a play button overlay or a clear text link if strict embedding is not used.
  - _Standard_: `{{< video https://www.youtube.com/embed/... >}}` if Quarto supports it, or consistent HTML/Markdown fallback.

## 5. Terminology & Abbreviations

- **Drift--Input**: Use an en-dash (`--`) when used as a compound modifier.
- **ZTCF**: Zero Torque Counterfactual.
- **ZVCF**: Zero Velocity Counterfactual.
- **Golfer--Club--Shaft**: Use en-dashes for multi-part system names.
- **Voice**: Objective, theoretical, precise. Avoid conversational filler.

## 6. House Rules

- **Rule #1**: Sentence case for H2/H3.
- **Rule #2**: Max paragraph length ~6 sentences.
- **Rule #3**: Punctuation inside display math.
- **Rule #4**: Consistent en-dashes for compound modifiers.
- **Rule #5**: Explicit callout types.
